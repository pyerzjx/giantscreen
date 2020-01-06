from collections import OrderedDict
from flask import g,request
import xpinyin
import re


# 请求参数处理
def deal_with_district_code(district_code):
    prepare_code = {'佛山市': '440601%', '禅城区': '440604%', '南海区': '440605%', '顺德区': '440606%', '三水区': '440607%',
                    '高明区': '440608%'}
    return prepare_code.get(district_code)


#  请求参数处理函数2
def area_num(district_code):
    prepare_code = {'全市': "('440604','440605','440606','440607','440608','440600')", '禅城区': "('440604')",
                    '南海区': "('440605')", '顺德区': "('440606')", '三水区': "('440607')",
                    '高明区': "('440608')"}

    return prepare_code.get(district_code)


def deal_with_initials(pinyin):
    xp = xpinyin.Pinyin()
    return '%s as "value"' % (xp.get_initials(pinyin, u''))


# 参数处理 加单引号
def deal_code(district_code):
    district_code = "'" + district_code + "'"

    return district_code


# 参数处理 加百分号
def deal_baifenhao(district_code):
    district_code = "%" + district_code + "%"

    return district_code


# 去除区域百分号
def baifenhao(data):
    for i in data:
        if '%' in i["area"]:
            i["area"] = i["area"].replace("%", "")
    return data


# 行政中心名、编号参数转换
def serviceid_cn(district_code):
    prepare_code = {'九江镇行政服务中心': '44060512100001', '大沥镇大沥行政服务中心': '44060512500001', '大沥镇黄岐行政服务中心': '44060512500002',
                    '大沥镇盐步行政服务中心': '44060512500003', '芦苞镇行政服务中心': '44060710500001', '南庄行政服务中心': '44060410000001',
                    '伦教街道行政服务中心': '44060600300001', '容桂街道行政服务中心': '44060600600001', '南海区行政服务中心': '44060500000001',
                    '佛山市行政服务中心': '44060000000001', '白坭镇行政服务中心': '44060710400001', '里水镇和顺行政服务中心': '44060512600002',
                    '张槎行政服务中心': '44060401100001', '禅城区祖庙街道行政服务中心供水窗口': '4406060126804', '陈村镇行政服务中心': '44060610100001',
                    '高明区行政服务中心': '44060800000001', '顺德区行政服务中心(西座)': '44060600000002', '区行政服务中心智慧新城大厅': '44060400000002',
                    '西樵镇行政服务中心': '44060512200001', '狮山镇小塘行政服务中心': '44060512400003', '狮山镇大圃行政服务中心': '44060512400004',
                    '狮山镇罗村行政服务中心': '44060512400005', '均安镇行政服务中心': '44060610600001', '杏坛镇行政服务中心': '44060610500001',
                    '桂城街道行政服务中心': '44060501100001', '狮山镇行政服务中心': '44060512400001', '高明区明城镇行政服务中心': '44060810700001',
                    '云东海街道行政服务中心': '44060700400001', '南山镇行政服务中心': '44060710600001', '六和行政服务中心': '44060710600002',
                    '高明区杨和镇行政服务中心': '44060810600001', '狮山镇官窑行政服务中心': '44060512400006', '三水区行政服务中心': '44060700000001',
                    '西南街道行政服务中心': '44060700100001', '龙江镇行政服务中心': '44060610400001', '丹灶镇行政服务中心': '44060512300001',
                    '乐平镇行政服务中心': '44060710300001', '佛山高新区行政服务中心': '44060512400007', '大良街道行政服务中心（A区）': '44060600500001',
                    '乐从镇行政服务中心': '44060610300001', '顺德区行政服务中心(东座)': '44060600000001', '高明区更合镇行政服务中心': '44060810800001',
                    '狮山镇松岗行政服务中心': '44060512400002', '区行政服务中心魁奇路大厅': '44060400000001', '石湾行政服务中心': '44060401000001',
                    '大良行政服务中心B区': '4406060054905', '里水镇行政服务中心': '44060512600001', '大塘镇行政服务中心': '44060710100001',
                    '大塘镇行政服务中心': '44060710100001', '白坭镇行政服务中心': '44060710400001', '乐平镇行政服务中心': '44060710300001',
                    '南山镇行政服务中心': '44060710600001',
                    '祖庙行政服务中心': '44060401200001', '北滘镇行政服务中心': '44060610200001', '勒流街道行政服务中心': '44060600400001'}
    return prepare_code.get(district_code)


