# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, Response, g
import requests
import uuid
import json
import time
from instance import config
from math import ceil
from utils.json_helper import DateEncoder
from utils.api_util import sxf_token
import copy
import datetime
import urllib3
from utils.dbutils import redis
from utils.token_utils import TokenMaker
import demjson

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from collections import Counter

apis = Blueprint("apis", __name__)


@apis.route("/sxf_get_once/", methods=["get"])
def sxf_get_once():
    # 请求参数
    args = request.args.to_dict()
    method = args.get('method')
    target = args.get('target')
    target = target.split(".") if target else target
    from_time = args.get('fromTime')
    from_time = int(from_time) if from_time else int((datetime.datetime.now() - datetime.timedelta(days=8)).timestamp())
    to_time = args.get('toTime')
    to_time = int(to_time) if to_time else int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())
    max_count = args.get('maxCount')
    url = config.SXF_BASE_URL % (config.SXF_IP, method)
    interval = int(args.get('interval'))
    token = sxf_token()
    count_resp = 0
    ru = request.url.replace('&cache_del=1', '')
    redis_key = TokenMaker().generate_token(ru, request.method)
    cache_del = args.get('cache_del')
    if not cache_del:
        cache_data = redis.get(redis_key)
        if cache_data != None:
            return Response(json.dumps({"code": 1, "data": cache_data}, cls=DateEncoder), mimetype='application/json')
    if interval:
        from_datetime = datetime.datetime.fromtimestamp(from_time)  # 时间戳转日期
        to_datetime = datetime.datetime.fromtimestamp(to_time)  # 时间戳转日期
        iter_time = ceil((to_datetime - from_datetime).days / interval)

        while iter_time:
            iter_target = copy.deepcopy(target)
            from_time = int(from_datetime.timestamp())
            to_mid_time = int((from_datetime + datetime.timedelta(days=interval)).timestamp())
            params = {"token": token, "fromActionTime": from_time,
                      "toActionTime": to_mid_time, "maxCount": max_count}
            resp = requests.get(url, params=params, verify=False).json()
            while iter_target:
                resp = resp.get(iter_target.pop(0))
            count_resp += int(resp)

            from_datetime = from_datetime + datetime.timedelta(days=interval)
            iter_time -= 1
    else:
        params = {"token": token, "fromActionTime": str(from_time), "toActionTime": str(to_time),
                  "maxCount": max_count}
        resp = requests.get(url, params=params, verify=False).json()
        while target:
            resp = resp.get(target.pop(0))
        count_resp = resp
    redis.set(redis_key, count_resp)
    redis.expire(redis_key, 86400)
    return Response(json.dumps({"code": 1, "data": count_resp}, cls=DateEncoder), mimetype='application/json')


@apis.route("/sxf_get_everytime/", methods=["get"])
def sxf_get_everytime():
    # 请求参数
    args = request.args.to_dict()

    method = args.get('method')
    target = args.get('target')
    target = target.split(".") if target else target
    backcount = int(args.get('backcount'))
    today = datetime.datetime.now()
    max_count = args.get('maxCount')
    url = config.SXF_BASE_URL % (config.SXF_IP, method)
    ru = request.url.replace('&cache_del=1', '')
    redis_key = TokenMaker().generate_token(ru, request.method)
    cache_del = args.get('cache_del')
    if not cache_del:
        cache_data = redis.get(redis_key)
        if cache_data != None:
            return Response(json.dumps({"code": 1, "data": demjson.decode(cache_data)}, cls=DateEncoder),
                            mimetype='application/json')

    token = sxf_token()
    resp_time_list = []
    count_resp_list = []
    while backcount:
        target_deal = copy.deepcopy(target)
        from_time_pre = today - datetime.timedelta(days=backcount)
        from_time = int(from_time_pre.timestamp())
        to_time = int((today - datetime.timedelta(days=backcount - 1)).timestamp())
        backcount -= 1
        params = {"token": token, "fromActionTime": str(from_time), "toActionTime": str(to_time),
                  "maxCount": max_count}

        resp = requests.get(url, params=params, verify=False).json()
        while target_deal:
            resp = resp.get(target_deal.pop(0))

        resp_time_list.append(from_time_pre.date())
        count_resp_list.append(resp)
    redis.set(redis_key, demjson.encode([resp_time_list, count_resp_list], strict=False))
    redis.expire(redis_key, 86400)
    return Response(json.dumps({"code": 1, "data": [resp_time_list, count_resp_list]}, cls=DateEncoder),
                    mimetype='application/json')


