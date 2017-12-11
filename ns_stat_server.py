#!/usr/bin/env python
# -*- coding: utf8 -*-
# __author__ = tliu

import os
import datetime
import time
import json
from lib.bottle import request, Bottle, view, run, static_file
from init_db import NSSTATDB
from lib.common_lib import re_joint_dir_by_os, get_conf_pat
from lib.stat_lib import stat_daytable_increment, statcrius_daytable_increment, statares_daytable_increment
from lib.stat_lib import statinterds_daytable_increment, stattornado_daytable_increment
from lib.alarm import alarm_for_ns
from lib.prostat_lib import statinterds_type_increment, stattornado_type_increment
from lib.prostat_lib import stattopic_type_increment, statcrius_type_increment, statares_type_increment


class NSSTATConf:
    def __init__(self):
        # 读取conf目录下的ns.ini文件
        ns_conf = re_joint_dir_by_os("conf|ns.ini")

        # server_ip = 172.16.5.43
        self.server_ip = get_conf_pat(ns_conf, "server", "ip")

        # server_port = 8081
        self.server_port = get_conf_pat(ns_conf, "server", "port")

        # 各模块协议名对应关系
        self.json_file = re_joint_dir_by_os("conf|meta_data.json")


app = Bottle()

db = NSSTATDB()

# 初始化数据库表
db.run_all_init_func()

# 加载css、js等
@app.route("/assets/<static_filename:re:.*\.css|.*\.js|.*\.png|.*\.jpg|.*\.gif>")
def server_assets(static_filename):
    """
    加载js、css、图片等资源
    """
    assets_path = "./assets"
    return static_file(filename=static_filename, root=assets_path)


@app.post('/updatees/')
def updatees():
    result_es = request.json
    try:
        for i in result_es['result_es'].keys():
            # str(i) 表示表名，str型
            # result_es['result_es'][str(i)]['CAPTURETIME']  表示CAPTURETIME，int型
            # print str(i)
            # print type(i)
            # print result_es['result_es'][str(i)]['CAPTURETIME'], type(result_es['result_es'][str(i)]['CAPTURETIME'])
            # print result_es['result_es'][str(i)]['TABLENUM'], type(result_es['result_es'][str(i)]['TABLENUM'])
            # print result_es['result_es'][str(i)]['TABLESIZE']

            insert_es_sql = "INSERT INTO " \
                              "ns_stat_es (TABLENAME, TABLENUM, CAPTURETIME, TABLESIZE, DATE)" \
                              "VALUES ('%s', '%s', '%s', '%s', '%s')" % \
                              (str(i), result_es['result_es'][str(i)]['TABLENUM'], result_es['result_es'][str(i)]['CAPTURETIME'], result_es['result_es'][str(i)]['TABLESIZE'], result_es['result_es'][str(i)]['DATE'])
            db.cur.execute(insert_es_sql)
        # print insert_es_sql

        db.conn.commit()
    except Exception, e:
        print e


@app.post('/updateares_type/')
def updateares_type():
    result_ares = request.json
    print result_ares
    result_list = result_ares.values()

    try:
        for i in result_list:
            # print "i", i
            for ii in i:
                for table_data in ii:
                    insert_crius_sql = "INSERT INTO " \
                                       "ns_stat_ares_type (STATTIME, TABLECATEGORY, TOTALCOUNT, SUCCOUNT, FAILCOUNT, STORESIZE, CAPTURETIME, DATE) " \
                                       "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                                       (table_data[0], table_data[1], table_data[2], table_data[3], table_data[4], table_data[5], table_data[6], table_data[7])
                    print insert_crius_sql
                    db.cur.execute(insert_crius_sql)
        db.conn.commit()
    except Exception, e:
        print e