# 数据格式处理
def deal_with_xaxisname(data):
    xaxisname = dict()
    name = dict()
    res = []
    if isinstance(data, list):
        for i in data:
            xaxisname[i.get('LL')] = i.get('XAXISNAME')
            name[i.get('CKLX')] = i.get('NAME')

        ll = sorted(xaxisname)
        cklx = sorted(name)
        res.append({'xAxisName': [xaxisname.get(i) for i in ll]})

        for cl in cklx:
            pre_data = []
            for j in ll:
                for k in data:
                    if all([k['CKLX'] == cl, k['LL'] == j]):
                        pre_data.append(k['COUNT'])
                        break
            res.append({'name': name.get(cl), 'data': pre_data})
    return res


def deal_chuangkoutype(data):
    res = []
    xAxisName = ["禅城区", "南海区", "顺德区", "高明区", "三水区"]
    chuangkou_type = ["经营许可", "投资建设", "企业登记", "社会民生", "税务", "公安", "其他类"]
    res.append({"xAxisName": xAxisName})
    for i in range(1, 8):
        dic = {}
        dic["name"] = chuangkou_type[i - 1]
        lis = [0, 0, 0, 0, 0]
        for j in xAxisName:
            for jj in data:
                if jj["CHUANGKOU"] == dic["name"] and jj["AREA"] == j:
                    lis[xAxisName.index(j)] = jj["COUNT(*)"]
        dic["data"] = lis
        res.append(dic)
    return res


def deal_with_one_reversal(data):
    pre_data = []
    for k, v in data[0].items():
        pre_data.append({'name': k, 'count': v})
    return pre_data


def deal_with_gongdan(data):
    res_data = {}
    res_data['xAxisName'] = [i.get('xAxisName') for i in data]

    for i in data:
        i.pop('xAxisName')

    pre_data = data[0]
    res_data['lengendData'] = list(pre_data.keys())

    res_data['data'] = [list(j.values()) for j in data]
    return res_data


def loop_into_set(k, data):
    return set(map(lambda d: d.get(k), data))


def compose(data):
    li = data.popitem()
    li = {li[0]: li[1]}
    res = []
    if len(data):
        ll = compose(data)
        for i in list(li.values())[0]:
            if isinstance(ll, dict):
                for j in list(ll.values())[0]:
                    res.append({list(li.keys())[0]: i, list(ll.keys())[0]: j})
            elif isinstance(ll, list):
                for j in ll:
                    j.update({list(li.keys())[0]: i})
                    res.append(j)
    else:
        res = li
    return res


def deal_with_two_set(data):
    dw_data = list(data[0].keys())
    pre_res = [loop_into_set(i, data) for i in dw_data[:-1]]
    res = dict(zip(dw_data[:-1], pre_res))

    dw_data_list = []

    for i in pre_res[0]:
        pre_dw_data_list = []
        for j in pre_res[1]:
            for d in data:
                if all([d.get(dw_data[:-1][1]) == j, d.get(dw_data[:-1][0]) == i]):
                    pre_dw_data_list.append(d.get(dw_data[-1]))

        dw_data_list.append(pre_dw_data_list)

    res.update({dw_data[-1]: dw_data_list})
    return res


# 区域统计数据处理
def area_count(data):
    res = []
    for i in data:
        dic = {}
        dic["name"] = i["AREA"]
        dic["count"] = i["COUNT"]
        res.append(dic)
    return res


# 分页数据处理
def deal_page(data):
    args = g.get('args')
    res = {}
    res["page"] = args["p1"]
    res["rows"] = data
    res["total"] = len(data)

    return res


