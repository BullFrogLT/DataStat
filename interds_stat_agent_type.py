#!/usr/bin/env python
# -*- coding: utf8 -*-
# __author__ = tliu


from lib.common_lib_nooracle import re_joint_dir_by_os, get_conf_pat, get_files_path
import time
import json
import urllib2
import datetime
import os


class NSConf:
    def __init__(self):
        ns_conf = re_joint_dir_by_os("conf|ns.ini")
        self.server_ip = get_conf_pat(ns_conf, "server", "ip")
        self.server_port = get_conf_pat(ns_conf, "server", "port")


def get_interds_stat(dsfile, capture_time_t, today_month_t):
    interds_data = {}

    with open(dsfile, 'r') as f:
        data_tmp = f.readlines()
        r = []

        for d in data_tmp[3:-2]:
            a = []
            tmp = filter(lambda x: x != '\n', ','.join(filter(lambda x: x, d.split(' '))))
            aa = tmp.split(',')
            # print "aaa:", aa
            if [''] != aa and ['\r'] != aa:
                DATASOURCE = aa[0]      # 新增
                DATATYPE = aa[1]

                ReadNum = aa[2]
                ResultNum = aa[3]
                ConDropNum = aa[4]
                OutPutType = aa[5]       # 新增
                OutSuccNum = aa[6]
                OutFailedNum = aa[7]
                OutDropNum = aa[8]
                a.append(DATASOURCE)
                a.append(DATATYPE)
                a.append(ReadNum)
                a.append(ResultNum)
                a.append(ConDropNum)
                a.append(OutPutType)
                a.append(OutSuccNum)
                a.append(OutFailedNum)
                a.append(OutDropNum)
                a.append(capture_time_t)
                a.append(today_month_t)
                r.append(a)
    interds_data['result_interds'] = r
    print interds_data
    return interds_data

def put_interds_data(server_ip, server_port, interds_data):
    try:
        req = urllib2.Request("http://{IP}:{PORT}/updateinterds_type/".format(IP=server_ip, PORT=server_port), json.dumps(interds_data), {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        # response = f.readlines()
        # print response
        f.close()
    except Exception, e:
        print e


def main():
    apm = NSConf()

    # 删除结果目录中的历史
    path = '/home/NebulaSolarStat/'
    out_path = path + 'DSRunStat/out/'

    rm_com = "source /etc/profile;rm -rf {A}*".format(A=out_path)
    os.system(rm_com)

    # capture_time-1800,因为程序在当前小时第2分钟运行程序，处理的是上一个小时数据，
    # 所以capture_time需要配置为上一小时时间，1800为半小时，为确保capturetime为最大值，如果修改此工具执行周期，需要修改1800的值
    capture_time = int(time.time()) - 1800

    now_time = datetime.datetime.now()

    b1 = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:00:00")
    b2 = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:59:59")

    if int(str(now_time).split(" ")[1][0:2]) == 00:
        today_month = (now_time + datetime.timedelta(days=-1)).strftime("%Y%m%d")
        print "today_month:1:", today_month
    else:
        today_month = (now_time + datetime.timedelta()).strftime("%Y%m%d")
        print "today_month:2:", today_month


    # 执行脚本工具，检测一小时内中的数据
    # a = time.localtime(time.time())
    # b1 = time.strftime("%Y-%m-%d %H:00:00", a)
    # b2 = time.strftime("%Y-%m-%d %H:58:59", a)
    do_com = "source /etc/profile;cd {P};sh bin/start.sh /home/nebula/inter_ds/fileprocess/log/dc/ {A} {B}".format(P="/home/NebulaSolarStat/DSRunStat/", A=b1, B=b2)

    # do_com = "source /etc/profile;cd {P};sh bin/start.sh /home/nebula/inter_ds/fileprocess/log/dc/ 2017-11-14 14:45:27 2017-11-14 15:49:28".format(P="/home/NebulaSolarStat/DSRunStat/")
    print "do_com:", do_com
    os.system(do_com)


    #读取文件，取出所有数据
    dsfile = get_files_path(out_path, 'txt')
    # print "dsfile", dsfile
    # 检查文件是否存在
    if [] == dsfile:
        print "文件不存在，退出"
    else:
        interds_data = get_interds_stat(dsfile[0], capture_time, today_month)

        put_interds_data(apm.server_ip, apm.server_port, interds_data)

    # 将统计文件拷贝到bak目录


if __name__ == '__main__':
    main()