@app.post('/updateares/')
def updateares():
    result_ares = request.json
    result_list = result_ares.values()[0]

    try:
        for table_data in result_list:
            insert_crius_sql = "INSERT INTO " \
                               "ns_stat_ares (STATTIME, TOTALCOUNT, SUCCOUNT, FAILCOUNT, CAPTURETIME, DATE) " \
                               "VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % \
                               (table_data[0], table_data[1], table_data[2], table_data[3], table_data[4], table_data[5])
            db.cur.execute(insert_crius_sql)
        db.conn.commit()
    except Exception, e:
        print e


@app.post('/updatecrius/')
def updatecrius():
    result_cirus = request.json

    # 取字典中的capture_time 1503046469
    capture_time = result_cirus.values()[0][-2]      # int

    # 取字典中的date 20170818
    date = str(result_cirus.values()[0][-1])

    result_list = result_cirus.values()[0][:-2]
    # print "result_list:", result_list
    try:
        for table_data in result_list:
            # print table_data,
            insert_crius_sql = "INSERT INTO " \
                               "ns_stat_crius (IMPORT_DATE, TABLE_CATEGORY, SUCCESS_COUNT, CAPTURETIME, FAILED_COUNT, LOADTYPE, DATE) " \
                               "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                               (table_data[0], table_data[1].rstrip("\t"), table_data[2], capture_time, table_data[3], table_data[4], date)
            # print insert_crius_sql
            # print insert_crius_sql

            db.cur.execute(insert_crius_sql)
        db.conn.commit()
    except Exception, e:
        print e


@app.post('/updatetop/')
def updatetop():
    result_top = request.json
    result_list_tmp = result_top.values()
    result_list = result_list_tmp[0]

    try:
        for top_data in result_list:
            # print "TABLENAME:", top_data[0]
            # print "TABLENUM:", top_data[1]
            # print "CAPTURETIME:", top_data[2]
            # print "DATE:", top_data[3]
            # print
            # print

            # print top_data,
            insert_top_sql = "INSERT INTO " \
                             "ns_stat_top (TABLENAME, TABLENUM, CAPTURETIME, DATE) " \
                             "VALUES ('%s', '%s', '%s', '%s')" % \
                             (top_data[0], top_data[1], top_data[2], top_data[3])
            # print "insert:", insert_top_sql
            db.cur.execute(insert_top_sql)
        db.conn.commit()
        # return result_list
    except Exception, e:
        print e

@app.post('/updateinterds_type/')
def updateinterds_type():
    result_interds = request.json

    result_list_tmp = result_interds.values()
    # print "result_list_tmp", result_list_tmp
    result_list = result_list_tmp[0]
    print result_list

    # result_list_tmp[0][0] 协议
    # result_list[0] list第一条数据
    # print "result_list[0]", result_list[0]

    try:
        for interds_data in result_list:

            insert_interds_sql = "INSERT INTO " \
                             "ns_stat_interds_type (DATASOURCE, DATATYPE, READNUM, RESULTNUM, CONDROPNUM, OUTPUTTYPE, OUTSUCCNUM, OUTFAILEDNUM, OUTDROPNUM, CAPTURETIME, DATE) " \
                             "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                             (interds_data[0], interds_data[1], interds_data[2], interds_data[3], interds_data[4], interds_data[5], interds_data[6], interds_data[7], interds_data[8], interds_data[9], interds_data[10])
            # print "insert:", insert_interds_sql
            db.cur.execute(insert_interds_sql)
        db.conn.commit()
    #     # return result_list
    except Exception, e:
        print e


@app.post('/updateinterds/')
def updateinterds():
    result_interds = request.json

    result_list_tmp = result_interds.values()
    # print "result_list_tmp", result_list_tmp
    result_list = result_list_tmp[0]
    print result_list

    # result_list_tmp[0][0] 协议
    # result_list[0] list第一条数据
    # print "result_list[0]", result_list[0]

    try:
        for interds_data in result_list:

            insert_interds_sql = "INSERT INTO " \
                             "ns_stat_interds (DATATYPE, READNUM, RESULTNUM, CONDROPNUM, OUTSUCCNUM, OUTFAILEDNUM, OUTDROPNUM, CAPTURETIME, DATE) " \
                             "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                             (interds_data[0], interds_data[1], interds_data[2], interds_data[3], interds_data[4], interds_data[5], interds_data[6], interds_data[7], interds_data[8])
            # print "insert:", insert_interds_sql
            db.cur.execute(insert_interds_sql)
        db.conn.commit()
    #     # return result_list
    except Exception, e:
        print e