# 员工信息数据处理
def deal_yuangong(data):
    res = {}
    for i in data:
        res["num"] = i["employeenum"]
        res["name"] = i["employeename"]
        res["PersonnelNature"] = i["nature"]
        res["servicePost"] = i["servicepost"]
        res["sex"] = i["SEX"]
        res["serviceLength"] = 1
        res["business"] = str(i["business"]) + "件"
        res["staisfaction"] = "90%"
    return res


# 必经环节数据格式处理
def bijinghj_deal(data):
    res = []
    for i in data:
        ressq = {}
        ressq["name"] = i["sqbusiname"]
        ressq["time"] = i["sqtime"]
        ressq["data"] = [{"登记时间": i["sqtime"], "申请来源": i["sqsourcetype"], "申请人类型": i["sqrlxtype"], "申请人名称": i["sqname"],
                          "申请人证件号码": i["sqcardid"], "事项编码": i["sqsssxbm"], "事项名称": i["sqsssxmc"],
                          "承诺时限": (str(i["sqtimelimit"]) + "个工作日"),
                          "申请结果": i["sqresult"], "经办人": i["sqnodeactor"], "处理时间": i["sqdealtime"]}]
        res.append(ressq)
        ressl = {}
        ressl["name"] = i["slbusiname"]
        ressl["time"] = i["sltime"]
        ressl["data"] = [{"登记时间": i["sltime"], "审核材料份数": i["slclid"], "审核结果": i["slresult"],
                          "经办人": i["slpervnodeactor"], "处理时间": i["sldealtime"]}]
        res.append(ressl)
        resxs = {}
        resxs["name"] = i["xsbusiname"]
        resxs["time"] = i["xstime"]
        resxs["data"] = [{"登记时间": i["xstime"], "审核结果": i["xsresult"], "处理部门": i["xsdepartmentid"],
                          "经办人": i["xsnodeactor"], "处理时间": i["xshandlerdate"]}]
        res.append(resxs)

        ressc = {}
        ressc["name"] = i["scbusiname"]
        ressc["time"] = i["sctime"]
        ressc["data"] = [{"登记时间": i["sctime"], "审核结果": i["scresult"], "处理部门": i["scdepartmentid"],
                          "经办人": i["scnodeactor"], "处理时间": i["schandlerdate"]}]
        res.append(ressc)

        reszjqf = {}
        reszjqf["name"] = i["zjbusiname"]
        reszjqf["time"] = i["zjtime"]
        reszjqf["data"] = [{"登记时间": i["zjtime"], "签发人": i["zjissueactor"], "证件名称": i["zjmc"],
                            "经办人": i["zjnodeactor"], "处理时间": i["zjhandlerdate"]}]
        res.append(reszjqf)

        reszjbf = {}
        reszjbf["name"] = i["zjbusiname"]
        reszjbf["time"] = i["zjtime"]
        reszjbf["data"] = [{"登记时间": i["zjtime"], "送达方式": i["zjbfsdfs"], "送达时间": i["zjbfsdsj"],
                            "经办人": i["zjbfnodeactor"], "处理时间": i["zjbfhandlerdate"]}]
        res.append(reszjbf)
    return res