@apis.route("/sxf_get_additional/", methods=["get"])
def sxf_get_additional():
    args = request.args.to_dict()
    method = args.get('method')
    target = args.get('target')
    target = target.split(".") if target else target
    from_time = args.get('fromTime')
    from_time = int(from_time) if from_time else int((datetime.datetime.now() - datetime.timedelta(days=8)).timestamp())
    to_time = args.get('toTime')
    to_time = int(to_time) if to_time else int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())
    max_count = args.get('maxCount')
    url = config.SXF_BASE_URL % (config.SXF_IP, method)
    interval = int(args.get('interval'))
    condition = args.get("condition").split("=")
    token = sxf_token()
    count_resp = 0

    ru = request.url.replace('&cache_del=1', '')
    redis_key = TokenMaker().generate_token(ru, request.method)
    cache_del = args.get('cache_del')
    if not cache_del:
        cache_data = redis.get(redis_key)
        if cache_data != None:
            return Response(json.dumps({"code": 1, "data": demjson.decode(cache_data)}, cls=DateEncoder),
                            mimetype='application/json')

    if interval:
        from_datetime = datetime.datetime.fromtimestamp(from_time)  # 时间戳转日期
        to_datetime = datetime.datetime.fromtimestamp(to_time)  # 时间戳转日期
        iter_time = ceil((to_datetime - from_datetime).days / interval)

        while iter_time:
            iter_target = copy.deepcopy(target)
            from_time = int(from_datetime.timestamp())
            to_mid_time = int((from_datetime + datetime.timedelta(days=interval)).timestamp())
            params = {"token": token, "fromActionTime": from_time,
                      "toActionTime": to_mid_time, "maxCount": max_count}
            resp = requests.get(url, params=params, verify=False).json()
            while iter_target:
                resp = resp.get(iter_target.pop(0))
            if len(condition) == 1:
                count_resp = dict(Counter(sorted([r[condition[0]] for r in resp])))
            else:
                count_resp = Counter([r[condition[0]] == int(condition[1]) for r in resp])[1]

            from_datetime = from_datetime + datetime.timedelta(days=interval)
            iter_time -= 1
    else:
        params = {"token": token, "fromActionTime": str(from_time), "toActionTime": str(to_time),
                  "maxCount": max_count}
        resp = requests.get(url, params=params, verify=False).json()
        while target:
            resp = resp.get(target.pop(0))
        print("=" * 20)
        print(resp)
        print("=" * 20)
        if len(condition) == 1:
            count_resp = dict(Counter(sorted([r[condition[0]] for r in resp])))
            print("count_resp", count_resp)
        else:
            count_resp = Counter([r[condition[0]] == int(condition[1]) for r in resp])[1]

    redis.set(redis_key, demjson.encode(count_resp, strict=False))
    redis.expire(redis_key, 86400)

    return Response(json.dumps({"code": 1, "data": count_resp}, cls=DateEncoder), mimetype='application/json')