@app.post('/updatetornado_type/')
def updatetornado_type():
    result_tornado = request.json
    print "result_tornado:", result_tornado

    try:
        for tornado_data in result_tornado:
            insert_interds_sql = "INSERT INTO " \
                             "ns_stat_tornado_type (CITY, DATASOURCE, DATATYPE, DATAFLAG, REC_TOTAL, MAKE_TOTAL, LEGA_TOTAL, SUC_NUM, FAILED_NUM, DROP_NUM, AVA_SIZE, OUTPUTKAFKA, STATTIME, CAPTURETIME, DATE) " \
                             "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                             (str(tornado_data[0]), str(tornado_data[1]), str(tornado_data[2]), str(tornado_data[3]),
                              str(tornado_data[4]), str(tornado_data[5]), str(tornado_data[6]), str(tornado_data[7]),
                              str(tornado_data[8]), str(tornado_data[9]), str(tornado_data[10]), str(tornado_data[11]),
                              str(tornado_data[12]), str(tornado_data[13]), str(tornado_data[14]))
            # print "insert:", insert_interds_sql
            db.cur.execute(insert_interds_sql)
        db.conn.commit()
    except Exception, e:
        print e


@app.post('/updatetornado/')
def updatetornado():
    result_tornado = request.json
    result_list_tmp = result_tornado.values()
    # print "result_list_tmp", result_list_tmp
    result_list = result_list_tmp[0]

    try:
        for tornado_data in result_list:

            insert_interds_sql = "INSERT INTO " \
                             "ns_stat_tornado (STATTIME, REC_TOTL, SUC_NUM, FAILED_NUM, TOKFK_TOTAL, TOKFK_SUC, TOKFK_FAILED, CAPTURETIME, DATE) " \
                             "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                             (tornado_data[0], tornado_data[1], tornado_data[2], tornado_data[3], tornado_data[4], tornado_data[5], tornado_data[6], tornado_data[7], tornado_data[8])
            # print "insert:", insert_interds_sql
            db.cur.execute(insert_interds_sql)
        db.conn.commit()
    #     # return result_list
    except Exception, e:
        print e


# @app.route('/', method="GET")
# def index():
#     return "<h1>aaaa</h1>"


@app.route('/protocol/', method='GET')
@view("protocol")
def protocol():
    # 正常代码
    # 取json数据
    today = datetime.datetime.now().strftime("%Y%m%d")      # 今天时间，年与日格式

    a_time = 7
    interds_s = statinterds_type_increment()
    tornado_s = stattornado_type_increment()
    topic_s = stattopic_type_increment()
    crius_s = statcrius_type_increment()
    ares_s = statares_type_increment()

    j_data = json.loads(open(ns.json_file).read())

    print j_data, type(j_data)

    # 取json中key，就是取唯一的协议名，返回列表
    pro_name = j_data.keys()


    # 需要返回给界面所有数据，变量data {}
    result = {}     # result['data'] = [interds/tornado]