#  大厅窗口数据处理
def dating_deal(data):
    res = []
    cklc = []
    type01 = ["社会民生", "企业登记", "经营许可", "投资建设", "公安", "税务", "其他类"]
    if data == []:
        return []
    print("data=", data)
    for i in data:
        print("iiii=", i)
        if i["STAFF_CODE11"] == None:
            i["STAFF_CODE11"] = ""
            status = "空闲"
        else:
            status = "正在办理业务"
        if i["CKLC"] not in cklc:
            resdic = {}
            cklc.append(i["CKLC"])
            resdic["floor"] = i["CKLC"]
            resdic["windowsCount"] = i["COUNT"]
            a = int(i["COUNT"] / 2)
            resdic["windowsInfo"] = [{"name": "正在办理窗口", "count": a}, {"name": "今日无业务窗口", "count": 0},
                                     {"name": "空闲窗口", "count": (i["COUNT"] - a)},
                                     {
                                         "name": "数据关联出错窗口",
                                         "count": 0
                                     }]
            if i["STAFF_CODE11"] != "":
                resdic["windowsList"] = [{
                    "id": i["STAFF_CODE11"],
                    "type": type01[int(i["CKLX"]) - 1],
                    "status": status
                }]

                res.append(resdic)
        else:
            tt = i["CKLC"]
            aa = {
                "id": i["STAFF_CODE11"],
                "type": type01[int(i["CKLX"]) - 1],
                "status": status
            }
            for j in res:
                if j["floor"] == tt and aa not in j["windowsList"] and i["STAFF_CODE11"] != None and [
                    "STAFF_CODE11"] != "":
                    j["windowsList"].append({
                        "id": i["STAFF_CODE11"],
                        "type": type01[int(i["CKLX"]) - 1],
                        "status": status
                    })

    for aa in res:
        for bb in aa["windowsList"]:
            if bb["id"] == "":
                aa["windowsList"].remove(bb)
    return res


def deal_with_kv_separate(data):
    k2p = list(data[0].keys())
    xp = xpinyin.Pinyin()
    pre_data = []
    pinyink = dict(zip(k2p, [xp.get_initials(pinyin, u'').lower() for pinyin in k2p]))
    for i in data:
        p_d = {}
        for j in i:
            p_d[pinyink[j]] = i[j]
        pre_data.append(p_d)
    return pre_data


def deal_with_kv_separate2(data):
    if data:
        xp = xpinyin.Pinyin()
        k2p = list(data[0].keys())
        pre_data = [{'coordinate': k2p}]
        pinyink = dict(zip(k2p, [xp.get_pinyin(pinyin, u'').lower() for pinyin in k2p]))
        for i in data:
            p_d = {}
            for j in i:
                p_d[pinyink[j]] = i[j]
            pre_data.append(p_d)
        return pre_data
    else:
        return data


# 九楼舆情大屏企业舆情处理
def deal_qiyeyuqing(data):
    res = []
    quchonglist = []
    for i in data:
        dic = {}
        dic["name"] = i["ENTERPRISE"]
        dic["datas"] = [
            {"name": "调解成功率", "value": str(i["TIAOJIECHENGGONGLV"]) + "%"},
            {"name": "投诉量", "value": i["TOUSU_ZONG"]},
            {"name": "投诉增长率", "value": str(i["TOUSUZENGZHANGLV"]) + "%"},
            {"name": "爆发性问题", "value": i["EXPLOSIVE_ISSUES"]},
            {"name": i["PROBLEMCLASSIFICATION"], "value": i["F_TOUSUL"]}
        ]
        if i["ENTERPRISE"] not in quchonglist:
            quchonglist.append(i["ENTERPRISE"])
            res.append(dic)
        else:
            for ii in res:
                if ii["name"] == i["ENTERPRISE"]:
                    ii["datas"].append(dic["datas"][4])
    #  排序方式二
    # for i in data:
    #     x = i["datas"][4:]
    #     aa = sorted(x, key=lambda x: x['value'], reverse=True)
    #     i["datas"] = i["datas"][0:4] + aa
    return res

# 处理列表中重复字典元素
def deleteDuplicate(li):
    temp_list = list(set([str(i) for i in li]))
    li = [eval(i) for i in temp_list]
    return li