@apis.route("/sxf_riskeven_detail/", methods=["get"])
def sxf_riskeven_detail():
    args = request.args.to_dict()
    method = args.get('method')
    target = args.get('target')
    target = target.split(".") if target else target
    from_time = args.get('fromTime')
    from_time = int(from_time) if from_time else int((datetime.datetime.now() - datetime.timedelta(days=8)).timestamp())
    to_time = args.get('toTime')
    to_time = int(to_time) if to_time else int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())
    max_count = args.get('maxCount')
    url = config.SXF_BASE_URL % (config.SXF_IP, method)
    interval = int(args.get('interval'))
    token = sxf_token()

    ru = request.url.replace('&cache_del=1', '')
    redis_key = TokenMaker().generate_token(ru, request.method)
    cache_del = args.get('cache_del')
    if not cache_del:
        cache_data = redis.get(redis_key)
        if cache_data != None:
            return Response(json.dumps({"code": 1, "data": demjson.decode(cache_data)}, cls=DateEncoder),
                            mimetype='application/json')

    resp_data = []
    duplicate_moval = []
    calculation_list = []
    if interval:
        from_datetime = datetime.datetime.fromtimestamp(from_time)  # 时间戳转日期
        to_datetime = datetime.datetime.fromtimestamp(to_time)  # 时间戳转日期
        iter_time = ceil((to_datetime - from_datetime).days / interval)
        while iter_time:
            iter_target = copy.deepcopy(target)
            from_time = int(from_datetime.timestamp())
            to_mid_time = int((from_datetime + datetime.timedelta(days=interval)).timestamp())

            params = {"token": token, "fromActionTime": str(from_time), "toActionTime": str(to_mid_time),
                      "maxCount": max_count}
            resp = requests.get(url, params=params, verify=False).json()
            while iter_target:
                resp = resp.get(iter_target.pop(0))

            while len(resp):
                bad_guy = resp.pop()
                if bad_guy['ip'] not in duplicate_moval:
                    duplicate_moval.append(bad_guy['ip'])
                    calculation_list.append(bad_guy)
            while len(calculation_list):
                cl = calculation_list.pop()
                data = {"asset_ip": str(cl["ip"]), "branch_id": int(cl["branchId"]), "event_key": str(cl["eventKey"]),
                        "rule_id": int(cl["ruleId"]), "data_type": int(cl["type"]), "group": int(cl["groupId"]),
                        "token": token}

                respp = \
                    requests.post(config.SXF_BASE_URL % (config.SXF_IP, "detail"), verify=False, json=data)
                respp = respp.json()["data"]["top10"]
                while respp:
                    bigbadguy = respp.pop()

                    try:
                        pre_data = {"srcCountryCrc": bigbadguy['srcCountryCrc'],
                                    "srcProvinceCrc": bigbadguy['srcProvinceCrc'],
                                    "dstCountryCrc": bigbadguy['dstCountryCrc'],
                                    "dstProvibceCrc": bigbadguy['dstProvinceCrc']}
                        if not resp_data.count(pre_data):
                            resp_data.append(pre_data)
                    except Exception as e:
                        continue

            from_datetime = from_datetime + datetime.timedelta(days=interval)
            iter_time -= 1
    else:
        params = {"token": token, "fromActionTime": str(from_time), "toActionTime": str(to_time),
                  "maxCount": max_count}
        resp = requests.get(url, params=params, verify=False).json()
        while target:
            resp = resp.get(target.pop(0))

        while len(resp):
            bad_guy = resp.pop()
            if bad_guy['ip'] not in duplicate_moval:
                duplicate_moval.append(bad_guy['ip'])
                calculation_list.append(bad_guy)
        while len(calculation_list):
            cl = calculation_list.pop()
            data = {"asset_ip": str(cl["ip"]), "branch_id": int(cl["branchId"]), "event_key": str(cl["eventKey"]),
                    "rule_id": int(cl["ruleId"]), "data_type": int(cl["type"]), "group": int(cl["groupId"]),
                    "token": token}
            respp = \
                requests.post(config.SXF_BASE_URL % (config.SXF_IP, "detail"), verify=False, json=data).json()["data"]

            respp = respp["top10"]

            while respp:
                bigbadguy = respp.pop()
                try:
                    pre_data = {"srcCountryCrc": bigbadguy['srcCountryCrc'],
                                "srcProvinceCrc": bigbadguy['srcProvinceCrc'],
                                "dstCountryCrc": bigbadguy['dstCountryCrc'],
                                "dstProvibceCrc": bigbadguy['dstProvinceCrc']}
                    if not resp_data.count(pre_data):
                        resp_data.append(pre_data)
                except Exception as e:
                    continue

    redis.set(redis_key, demjson.encode(resp_data, strict=False))
    redis.expire(redis_key, 86400)
    return Response(json.dumps({"code": 1, "data": resp_data}, cls=DateEncoder), mimetype='application/json')


