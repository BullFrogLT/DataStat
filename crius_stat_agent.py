#!/usr/bin/env python
# -*- coding: utf8 -*-
# __author__ = tliu

import time
from lib.common_lib import re_joint_dir_by_os, get_conf_pat
from lib.common_ora import OperateOracle
import urllib2
import json
import datetime


class NSConf:
    def __init__(self):
        ns_conf = re_joint_dir_by_os("conf|ns.ini")
        self.BGDB_IP = get_conf_pat(ns_conf, "crius", "BGDB_IP")
        self.BGDB_USERNAME = get_conf_pat(ns_conf, "crius", "BGDB_USERNAME")
        self.BGDB_PASSWORD = get_conf_pat(ns_conf, "crius", "BGDB_PASSWORD")
        self.server_ip = get_conf_pat(ns_conf, "server", "ip")
        self.server_port = get_conf_pat(ns_conf, "server", "port")

def get_db_data(USERNAME, PASSWORD, IP):
    oracon = '{USER}/{PWD}@{IP}:1521/ora11g'.format(USER=USERNAME, PWD=PASSWORD, IP=IP)
    con_bigdata = OperateOracle(oracon)

    capture_time = int(time.time())
    today_month = datetime.datetime.now().strftime("%Y%m%d")

    # 今天是20170822
    t1 = time.mktime(time.strptime(time.strftime('%Y-%m-%d 00:00:00', time.localtime(time.time())), '%Y-%m-%d %H:%M:%S'))
    # 取6天前0点的绝对秒 1502812800
    starttime = int(t1 - 518400)
    # 取当天23:59:59的绝对秒  1503417599
    endtime = int(t1 + 86399)

    # 取近7天的所有数据
    sql = """
    select * from NB_DATA_IMPORT_STAT
        where IMPORT_DATE between {A} and {B}
        and LOADTYPE = 'hdfs_rtload'
    """.format(A=starttime, B=endtime)

    try:
        crius_data = {}
        con_bigdata.curs.execute(sql)
        query_res = con_bigdata.curs.fetchall()
        # 如果当天crius没有将统计数据入bigdata库，则返回的crius_data['result_crius']数据只有2个字段
        # crius_data: {'result_crius': [1505897669, '20170920']}
        query_res.append(capture_time)
        query_res.append(today_month)
        # print "query_res type is :", type(query_res)
        crius_data['result_crius'] = query_res
        return crius_data

    except Exception, e:
        print e


def putcriusdata(server_ip, server_port, crius_data):
    try:
        req = urllib2.Request("http://{IP}:{PORT}/updatecrius/".format(IP=server_ip, PORT=server_port), json.dumps(crius_data), {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        # response = f.readlines()
        # print response
        f.close()
    except Exception, e:
        print e


def main():
    """
        crius程序每间隔1200秒往oracle中插入统计数据，本程序1小时运行一次，数据量统计会有延迟
    """
    apm = NSConf()

    # 取bigdata库中crius入库数据
    # get_db_data(apm.BGDB_USERNAME, apm.BGDB_PASSWORD, apm.BGDB_IP)
    crius_data = get_db_data(apm.BGDB_USERNAME, apm.BGDB_PASSWORD, apm.BGDB_IP)

    # 将数据写入 sqlite3
    putcriusdata(apm.server_ip, apm.server_port, crius_data)


if __name__ == '__main__':
    '''
    统计Crius当日处理数据，将数据入库
    '''
    main()