# 处理运营大屏 运营检测处理
def deal_yunyingjiance(data):
    res = []
    for i in data:
        dic = {}
        dic["itemName"] = i["KIND"]
        dic["value"] = i["CATEGORY"]
        dic["starCount"] = i["WARNING"]
        if dic not in res:
            res.append(dic)

    t_data = []
    for ii in data:
        dic = {}
        dic["itemName"] = ii["KIND"]
        dic["value"] = ii["CATEGORY"]
        dic["starCount"] = ii["WARNING"]
        id1 = ii["id1"]
        id2 = ii["id2"]
        id3 = ii["id3"]
        if ii["CATEGORY"] == "工单流转" and ii["KIND"] == "流转部门较多":  # 短链接
            dic["starName"] = [{"name": ii["CONTENT"], "id1": id1, "id2": "", "id3": ""}]
        elif ii["CATEGORY"] == "工单流转" and ii["KIND"] == "超时反馈":  # 长链接
            dic["starName"] = [{"name": ii["CONTENT"], "id1": id1, "id2": id2, "id3": id3}]
        elif ii["CATEGORY"] == "异常表单" and ii["KIND"] == "特殊表单":  # 短链接
            dic["starName"] = [{"name": ii["CONTENT"], "id1": id1, "id2": "", "id3": ""}]
        elif ii["CATEGORY"] == "异常表单" and ii["KIND"] == "长时间暂存":  # 短链接
            dic["starName"] = [{"name": ii["CONTENT"], "id1": id1, "id2": "", "id3": ""}]
        elif ii["CATEGORY"] == "异常表单" and ii["KIND"] == "多次被值班座席退回":  # 短链接
            dic["starName"] = [{"name": ii["CONTENT"], "id1": id1, "id2": "", "id3": ""}]
        else:
            dic["starName"] = [{"name": ii["CONTENT"], "id1": "", "id2": "", "id3": ""}]

        t_data.append(dic)
    re_data = []
    for j in res:
        pre_dic = {}
        starName_lst = []
        pre_dic["itemName"] = j["itemName"]
        pre_dic["value"] = j["value"]
        pre_dic["starCount"] = j["starCount"]
        for jj in filter(lambda x: x["itemName"] == j["itemName"] and x["value"] == j["value"] and x["starCount"] == j[
            "starCount"], t_data):
            starName_lst = starName_lst + jj["starName"]
        pre_dic["starName"] = deleteDuplicate(starName_lst)
        re_data.append(pre_dic)
    return re_data


#  处理运营大屏 智能知识采集
def deal_zhinengzhishi(data):
    xinzenglst = []
    xiugailst = []
    res = {}
    for i in data:
        if i["MANAGEMENT"] == "新增":
            xinzenglst.append({"name": i["PARENTLEVEL"], "value": i["SUM_NUM"]})
        else:
            xiugailst.append({"name": i["PARENTLEVEL"], "value": i["SUM_NUM"]})

    res["addDate"] = xinzenglst
    res["updateDate"] = xiugailst

    return res


# 处理运营大屏 智能知识采集 咨询热点
def deal_zhinengzhishi_xixunredian(data):
    xinzenglst = []
    xiugailst = []
    res = {}
    for i in data:
        if i["MANAGEMENT"] == "新增":
            xinzenglst.append({"hotSopt": i["NAME"], "heat": i["NUM11"]})
        else:
            xiugailst.append({"hotSopt": i["NAME"], "heat": i["NUM11"]})

    res["leftDate"] = xinzenglst
    res["rightDate"] = xiugailst

    return res


# 舆情大屏 情绪预警数据处理
def deal_qingxuyujing(data):
    res = []
    rnlist = []
    for i in data:
        if i["RN"] not in rnlist:
            rnlist.append(i["RN"])
            dic = {}
            dic_lst = []
            dic["RN"] = i["RN"]
            dic_lst.append({"TYPE": i["TYPE"], "XAXIS": i["XAXIS"], "YAXIS": i["YAXIS"]})
            dic["datas"] = dic_lst
            res.append(dic)
        else:
            for j in res:
                if j["RN"] == i["RN"]:
                    j["datas"].append({"TYPE": i["TYPE"], "XAXIS": i["XAXIS"], "YAXIS": i["YAXIS"]})

    return res