@apis.route("/sxf_riskeven_detail_src/", methods=["get"])
def sxf_riskeven_detail_src():
    args = request.args.to_dict()
    method = args.get('method')
    target = args.get('target')
    target = target.split(".") if target else target
    from_time = args.get('fromTime')
    from_time = int(from_time) if from_time else int((datetime.datetime.now() - datetime.timedelta(days=8)).timestamp())
    to_time = args.get('toTime')
    to_time = int(to_time) if to_time else int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())
    max_count = args.get('maxCount')
    url = config.SXF_BASE_URL % (config.SXF_IP, method)
    interval = int(args.get('interval'))
    token = sxf_token()

    ru = request.url.replace('&cache_del=1', '')
    redis_key = TokenMaker().generate_token(ru, request.method)
    cache_del = args.get('cache_del')
    if not cache_del:
        cache_data = redis.get(redis_key)
        if cache_data != None:
            return Response(json.dumps({"code": 1, "data": demjson.decode(cache_data)}, cls=DateEncoder),
                            mimetype='application/json')

    resp_data = dict()
    duplicate_moval = []
    calculation_list = []

    if interval:
        from_datetime = datetime.datetime.fromtimestamp(from_time)  # 时间戳转日期
        to_datetime = datetime.datetime.fromtimestamp(to_time)  # 时间戳转日期
        iter_time = ceil((to_datetime - from_datetime).days / interval)
        while iter_time:
            iter_target = copy.deepcopy(target)
            from_time = int(from_datetime.timestamp())
            to_mid_time = int((from_datetime + datetime.timedelta(days=interval)).timestamp())

            params = {"token": token, "fromActionTime": str(from_time), "toActionTime": str(to_mid_time),
                      "maxCount": max_count}
            resp = requests.get(url, params=params, verify=False).json()
            while iter_target:
                resp = resp.get(iter_target.pop(0))

            while len(resp):
                bad_guy = resp.pop()
                if bad_guy['ip'] not in duplicate_moval:
                    duplicate_moval.append(bad_guy['ip'])
                    calculation_list.append(bad_guy)
            while len(calculation_list):
                cl = calculation_list.pop()
                data = {"asset_ip": str(cl["ip"]), "branch_id": int(cl["branchId"]), "event_key": str(cl["eventKey"]),
                        "rule_id": int(cl["ruleId"]), "data_type": int(cl["type"]), "group": int(cl["groupId"]),
                        "token": token}
                respp = \
                    requests.post(config.SXF_BASE_URL % (config.SXF_IP, "detail"), verify=False, json=data).json()[
                        "data"]["top10"]
                while respp:
                    bigbadguy = respp.pop()
                    try:
                        if resp_data.get(bigbadguy['srcCountryCrc']):
                            resp_data[bigbadguy['srcCountryCrc']] += bigbadguy['attackCount']
                        else:
                            resp_data[bigbadguy['srcCountryCrc']] = bigbadguy['attackCount']
                    except Exception as e:
                        continue

            from_datetime = from_datetime + datetime.timedelta(days=interval)
            iter_time -= 1

    else:
        params = {"token": token, "fromActionTime": str(from_time), "toActionTime": str(to_time),
                  "maxCount": max_count}
        resp = requests.get(url, params=params, verify=False).json()
        while target:
            resp = resp.get(target.pop(0))

        while len(resp):
            bad_guy = resp.pop()
            if bad_guy['ip'] not in duplicate_moval:
                duplicate_moval.append(bad_guy['ip'])
                calculation_list.append(bad_guy)
        while len(calculation_list):
            cl = calculation_list.pop()
            data = {"asset_ip": str(cl["ip"]), "branch_id": int(cl["branchId"]), "event_key": str(cl["eventKey"]),
                    "rule_id": int(cl["ruleId"]), "data_type": int(cl["type"]), "group": int(cl["groupId"]),
                    "token": token}
            respp = \
                requests.post(config.SXF_BASE_URL % (config.SXF_IP, "detail"), verify=False, json=data).json()["data"][
                    "top10"]
            while respp:
                bigbadguy = respp.pop()
                try:
                    if resp_data.get(bigbadguy['srcCountryCrc']):
                        resp_data[bigbadguy['srcCountryCrc']] += bigbadguy['attackCount']
                    else:
                        resp_data[bigbadguy['srcCountryCrc']] = bigbadguy['attackCount']
                except Exception as e:
                    continue

    redis.set(redis_key, demjson.encode(resp_data, strict=False))
    redis.expire(redis_key, 86400)

    return Response(json.dumps({"code": 1, "data": resp_data}, cls=DateEncoder), mimetype='application/json')


