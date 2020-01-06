#! usr/bin/python3
# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, Response, g
from app.User.model import User
import json
from utils.json_helper import DateEncoder
from .model import Cwebapi
from .model import Datasource
import pymysql
import cx_Oracle
from utils import api_util
import demjson
import requests
from utils.dbutils import redis
from instance import config
from utils.token_utils import TokenMaker
import re

webapi = Blueprint("webapi", __name__)

# 处理oracle数据库存储过程接口
@webapi.route("/dealoracle", methods=["get"])
def dealoracle():
    # oracle存储过程函数名
    func = request.args.get('f')
    # 搜索关键字
    sword = request.args.get('z')
    conn = cx_Oracle.connect(config.OR_USER, config.OR_PW, config.OR_HOST)
    # 创建游标
    cursor = conn.cursor()
    # 调用存储过程
    res = []
    try:
        outdata = cursor.var(cx_Oracle.CURSOR)
        aa = cursor.callproc("DP.SP_SENTIMENT_INDEX", [sword, outdata])
        dic = {}
        for i in aa[1]:
            v = re.search("\d+(\.\d+)?", i[2])
            it = float(v.group())
            if it <= 10:
                dic[i[1]] = round(it)
            else:
                a = 1
                while True:
                    b = it / (10 * a)
                    if 0 <= b <= 10:
                        dic[i[1]] = round(b)
                        break
                    else:
                        a = a + 1

        res = [
            {"舆情影响力": dic["舆情影响力"]},
            {"舆情敏感度": dic["舆情敏感度"]},
            {"舆情覆盖范围": dic["舆情覆盖范围"]},
            {"热度趋势": dic["热度趋势"]},
            {"舆情声量": dic["舆情声量"]}
        ]
    except Exception as e:
        raise e
    # 资源关闭
    cursor.close()
    conn.commit()
    conn.close()
    return Response(json.dumps({"code": 1, "data": res}, cls=DateEncoder), mimetype='application/json')



@webapi.route("/", methods=["get"])
def general_query():
    # 请求参数
    args = request.args.to_dict()

    # 接口名
    service_id = args.get('serviceId')
    webapi_msg = Cwebapi.query.filter(Cwebapi.api == service_id).first()

    # 缓存
    cache_time = webapi_msg.cache_time
    cachekey = TokenMaker().generate_token(config.WEBPICACHEKEY,request.url)

    # 从缓存拿数据
    if cache_time:
        cache_data = redis.get(cachekey)
        if cache_data != None:
            return Response(json.dumps({"code": 1, "data": demjson.decode(cache_data)}, cls=DateEncoder),
                            mimetype='application/json')

    # 参数列表
    params_list = webapi_msg.params.split(',') if webapi_msg.params else None
    sqlview = webapi_msg.sql_view

    # 处理参数
    deal_params = webapi_msg.deal_params
    # 替换参数
    if params_list:
        for i in params_list:
            sqlview = sqlview.replace("[%s]" % i, args.get(i))

    if deal_params:
        for i in params_list:
            deal_params = deal_params.replace("[%s]" % i, args.get(i))
        deal_params_dict = demjson.decode(deal_params)
        # k=area_num , v="南海区"
        for k, v in deal_params_dict.items():
            deal_params_met = getattr(api_util, k)
            pre_deal_params_met = deal_params_met(v)
            sqlview = sqlview.replace(v, str(pre_deal_params_met))
    
    # g['args'] = args
    g.args = args
    print('sqlview', sqlview)
    # 数据库连接池
    datasource_id = webapi_msg.datasource_id
    datasource_msg = Datasource.query.filter(Datasource.id == datasource_id, Datasource.flag == 1).first()
    # 数据库连接方式
    con_type = datasource_msg.type
    dsn = datasource_msg.connect
    user = datasource_msg.account
    password = datasource_msg.passwd
    if con_type == 'mysql':
        host, el = dsn.split(':')
        port, database = el.split('/')
        try:
            conn = pymysql.connect(host=host, port=int(port), db=database, user=user, password=password)
        except Exception:
            return jsonify({'code': -1, 'data': "连接失败"})
        else:
            # 定义游标
            cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
            cur.execute(sqlview)
            res = cur.fetchmany(200)

    else:
        try:
            conn = cx_Oracle.connect(user=user, password=password, dsn=dsn, encoding="UTF-8")
        except cx_Oracle.DatabaseError:
            oracle_ip, oracle_exp = dsn.split(':', 1)
            oracle_port, oracle_sid = oracle_exp.split('/', 1)
            dsn = cx_Oracle.makedsn(oracle_ip, int(oracle_port), sid=oracle_sid)
            conn = cx_Oracle.connect(user=user, password=password, dsn=dsn, encoding="UTF-8")
        except Exception as e:
            return jsonify({'code': -1, 'data': "连接失败"})

        from utils.dbutils import makeDictFactory

        # 定义游标
        cur = conn.cursor()
        cur.execute(sqlview)
        cur.rowfactory = makeDictFactory(cur)
        res = cur.fetchmany(200)

    cur.close()
    conn.close()
    # 格式处理
    f, b = service_id.split('@', 1)
    if b:
        deal_data_met = getattr(api_util, b)
        res = deal_data_met(res)
    # 缓存数据
    if cache_time:
        redis.set(cachekey, demjson.encode(res))
        redis.expire(cachekey, cache_time)
    return Response(json.dumps({"code": 1, "data": res}, cls=DateEncoder), mimetype='application/json')