# 运营大屏好差评 满意度数据处理
def haochaping_manyidu(data):
    res = []
    for i in data:
        dic = {}
        dic["KIND"] = i["KIND"]
        dic["BMY_FCBMY"] = i["BMY"] + i["FCBMY"]
        dic["ZL"] = i["FCMY"] + i["MY"] + i["YB"] + i["BMY"] + i["FCBMY"] + i["WPJ"]
        res.append(dic)
    res_dic = {}
    BMY_FCBMY = 0
    ZL = 0
    for j in res:
        if j["KIND"] == "BANJIAN":
            res_dic["banjianmanyidu"] = "%.1f" % ((1 - (j["BMY_FCBMY"] / j["ZL"])) * 100) + "%"
        else:
            BMY_FCBMY = BMY_FCBMY + j["BMY_FCBMY"]
            ZL = ZL + j["ZL"]
    res_dic["rexianmayidu"] = "%.1f" % ((1 - BMY_FCBMY / ZL) * 100) + "%"

    return res_dic


# 九楼热线舆情大屏 智能舆情
def zhinengyuqing_deal(data):
    res = []
    for i in data:
        dic = {}
        v= re.search("\d+(\.\d+)?",i["INDEXVAL"])
        it = float(v.group())
        if it <= 10:
            dic[i["INDEXNAME"]] = round(it)
        else:
            a = 1
            while True:
                b = it / (10 * a)
                if 0 <= b <= 10:
                    dic[i["INDEXNAME"]] = round(b)
                    break
                else:
                    a = a + 1
        res.append(dic)
    return res


# 九楼热线运营大屏 智能运营搜索处理接口
def deal_zhinengyunying_seacher(data):
    searchData = {}
    idlist = []
    leve3list = []
    searchData["faceProblem"] = []
    searchData["problemAnalysis"] = []
    leve2list = []
    for i in data:
        levenum = i["LEVELNUM"]
        if levenum == "1":
            searchData["problem"] = i["CONTENT"] + i["VALUE"]
        elif i["LEVELNUM"] == "2":
            idlist.append({"id": i["ID"], "name": i["CONTENT"]})
            searchData["faceProblem"].append({"name": i["CONTENT"], "data": []})
        elif i["LEVELNUM"] == "3":
            if i["END"] != None:
                isActive = 1
                relate = [i["END"]]
            else:
                isActive = 0
                relate = 0
            a = {"id": i["ID"], "data": {"name": i["CONTENT"] + ":" + i["VALUE"]}}
            if a not in leve2list:
                leve2list.append(a)
                leve3list.append({"id": i["ID"], "data": {"name": i["CONTENT"] + ":" + i["VALUE"], "isActive": isActive,
                                                          "relate": relate}})
            else:
                for ii in leve3list:
                    if ii["id"]==i["ID"]:
                        ii["data"]["relate"].append(i["END"])
        elif i["LEVELNUM"] == "4":
            if i["END"] != None:
                isActive = 1
                relate = i["END"]
            else:
                isActive = 0
                relate = 0
            searchData["problemAnalysis"].append(
                {"name": i["CONTENT"], "text": i["VALUE"], "isActive": isActive, "relate": relate})
        elif i["LEVELNUM"] == "5":
            searchData["suggest"] = i["VALUE"]

    for jj in leve3list:
        for j in idlist:
            if j["id"] in jj["id"]:
                for jjj in searchData["faceProblem"]:
                    if jjj["name"] == j["name"]:
                        jjj["data"].append(jj["data"])

    return searchData



# 九楼热线舆情大屏 智能舆情 舆情解读
def znyiyuqingjiedu_deal(data):
    res = {}
    ziti = []
    for i in data:
        A = request.args.get('z')
        i["A"]= A
        a = '本报告围绕“{A}”主题，对{B}至今热线收到市民反映的相关事件进行深入的挖掘分析。从近一个月舆情信息来看，共有事件相关信息{C}条，与上年同期对比{D}，其中咨询问题占{E}，诉求问题占{F}，最高舆情声量出现在{G}，共计{H}，占该段时间相关信息的{I}。事件涉及人群以{J}为主，市民较为关心的问题主要是{K}等。'.format(
            A=A ,B=i["B"], C=i["C"], D=i["D"], E=i["E"], F=i["F"], G=i["G"], H=i["H"], I=i["I"], J=i["J"], K=i["K"],
        )
        ziti.append(i["A"])
        ziti.append(i["B"])
        ziti.append(i["C"])
        ziti.append(i["D"])
        ziti.append(i["E"])
        ziti.append(i["F"])
        ziti.append(i["G"])
        ziti.append(i["H"])
        ziti.append(i["I"])
        ziti.append(i["J"])
        ziti.append(i["K"])
    res["content"] = a
    res["ziti"] = ziti

    return res