@apis.route("/sxf_riskeven_detail_list/", methods=["get"])
def sxf_riskeven_detail_list():
    args = request.args.to_dict()
    method = args.get('method')
    target = args.get('target')
    target = target.split(".") if target else target
    from_time = args.get('fromTime')
    from_time = int(from_time) if from_time else int((datetime.datetime.now() - datetime.timedelta(days=8)).timestamp())
    to_time = args.get('toTime')
    to_time = int(to_time) if to_time else int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())
    max_count = args.get('maxCount')
    url = config.SXF_BASE_URL % (config.SXF_IP, method)
    interval = int(args.get('interval'))
    token = sxf_token()

    ru = request.url.replace('&cache_del=1', '')
    redis_key = TokenMaker().generate_token(ru, request.method)
    cache_del = args.get('cache_del')
    if not cache_del:
        cache_data = redis.get(redis_key)
        if cache_data != None:
            return Response(json.dumps({"code": 1, "data": demjson.decode(cache_data)}, cls=DateEncoder),
                            mimetype='application/json')

    resp_data = []
    duplicate_moval = []
    calculation_list = []

    if interval:
        from_datetime = datetime.datetime.fromtimestamp(from_time)  # 时间戳转日期
        to_datetime = datetime.datetime.fromtimestamp(to_time)  # 时间戳转日期
        iter_time = ceil((to_datetime - from_datetime).days / interval)

        while iter_time:
            iter_target = copy.deepcopy(target)
            from_time = int(from_datetime.timestamp())
            to_mid_time = int((from_datetime + datetime.timedelta(days=interval)).timestamp())

            params = {"token": token, "fromActionTime": str(from_time), "toActionTime": str(to_mid_time),
                      "maxCount": max_count}
            resp = requests.get(url, params=params, verify=False).json()
            while iter_target:
                resp = resp.get(iter_target.pop(0))

            while len(resp):
                bad_guy = resp.pop()
                if bad_guy['ip'] not in duplicate_moval:
                    duplicate_moval.append(bad_guy['ip'])
                    calculation_list.append(bad_guy)
            while len(calculation_list):
                cl = calculation_list.pop()
                data = {"asset_ip": str(cl["ip"]), "branch_id": int(cl["branchId"]), "event_key": str(cl["eventKey"]),
                        "rule_id": int(cl["ruleId"]), "data_type": int(cl["type"]), "group": int(cl["groupId"]),
                        "token": token}
                respp = \
                    requests.post(config.SXF_BASE_URL % (config.SXF_IP, "detail"), verify=False, json=data).json()[
                        "data"]["top10"]
                while respp:
                    bigbadguy = respp.pop()
                    if bigbadguy['level'] == 3:
                        try:
                            resp_data.append(
                                {"recordTime": bigbadguy["recordTime"],
                                 "srcIp": bigbadguy["srcIp"], "dstIp": bigbadguy["dstIp"],
                                 "attackType": bigbadguy["attackType"], "level": bigbadguy["level"],
                                 "attackCount": bigbadguy["attackCount"]})
                        except Exception as e:
                            continue

            from_datetime = from_datetime + datetime.timedelta(days=interval)
            iter_time -= 1
    else:
        params = {"token": token, "fromActionTime": str(from_time), "toActionTime": str(to_time),
                  "maxCount": max_count}
        resp = requests.get(url, params=params, verify=False).json()
        while target:
            resp = resp.get(target.pop(0))

        while len(resp):
            bad_guy = resp.pop()
            if bad_guy['ip'] not in duplicate_moval:
                duplicate_moval.append(bad_guy['ip'])
                calculation_list.append(bad_guy)
        while len(calculation_list):
            cl = calculation_list.pop()
            data = {"asset_ip": str(cl["ip"]), "branch_id": int(cl["branchId"]), "event_key": str(cl["eventKey"]),
                    "rule_id": int(cl["ruleId"]), "data_type": int(cl["type"]), "group": int(cl["groupId"]),
                    "token": token}
            respp = \
                requests.post(config.SXF_BASE_URL % (config.SXF_IP, "detail"), verify=False, json=data).json()["data"][
                    "top10"]
            while respp:
                bigbadguy = respp.pop()
                if bigbadguy['level'] == 3:
                    try:
                        resp_data.append(
                            {"recordTime": bigbadguy["recordTime"],
                             "srcIp": bigbadguy["srcIp"], "dstIp": bigbadguy["dstIp"],
                             "attackType": bigbadguy["attackType"], "level": bigbadguy["level"],
                             "attackCount": bigbadguy["attackCount"]})
                    except Exception as e:
                        continue
    resp_data = sorted(resp_data, key=lambda k: k['attackCount'], reverse=True)
    resp_data = sorted(resp_data[:20], key=lambda k: k['recordTime'], reverse=True)
    redis.set(redis_key, demjson.encode(resp_data, strict=False))
    redis.expire(redis_key, 86400)

    return Response(json.dumps({"code": 1, "data": resp_data}, cls=DateEncoder), mimetype='application/json')