# {'CRIUS': {'20171113': [0, 0], '20171112': [0, 0], '20171111
# {'表名': {'20171117'}: [interds, tornado, topic, crius, ares]
# {'表名': {'20171117': [interdsREADNUM, interdsOUTSUCCNUM, tornado, topic, crius, ares], '20171116': [....]

    # 对每个协议进行遍历
    data_pro = {}
    for p in pro_name:
        print "表名：", p
        # print "lien:", j_data[p]['INTERDS'], len(j_data[p]['INTERDS'])
        # 界面中需要展示的协议名称，即json数据中的TABLENAME
        # print "TABLENAME:", j_data[p]['TABLENAME']

        # 每个协议对应7天的、interds、tornadao等的数据标量
        pro_data = {}
        # 按时间进行遍历，通过sql查找sqlite库中近7天的数据量
        for i in range(a_time):
            list_tmp = []     # 这里是添加表名，需要放到最外层
            # list_tmp.append(p)
            today_i = datetime.date.today() + datetime.timedelta(days=-i)   # 当日 20171117
            day_i = ''.join(str(today_i).split('-'))

            # 1.查找interds数据readnum,outsuccnum：
            for filed in ['READNUM', 'OUTSUCCNUM']:
                # for _num in len() j_data[p]['INTERDS']

                # 针对interds多个协议名对应一张表做处理
                j_data_sum = 0
                # print "j_data[p]['INTERDS']:", j_data[p]['INTERDS']
                for j_t in j_data[p]['INTERDS']:
                    tmp_s = interds_s.stat_interds_type(filed, day_i, j_t, j_data[p]['OUTTYPE'])
                    j_data_sum = j_data_sum + tmp_s
                list_tmp.append(j_data_sum)
            # print list_tmp      # [u'NB_APP_SHM_LGZSRYXX', 2200, 1100]

            # 2.查找tornado数据readnum,outsuccnum：
            for filed in ['REC_TOTAL', 'SUC_NUM']:
                tmp_s = tornado_s.stat_tornado_type(filed, day_i, j_data[p]['TORNADO'])
                list_tmp.append(tmp_s)
            # print "list_tmp:::", list_tmp       # list_tmp::: [2200, 1100, 3000, 300]

            # 3.查找topic数据：
            tmp_s = topic_s.stat_topic_type('TABLENUM', today, day_i, j_data[p]['TOPIC'])
            list_tmp.append(tmp_s)

            # 4.查找crius
            for field in ['SUCCESS_COUNT', 'FAILED_COUNT']:
                tmp_c = crius_s.stat_crius_type(field, today, today_i, j_data[p]['CRIUS'], day_i)
                list_tmp.append(tmp_c)

            # 5.查找ares
            for field in ['TOTALCOUNT', 'SUCCOUNT']:
                tmp_a = ares_s.stat_ares_type(field, day_i, j_data[p]['ARES'])
                list_tmp.append(tmp_a)




            print "list_tmp:::", list_tmp
            # interds_s.stat_interds_readnum()
            pro_data[day_i] = list_tmp
            print "prooo:", pro_data
        data_pro[str(p)] = pro_data
    result['PRO'] = data_pro
    print "result:", result

    return result


@app.route('/ares/', method='GET')
@view("ares")
def ares():
    try:
        result = {}
        ai = statares_daytable_increment()
        a_time = 7
        ares_data = {}
        for i in range(a_time):
            list_tmp = []
            today_a = datetime.date.today() + datetime.timedelta(days=-i)
            day_a = ''.join(str(today_a).split('-'))        # 当日 20170905
            for field in ['TOTALCOUNT', 'SUCCOUNT', 'FAILCOUNT']:
                list_tmp.append(ai.stat_ares_readnum(day_a, field))
            ares_data[day_a] = list_tmp
            # print ares_data
        result['ARES'] = ares_data
        return result
    except Exception, e:
        print "ARES统计出错", e