# 九楼热线运营大屏 员工画像
def yuangonghuaxiang_deal(data):
    res = {}
    textLeftData = []
    textRightData = []
    for i in data:
        lelist = [i["GENDER"], i["POLITIC_COUNTENANCE"], i["EDUCATIONAL_BACKGROUND"], i["AGE"], i["WORKING_YEAR"],
                  i["WORK_EXPERIENCE"], i["MARRIAGE_AND_BEARING"], i["CHARACTER"], i["WORK_MOTIVATION"]]
        leftstr = " ".join(lelist)
        textLeftData.append(leftstr)
        rilist = [i["HANDLING_EFFICIENCY"], i["DEGREE_OF_SATISFACTION"], i["AVAILABILITY"], i["CONTRIBUTION"],
                  i["QUALITY_AND_EFFICIENCY"], i["SKILLS_ENHANCEMENT"], i["PERFORMANCE"], i["GROUP_INFLUENCE"]]
        rightlist = []
        for j in rilist:
            if j != None:
                rightlist.append(j)
        if rightlist != []:
            rightstr = " ".join(rightlist)
            textRightData.append(rightstr)
    res["textLeftData"] = textLeftData
    res["textRightData"] = textRightData
    return res

# 九楼热线舆情大屏 智能舆情焦点关注
def znyqjiaodianguanzhu_deal(data):
    res = []
    lv1_list = []
    for i in data:
        if i["LV"] == 1 and i["LV"] not in lv1_list:
            lv1_list.append(i["S_TAG"])
            dic = {}
            dic["LV1"] = {"S_TAG": i["S_TAG"], "S_TAGNAME": i["S_TAGNAME"], "NUM": i["NUM"]}
            dic["LV2"] = []
            res.append(dic)
        elif i["LV"] == 2:
            for j in lv1_list:
                if j in str(i["S_TAG"]):
                    for jj in res:
                        if jj["LV1"]["S_TAG"] == j:
                            jj["LV2"].append({"S_TAG": i["S_TAG"], "S_TAGNAME": i["S_TAGNAME"], "NUM": i["NUM"]})

    return res


# 九楼热线舆情大屏 热度趋势
def yuqingreduqushi_deal(data):
    res = []
    for i in data:
        dic = {}
        dic["CREATE_TIME"] = i["CREATE_TIME"]
        dic["data"] = [{"热点问题": i["TOPIC"], "热度指数": i["IDX"]}]
        res.append(dic)

    return res

# 九楼热线舆情大屏 生命周期
def yqshengmingzhouqi_deal(data):
    res = []
    parentlevellist = []
    for i in data:
        if i["PARENTLEVEL"] not in parentlevellist:
            parentlevellist.append(i["PARENTLEVEL"])
            dic = {}
            dic["name"] = i["PARENTLEVEL"]
            dic["TUIJIANDU"] = i["TUIJIANDU"]
            dic["data1"] = [{"CLASSIFICATION": i["CLASSIFICATION"], "NUMBERS": i["NUMBERS"], "BAIFENBI": i["BAIFENBI"]}]
            dic["data2"] = [i["CONTENT"]]
            res.append(dic)
        else:
            for j in res:
                if j["name"] == i["PARENTLEVEL"]:
                    jj = {"CLASSIFICATION": i["CLASSIFICATION"], "NUMBERS": i["NUMBERS"], "BAIFENBI": i["BAIFENBI"]
                          }
                    if jj not in j["data1"]:
                        j["data1"].append(jj)
                    if i["CONTENT"] not in j["data2"]:
                        j["data2"].append(i["CONTENT"])

    return res
