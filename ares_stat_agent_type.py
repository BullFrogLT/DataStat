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
    rt = []
    print "day:", day, "file", file

    get_list_command = """cat {FILE}""".format(FILE=file) + """ |grep "speed is 0 line/s" -n | tail -n 2"""

    # 取日志中 speed is 0 line/s 中间的日志
    # 找到speed is 0 line/s 的倒数第二行、倒数第一行
    result = os.popen(get_list_command).readlines()     # ['41555:speed is 0 line/s\n', '41584:speed is 0 line/s\n']
    first_line = result[0].split(":")[0]        # 41555
    last_line = result[1].split(":")[0]

    # 取两行中间的数据
    get_data = """sed -n '{A},{B}p' {FILE} | sed '1,5d' | sed '$d' | sed '$d'""".format(A=first_line, B=last_line, FILE=file)

    result_d = os.popen(get_data).read()
    # result_d = filter(lambda x: x != '\n', result_d)        # 需要过滤
    for r in result_d.split("\n"):
        # r 打印每行，例如 NB_APP_AUTH              0(0)                     0(0)                     0(0)                     0(0)
        tmp = filter(lambda x: x != '\n', ','.join(filter(lambda x: x, r.split(' '))))      # NB_APP_AUTH,111110(111110),222220(2222220),333330(33333330),1231230(4444440)
        # 过滤列表中的空行

        if 0 != len(tmp):
            line_data = tmp.split(",")
            # line_data = filter(lambda x: x != '', line_data)
            # print "len:", len(line_data)
            # print "line:::", line_data, type(line_data)  # ['NB_APP_AUTH', '0(0)', '0(0)', '0(0)', '0(0)']
            if 0 != len(line_data) or line_data != ['']:
                TABLECATEGORY = line_data[0]
                TOTALCOUNT = line_data[1].split("(")[1][:-1]
                SUCCOUNT = line_data[2].split("(")[1][:-1]
                FAILCOUNT = line_data[3].split("(")[1][:-1]
                STORESIZE = line_data[4].split("(")[1][:-1]
                rt.append([day, TABLECATEGORY, TOTALCOUNT, SUCCOUNT, FAILCOUNT, STORESIZE, capture_time, today_month])
    return rt


def stat_count(file_name_list):
    ares_data = {}
    r = []
    # 统计ares每日处理数据量，格式为 [('20170905', [0, 0]),('20170904', [0, 0])]
    for k in file_name_list.keys():
        if os.path.exists(file_name_list[k]):
            # print "filename:", file_name_list[k]
            r.append(get_num(k, file_name_list[k]))
        else:
            r.append([[k, '', 0, 0, 0, '', capture_time, today_month]])
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
        req = urllib2.Request("http://{IP}:{PORT}/updateares_type/".format(IP=server_ip, PORT=server_port), json.dumps(ares_data), {'Content-Type': 'application/json'})
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

    print "ares_data:", ares_data
    putaresdata(apm.server_ip, apm.server_port, ares_data)


if __name__ == '__main__':
    capture_time = int(time.time())
    today_month = datetime.datetime.now().strftime("%Y%m%d")

    main()