@app.route('/', method='GET')
@app.route('/alarm/', method='GET')
@view("alarm")
def alarm():

    today = datetime.datetime.now().strftime("%Y%m%d")      # 今天日期，格式为 20170913
    day_e = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y%m%d")     # 昨日日期，格式为 20170912
    first_day = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y%m%d")     # 昨日日期，格式为 20170912

    today_d = datetime.date.today() + datetime.timedelta(days=0)
    first_time = int(time.mktime(today_d.timetuple()))
    last_time = int(time.mktime(today_d.timetuple()) + 86399)


    # 统计预警模块
    result_alarm = {}
    try:
        # 1001:监测interds全部接受数据量是否为0
        alarm = alarm_for_ns().init_db_today_interds_readnum_count(today)
        result_alarm['INTERDS_READNUM_TODAY_ALARM'] = alarm

        # 1002:监测interds正确处理的数据量是否为0
        alarm = alarm_for_ns().init_db_today_interds_resultnum_count(today)
        result_alarm['INTERDS_RESULTNUM_TODAY_ALARM'] = alarm

        # 1003:监测tornado接受总量是否为0
        alarm = alarm_for_ns().init_db_today_tornado_rectotl_count(today)
        result_alarm['TORNADO_RECTOTL_TODAY_ALARM'] = alarm

        # 1004:监测tornado业务输出KFK成功条数是否为0
        alarm = alarm_for_ns().init_db_today_tornado_tokfksuc_count(today)
        result_alarm['TORNADO_TOKFKSUC_TODAY_ALARM'] = alarm

        # 1005:监测topic当日数据量是否为0
        alarm = alarm_for_ns().init_db_today_topic_tablenum_count(today)
        result_alarm['TOPIC_TABLENUM_TODAY_ALARM'] = alarm

        # 1006:监测crius处理成功数据量是否为0
        alarm = alarm_for_ns().init_db_today_crius_successcount_count(today, first_time, last_time)
        result_alarm['CRIUS_SUCCESSCOUNT_TODAY_ALARM'] = alarm

        # 1007:监测ares处理成功数据量是否为0
        alarm = alarm_for_ns().init_db_today_ares_totalcount_count(today)
        result_alarm['ARES_TOTALCOUNT_TODAY_ALARM'] = alarm

        # 1008:监测ES数据量是否为0
        alarm = alarm_for_ns().init_db_today_es_totalcount_count(today, first_day)
        result_alarm['ES_TABLENUM_TODAY_ALARM'] = alarm

        # 3001:INTERDS解析_成功输出数据量-TORNADO_接受总量!=0
        alarm = alarm_for_ns().init_db_tornado_3001_alarm(today)
        result_alarm['TORNADO_3001_ALARM'] = alarm

        # 4001:TORNADO_业务输出KAFKA成功条数-TOPIC数据量统计!=0
        alarm = alarm_for_ns().init_db_topic_4001_alarm(today)
        result_alarm['TOPIC_4001_ALARM'] = alarm

        # 2001:INTERDS解析,总共丢弃的数据量/接收数据量>5%
        alarm = alarm_for_ns().init_db_interds_2001_alarm(today)
        result_alarm['INTERDS_2001_ALARM'] = alarm

        # 2002:INTERDS解析,输出失败/正确处理>5%
        alarm = alarm_for_ns().init_db_interds_2002_alarm(today)
        result_alarm['INTERDS_2002_ALARM'] = alarm

        # 2003:INTERDS解析,丢弃数据量/接收数据量>5%
        alarm = alarm_for_ns().init_db_interds_2003_alarm(today)
        result_alarm['INTERDS_2003_ALARM'] = alarm

        # 3002:TORNADO解析失败处理量/接收量>5%
        alarm = alarm_for_ns().init_db_tornado_3002_alarm(today)
        result_alarm['TORNADO_3002_ALARM'] = alarm

        # 3003:KFK输出失败/KFK业务处理>5%
        alarm = alarm_for_ns().init_db_tornado_3003_alarm(today)
        result_alarm['TORNADO_3003_ALARM'] = alarm

        # 3004:Tornado输出kafka数据量/Tornado接收数据量<90%
        alarm = alarm_for_ns().init_db_tornado_3004_alarm(today)
        result_alarm['TORNADO_3004_ALARM'] = alarm

        # 4002:|(昨天数据量-近七天平均数据量)|/近七天平均数据量>5%
        alarm = alarm_for_ns().init_db_topic_4002_alarm()
        result_alarm['TOPIC_4002_ALARM'] = alarm

        # 6001:ARES当天处理数据总量 < (TOPIC数据量统计 * 0.05)
        alarm = alarm_for_ns().init_db_ares_6001_alarm(today)
        result_alarm['ARES_6001_ALARM'] = alarm

        # 6002:处理失败数据量/处理数据总量 > 5%
        alarm = alarm_for_ns().init_db_ares_6002_alarm(today)
        result_alarm['ARES_6002_ALARM'] = alarm

        print "result_alarm:", result_alarm
    except Exception, e:
        print e

    # ----------------------------------------------------------------------------------------------------------
    # 统计 TORNADO 当天数据量是否为0

    return result_alarm


