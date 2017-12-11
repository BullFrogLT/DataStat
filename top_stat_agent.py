#!/usr/bin/env python
# -*- coding: utf8 -*-
# __author__ = tliu

import os
import time
import datetime
import urllib2
import json
from lib.common_lib_nooracle import re_joint_dir_by_os, get_conf_pat


class NSConf:
    def __init__(self):
        ns_conf = re_joint_dir_by_os("conf|ns.ini")
        self.server_ip = get_conf_pat(ns_conf, "server", "ip")
        self.server_port = get_conf_pat(ns_conf, "server", "port")
        self.crius_tool_path = get_conf_pat(ns_conf, "hadoop", 'crius_tool_path')
        self.crius_tool_name = get_conf_pat(ns_conf, "hadoop", 'crius_tool_name')


def get_Topstat_data(toolpath, toolname):
    command = "cd {A}; sh {B} default true".format(A=toolpath, B=toolname)
    crius_data = os.popen(command).readlines()
    return crius_data


def putTopData(server_ip, server_port, top_data):
    try:
        req = urllib2.Request("http://{IP}:{PORT}/updatetop/".format(IP=server_ip, PORT=server_port), json.dumps(top_data), {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        # response = f.readlines()
        # print response
        f.close()
    except Exception, e:
        print e


def getTableNameCount(data_tmp):
    capture_time = int(time.time())
    today_month = datetime.datetime.now().strftime("%Y%m%d")

    top_data = {}
    r = []
    for d in data_tmp:
        r_tmp = []
        if 'topicName' in d:
            tablename_tmp = d.split(" ")[6]
            count_tmp = d.split(" ")[8].rstrip("\n")

            r_tmp.append(tablename_tmp)
            r_tmp.append(count_tmp)
            r_tmp.append(capture_time)
            r_tmp.append(today_month)

            r.append(r_tmp)
    top_data['result_top'] = r
    print
    # print "top_data : ", top_data
    return top_data

def main():
    apm = NSConf()


    # 依赖crius统计脚本，判断检测脚本是否存在
    _path = apm.crius_tool_path
    _toolname = apm.crius_tool_name

    data = get_Topstat_data(_path, _toolname)

    top_data = getTableNameCount(data)

    putTopData(apm.server_ip, apm.server_port, top_data)


if __name__ == '__main__':
    main()

