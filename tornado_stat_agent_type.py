#!/usr/bin/env python
# -*- coding: utf8 -*-
# __author__ = tliu

import urllib
import urllib2
from lib.common_lib_nooracle import re_joint_dir_by_os, get_conf_pat
import time
import datetime
import re
import json


class NSConf:
    def __init__(self):
        ns_conf = re_joint_dir_by_os("conf|ns.ini")
        self.server_ip = get_conf_pat(ns_conf, "server", "ip")
        self.server_port = get_conf_pat(ns_conf, "server", "port")
        self.rtpmaster = get_conf_pat(ns_conf, "tornado", "RTPMaster")
        self.output_kafka = get_conf_pat(ns_conf, "tornado", "OUTPUT_KAFKA")
        self.output_rtpworker = get_conf_pat(ns_conf, "tornado", "RTPWorker")


def put_tornado_data(server_ip, server_port, tornado_data):
    try:
        req = urllib2.Request("http://{IP}:{PORT}/updatetornado_type/".format(IP=server_ip, PORT=server_port), json.dumps(tornado_data), {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        # response = f.readlines()
        # print response
        f.close()
    except Exception, e:
        print e

def get_tornado_data_type(url, capture_time, day_t, result, kafka, today_month):
    # 如果打不开url，则说明没有数据

    if 404 == urllib.urlopen(url).getcode():
        pass
    elif 200 == urllib.urlopen(url).getcode():
        print "url:", url
        # 打开、读取网页内容
        html = urllib.urlopen(url).read()

        # html 是str类型，但是有换行符号，需要把换行符号去掉
        html = ''.join(html.split("\n"))

        # 通过正则表达式找到表格中的数据，传给data列表
        data = re.compile("<td ><font(.*?)</tr>").findall(html)
        # 通过正则表达式搜索每行中的内容，传给result
        for d in data:
            rule_data = re.compile("color=#0000CD>(.*?)</font></td>")
            data_tmp = rule_data.findall(d)
            # print "data_tmp", data_tmp

            # 去掉数字中的，号
            print "data_tmp:", data_tmp
            result_t = []
            for d_d in data_tmp:
                if ',' in d_d:
                    result_t.append(''.join(d_d.split(",")))
                else:
                    result_t.append(d_d)
            # 添加 print result、STATTIME、CAPTURETIME、DATE
            result_t.append(kafka)
            result_t.append(day_t)
            result_t.append(capture_time)
            result_t.append(today_month)

            # 传给最外层的result
            result.append(result_t)
        print "result::", result

    # 不返回，直接将结果传给最外层的result变量


def gettornadodata(rtpmaster, output_kafka, output_rtpworker, result):
    tornado_data = {}
    capture_time = int(time.time())         # capture_time
    today_month = datetime.datetime.now().strftime("%Y%m%d")       # DATE

    top_time = 10
    r = []

    # 1. 按天循环
    for i in range(top_time):
        a = []
        # day_t = (datetime.date.today() + datetime.timedelta(days=-i)).strftime("%Y%m%d")
        day_t = 20171007
        # print "day_t", day_t

        # 2. 按 OUTPUT_KAFKA中定义的协议循环
        for kafka in output_kafka:

            # 3. 按数据节点排序
            for rtpworker in output_rtpworker:

                # url = 'http://{RTPMASTER}/StreamCenter/{D}/allstat.html'.format(RTPMASTER=rtpmaster, D=day_t)
                # url = 'http://172.16.4.219/StreamCenter/20171028/.detail/TORNADO/192.168.0.63:1818KAFKA_SHML.html'.format(RTPMASTER=rtpmaster, D=day_t)
                url = 'http://{RTPMASTER}/StreamCenter/{D}/.detail/TORNADO/{RTPWORKER}:1818{OUTPUTKAFKA}.html'.format(
                    RTPMASTER=rtpmaster,
                    RTPWORKER=rtpworker,
                    OUTPUTKAFKA=kafka,
                    D=day_t)
                get_tornado_data_type(url, capture_time, day_t, result, kafka, today_month)


def main():
    apm = NSConf()
    result = []

    # tornado单台或者多台时，传给列表
    if ',' in apm.output_rtpworker:
        apm.output_rtpworker = apm.output_rtpworker.split(",")
    else:
        apm.output_rtpworker = [apm.output_rtpworker]

    # OUTPUT_KAFKA
    apm.output_kafka = apm.output_kafka.split(",")

    gettornadodata(apm.rtpmaster, apm.output_kafka, apm.output_rtpworker, result)

    print result

    put_tornado_data(apm.server_ip, apm.server_port, result)



if __name__ == '__main__':
    main()