@app.route('/index/', method='GET')
@view("index")
def index():
    # result:{es_data:{}, crius:{}}
    result = {}
    try:
        '''
        # 查找数据库中近7天ES数据量
        t_time = 8
        # es_data:{20170818:1000, 20170819:2000}
        es_data = {}
        for i in range(t_time):
            day_e = (datetime.date.today() + datetime.timedelta(days=-i)).strftime("%Y%m%d")
            # print day, type(day)
            day_es = "SELECT sum(TABLENUM) " \
                     "FROM ns_stat_ares " \
                     "where DATE = '{DAY}' " \
                     "AND CAPTURETIME = ( " \
                     "SELECT MAX(CAPTURETIME) " \
                     "FROM ns_stat_ares " \
                     "WHERE DATE = '{DAY}' " \
                     ")".format(DAY=day_e)
            db.cur.execute(day_es)
            es_num = db.cur.fetchall()[0][0]
            if es_num is None:
                es_num = 0
            es_data[day_e] = es_num
            # print es_data
            #  {'20170816': 1245, '20170819': 97202, '20170815': 1010, '20170817': 2040, '20170818': 2583, '20170820': 0, '20170821': 11037545, '20170822': 14807028}
        result['ES'] = es_data

        '''
        # ----------------------------------------------------------------------------------------------------------
        # 查找数据库中近7天ES数据量
        st = stat_daytable_increment()
        t_time = 7
        es_data = {}
        # 查找数据库中近7天，天表数据增量
        # 天表增量： 找出每天的天表数据量，可以算作每天的增量


        for i in range(t_time):
            # 当天年月日
            table_name = (datetime.date.today() + datetime.timedelta(days=-i)).strftime("%Y%m%d")
            first_day = (datetime.date.today() + datetime.timedelta(days=-i - 1)).strftime("%Y%m%d")

            # 天表增量
            day_table_increment = st.today_stat(table_name)

            # {'20170816': 3972601, '20170819': 0, '20170817': 133, '20170818': 135310, '20170820': 0, '20170821': 6365790, '20170822': 0}

            # 月表增量
            month_table_increment = st.month_stat(table_name, first_day)

            # 总表增量
            total_table_inceement = st.total_stat(table_name, first_day)

            # 增量的和
            total_tmp = day_table_increment + month_table_increment + total_table_inceement
            es_data[table_name] = total_tmp
        result['ES'] = es_data
    except Exception, e:
        print "ES统计出错", e

    try:
        # ----------------------------------------------------------------------------------------------------------
        # 查找数据库中近7天TOPIC数据量
        top_time = 7
        topic_data = {}
        today_topic = datetime.datetime.now().strftime("%Y%m%d")
        for i in range(top_time):
            day_t = (datetime.date.today() + datetime.timedelta(days=-i)).strftime("%Y%m%d")
            day_topic = "SELECT sum(TABLENUM) " \
                        "FROM ns_stat_top " \
                        "where DATE = '{TODAY}' " \
                        "AND TABLENAME like '%{DAY}%' " \
                        "AND CAPTURETIME = ( " \
                        "SELECT MAX(CAPTURETIME) " \
                        "FROM ns_stat_top " \
                        "WHERE DATE = '{TODAY}' " \
                        ")".format(DAY=day_t, TODAY=today_topic)

            db.cur.execute(day_topic)
            topic_num = db.cur.fetchall()[0][0]
            if topic_num is None:
                topic_num = 0
            topic_data[day_t] = topic_num
            result['TOPIC'] = topic_data
    except Exception, e:
        print "TOPIC统计出错", e

        # ----------------------------------------------------------------------------------------------------------
        # 查询数据库中crius入库数据量
        # 查找数据库中近7天crius数据量
        # 如果界面中近7天都没数据，说明数据库表中没有今天的统计结果

    try:
        sc = statcrius_daytable_increment()
        c_time = 7
        crius_data = {}
        # 统计日期DATE，保持不变
        today_crius = datetime.datetime.now().strftime("%Y%m%d")
        for i in range(c_time):
            list_tmp = []
            today_c = datetime.date.today() + datetime.timedelta(days=-i)  # 当日 20170822
            day_c = ''.join(str(today_c).split('-'))
            for field in ['SUCCESS_COUNT', 'FAILED_COUNT']:
                list_tmp.append(sc.stat_crius(today_c, today_crius, field))

            crius_data[day_c] = list_tmp
        result['CRIUS'] = crius_data
    except Exception, e:
        print "CRIUS统计出错", e


        # ----------------------------------------------------------------------------------------------------------
        # 查询数据库中ares入库数据量
    try:
        ai = statares_daytable_increment()
        a_time = 7
        ares_data = {}
        for i in range(a_time):
            list_tmp = []
            today_a = datetime.date.today() + datetime.timedelta(days=-i)
            day_a = ''.join(str(today_a).split('-'))        # 当日 20170905
            for field in ['TOTALCOUNT', 'SUCCOUNT', 'FAILCOUNT']:
                list_tmp.append(ai.stat_ares_readnum(day_a, field))
            ares_data[day_a] = list_tmp
            # print ares_data
        result['ARES'] = ares_data
    except Exception, e:
        print "ARES统计出错", e

        # ----------------------------------------------------------------------------------------------------------
        # 查询数据库中inter_ds入库数据量
    try:
        si = statinterds_daytable_increment()
        i_time = 7
        interds_data = {}
        # 统计日期DATE，保持不变
        for i in range(i_time):
            list_tmp = []
            today_i = datetime.date.today() + datetime.timedelta(days=-i)  # 当日 20170822
            day_i = ''.join(str(today_i).split('-'))
            for field in ['READNUM', 'RESULTNUM', 'CONDROPNUM', 'OUTSUCCNUM', 'OUTFAILEDNUM', 'OUTDROPNUM']:
                list_tmp.append(si.stat_interds_readnum(day_i, field))

            interds_data[day_i] = list_tmp
        result['INTERDS'] = interds_data
        print "result1:", result
    except Exception, e:
        print "INTERDS统计出错", e

        # ----------------------------------------------------------------------------------------------------------
        # 查询数据库中tornado入库数据量
    try:
        stk = stattornado_daytable_increment()
        tt_time = 7
        tornado_data = {}
        for i in range(tt_time):
            list_tmp = []
            today_tt = datetime.date.today() + datetime.timedelta(days=-i)  # 当日 20170822
            day_tt = ''.join(str(today_tt).split('-'))
            for field in ['REC_TOTL', 'SUC_NUM', 'FAILED_NUM', 'TOKFK_TOTAL', 'TOKFK_SUC', 'TOKFK_FAILED']:
                list_tmp.append(stk.stat_tornado_readnum(day_tt, field))

            tornado_data[day_tt] = list_tmp
            # print "tornado_data:", tornado_data
        result['TORNADO'] = tornado_data
        # ----------------------------------------------------------------------------------------------------------
        return result
    except Exception, e:
        print "tornado统计出错", e





if __name__ == '__main__':
    ns = NSSTATConf()



    run(app, host="0.0.0.0", port=ns.server_port, debug=True)