@apis.route("/sxf_riskeven_by_field/", methods=["get"])
def sxf_riskeven_by_field():
    args = request.args.to_dict()
    method = args.get('method')
    target = args.get('target')
    target = target.split(".") if target else target
    from_time = args.get('fromTime')
    from_time = int(from_time) if from_time else int((datetime.datetime.now() - datetime.timedelta(days=8)).timestamp())
    to_time = args.get('toTime')
    to_time = int(to_time) if to_time else int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())
    max_count = args.get('maxCount')
    url = config.SXF_BASE_URL % (config.SXF_IP, method)
    interval = int(args.get('interval'))
    token = sxf_token()
    ru = request.url.replace('&cache_del=1', '')
    redis_key = TokenMaker().generate_token(ru, request.method)
    cache_del = args.get('cache_del')
    if not cache_del:
        cache_data = redis.get(redis_key)
        if cache_data != None:
            return Response(json.dumps({"code": 1, "data": demjson.decode(cache_data)}, cls=DateEncoder),
                            mimetype='application/json')

    resp_data = []
    duplicate_moval = []
    calculation_list = []
    if interval:
        from_datetime = datetime.datetime.fromtimestamp(from_time)  # 时间戳转日期
        to_datetime = datetime.datetime.fromtimestamp(to_time)  # 时间戳转日期
        iter_time = ceil((to_datetime - from_datetime).days / interval)

        while iter_time:
            iter_target = copy.deepcopy(target)
            from_time = int(from_datetime.timestamp())
            to_mid_time = int((from_datetime + datetime.timedelta(days=interval)).timestamp())

            params = {"token": token, "fromActionTime": str(from_time), "toActionTime": str(to_mid_time),
                      "maxCount": max_count}
            resp = requests.get(url, params=params, verify=False).json()
            while iter_target:
                resp = resp.get(iter_target.pop(0))
            while len(resp):
                bad_guy = resp.pop()
                if bad_guy['ip'] not in duplicate_moval and bad_guy['eventType'] == 1:
                    duplicate_moval.append(bad_guy['ip'])
                    calculation_list.append(bad_guy)
            while len(calculation_list):
                cl = calculation_list.pop()
                try:
                    resp_data.append(
                        {'eventDes': cl['eventDes'], 'dealStatus': cl['dealStatus'], 'damage': cl['damage'],
                         'principle': cl['principle'], 'solution': cl['solution'], 'tag': cl['tag'],
                         'hostRisk': cl['hostRisk']})
                except Exception as e:
                    continue

            from_datetime = from_datetime + datetime.timedelta(days=interval)
            iter_time -= 1
    else:
        params = {"token": token, "fromActionTime": str(from_time), "toActionTime": str(to_time),
                  "maxCount": max_count}
        resp = requests.get(url, params=params, verify=False).json()
        while target:
            resp = resp.get(target.pop(0))
        while len(resp):
            bad_guy = resp.pop()
            if bad_guy['ip'] not in duplicate_moval and bad_guy['eventType'] == 1:
                duplicate_moval.append(bad_guy['ip'])
                calculation_list.append(bad_guy)
        while len(calculation_list):
            cl = calculation_list.pop()
            try:
                resp_data.append(
                    {'eventDes': cl['eventDes'], 'dealStatus': cl['dealStatus'], 'damage': cl['damage'],
                     'principle': cl['principle'], 'solution': cl['solution'], 'tag': cl['tag'],
                     'hostRisk': cl['hostRisk']})
            except Exception as e:
                continue

    redis.set(redis_key, demjson.encode(resp_data, strict=False))
    redis.expire(redis_key, 86400)

    return Response(json.dumps({"code": 1, "data": resp_data}, cls=DateEncoder), mimetype='application/json')


