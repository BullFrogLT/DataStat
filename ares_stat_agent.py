#!/usr/bin/env python
# -*- coding: utf8 -*-
# __author__ = tliu

import os
import time
import json
import urllib2
import datetime
from lib.common_lib import re_joint_dir_by_os, get_conf_pat


class NSConf:
    def __init__(self):
        ns_conf = re_joint_dir_by_os("conf|ns.ini")
        self.es_server_ip = get_conf_pat(ns_conf, "agent", "es_ip")
        self.es_server_port = get_conf_pat(ns_conf, "agent", "es_port")
        self.ares_log_path = get_conf_pat(ns_conf, "agent", "ares_log_path")
        self.server_ip = get_conf_pat(ns_conf, "server", "ip")
        self.server_port = get_conf_pat(ns_conf, "server", "port")


def get_num(day, file):
    get_list_command = """grep "ALLTABLECATEGORY" {FILE}""".format(FILE=file) + """ | sed -n '$p' | awk -F" " '{print $2,$3,$4}'"""

    result = os.popen(get_list_command).readline()

    # 0(87) 0(87) 0(0)，取后面的87
    totalcount = result.rstrip("\n").split(" ")[0].split("(")[1][:-1]
    sucCount = result.rstrip("\n").split(" ")[1].split("(")[1][:-1]
    failCount = result.rstrip("\n").split(" ")[2].split("(")[1][:-1]
    return [day, totalcount, sucCount, failCount, capture_time, today_month]


def stat_count(file_name_list):
    ares_data = {}
    r = []
    # 统计ares每日处理数据量，格式为 [('20170905', [0, 0]),('20170904', [0, 0])]
    for k in file_name_list.keys():
        if os.path.exists(file_name_list[k]):
            r.append(get_num(k, file_name_list[k]))
        else:
            r.append([k, 0, 0, 0, capture_time, today_month])
    ares_data['result_ares'] = r
    return ares_data


def get_log(ares_log_path):
    file_name_list_t = {}
    today = datetime.date.today()

    # 取未来三天时间
    for d in range(8):
        day = (today + datetime.timedelta(days=-d)).strftime("%Y%m%d")
        # 取当天日志文件
        if d == 0:
            # 取当日的最后一个mstatistic.log文件
            # 判断 mstatistic.log.当日.1文件是否存在：
            today_es_log_file = ares_log_path + "mstatistic.log." + (today + datetime.timedelta(days=-d)).strftime("%Y-%m-%d") + ".1"
            if os.path.exists(today_es_log_file):
                # 如果存在，则取最后一个
                get_last_log_cmd = """ls -l %smstatistic.log* | grep %s | sed -n '$p' | awk -F" " '{print $9}'""" % (ares_log_path, (today + datetime.timedelta(days=-d)).strftime("%Y-%m-%d"))
                file_name = os.popen(get_last_log_cmd).readline().rstrip("\n")
                file_name_list_t[day] = ares_log_path + file_name
            else:
                # 如果不存在，取 /home/nebula/NebulaPF_DataCenter_Ares/log/mstatistic.log
                file_name_list_t[day] = ares_log_path + "mstatistic.log"

        # 取历史文件
        else:
            # 久方法，已弃用
            # file_name = ares_log_path + "mstatistic.log." + (today + datetime.timedelta(days=-d)).strftime("%Y-%m-%d") + ".1"
            # file_name_list_t[day] = file_name

            # 最后一个日志文件生成时间是23:59
            grep_cmd = """ls -l %smstatistic.log* | grep %s | grep 23:59 | awk -F"/" '{print $6}'""" % (ares_log_path, (today + datetime.timedelta(days=-d)).strftime("%Y-%m-%d"))
            file_name = os.popen(grep_cmd).readline().rstrip("\n")
            if file_name == "":
                file_name_list_t[day] = ''
            else:
                file_name_list_t[day] = ares_log_path + file_name

    return file_name_list_t


def putaresdata(server_ip, server_port, ares_data):
    try:
        req = urllib2.Request("http://{IP}:{PORT}/updateares/".format(IP=server_ip, PORT=server_port), json.dumps(ares_data), {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        # response = f.readlines()
        # print response
        f.close()
    except Exception, e:
        print e


def main():
    apm = NSConf()

    file_name_list = get_log(apm.ares_log_path)

    ares_data = stat_count(file_name_list)
    # {'result_ares': [['20170829', 0, 0, 0, 1504592438, '20170905'], ['20170905', '8888', '6465', '6666', 1504592438, '20170905'], ['20170904', '4476', '4476', '0', 1504592438, '20170905'], ['20170903', '157', '157', '0', 1504592438, '20170905'], ['20170902', '24', '24', '0', 1504592438, '20170905'], ['20170901', '87', '87', '0', 1504592438, '20170905'], ['20170831', 0, 0, 0, 1504592438, '20170905'], ['20170830', 0, 0, 0, 1504592438, '20170905']]}
    print "ares_data:", ares_data
    putaresdata(apm.server_ip, apm.server_port, ares_data)


if __name__ == '__main__':
    capture_time = int(time.time())
    today_month = datetime.datetime.now().strftime("%Y%m%d")

    main()