@apis.route("/sxf_branch_count/", methods=["get"])
def sxf_branch_count():
    args = request.args.to_dict()
    method = args.get('method')

    url = config.SXF_BASE_URL % (config.SXF_IP, method)
    token = sxf_token()

    ru = request.url.replace('&cache_del=1', '')
    redis_key = TokenMaker().generate_token(ru, request.method)
    cache_del = args.get('cache_del')
    if not cache_del:
        cache_data = redis.get(redis_key)
        if cache_data != None:
            return Response(json.dumps({"code": 1, "data": demjson.decode(cache_data)}, cls=DateEncoder),
                            mimetype='application/json')

    params = {"token": token}
    resp = requests.get(url, params=params, verify=False).json()
    resp_len = len(resp['data'].values())

    redis.set(redis_key, demjson.encode(resp_len, strict=False))
    redis.expire(redis_key, 86400)
    return Response(json.dumps({"code": 1, "data": resp_len}, cls=DateEncoder), mimetype='application/json')


@apis.route("/deal/", methods=["POST"])
def deal():
    json_data = request.get_json()
    url = json_data["url"]
    obj = {
        "StatType": "",
        "Type": "",
        "DeptUID": "",
        "DeptName": "",
        "UserID": "",
        "UserName": "",
        "DeptSID": "",
        "SvcID": "",
        "TimeFrom": "2017/11/27 9:16:08",
        "TimeTo": "2018/11/27 9:16:08",
        "SvcName": "",
        "Field": "",
        "Digit": "10",
        "Name": "",
        "OperTotal": "",
        "ResponseTotal": "",
        "Flow": "",
        "IpTotal": "",
        "ID": "",
        "Count": "",
        "Month": "",
        "RankNum": "",
        "Time": ""
    }

    now_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    today = datetime.date.today()
    last_month = today + datetime.timedelta(days=-today.day)
    sh_time = datetime.datetime.strftime(last_month, "%Y/%m/%d") + " " + now_time.split(" ")[1]
    obj["TimeFrom"] = sh_time
    obj["TimeTo"] = now_time

    data = requests.post(url, obj)
    re_data = []

    for i in eval(data.text.replace('null', 'None')):
        dic = {}
        dic["IpTotal"] = int(i["IpTotal"])
        dic["Name"] = i["Name"]
        dic["OperTotal"] = int(i["OperTotal"])
        dic["ResponseTotal"] = int(i["ResponseTotal"])
        re_data.append(dic)
    re_data.sort(key=lambda s: s["ResponseTotal"], reverse=True)

    return Response(json.dumps({"code": 1, "data": re_data[0:10]}, cls=DateEncoder), mimetype='application/json')
