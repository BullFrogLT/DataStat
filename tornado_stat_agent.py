#!/usr/bin/env python
# -*- coding: utf8 -*-
# __author__ = tliu

import urllib
from lib.common_lib_nooracle import re_joint_dir_by_os, get_conf_pat
import time
import datetime
import urllib2
import json


class NSConf:
    def __init__(self):
        ns_conf = re_joint_dir_by_os("conf|ns.ini")
        self.server_ip = get_conf_pat(ns_conf, "server", "ip")
        self.server_port = get_conf_pat(ns_conf, "server", "port")
        self.rtpmaster = get_conf_pat(ns_conf, "tornado", "RTPMaster")
        self.output_kafka = get_conf_pat(ns_conf, "tornado", "OUTPUT_KAFKA")


def put_tornado_data(server_ip, server_port, tornado_data):
    try:
        req = urllib2.Request("http://{IP}:{PORT}/updatetornado/".format(IP=server_ip, PORT=server_port), json.dumps(tornado_data), {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        # response = f.readlines()
        # print response
        f.close()
    except Exception, e:
        print e


def gettornadodata(rtpmaster, output_kafka):
    tornado_data = {}
    capture_time = int(time.time())         # capture_time
    today_month = datetime.datetime.now().strftime("%Y%m%d")       # DATE

    top_time = 10
    r = []
    '''
        字段说明：
            day_t:  统计的数据的天数
            rec_total:  tornado 明细中的 接受总量/条
            suc_num：    明细中的 成功处理/条
            failed_num： 失败处理/条（rec_total - suc_num）
            tokfk_total：    各模块输出到kafka 合法总量/条 （分发总量/条）
            tokfk_suc：  各模块输出到kafka 输出成功/条  （分发成功/条）
            tokfk_failed：    各模块输出到kafka 输出失败/条 （tokfk_total - tokfk_suc）
            capture_time：
            today_month： 当天年月日，便于后续做统计分析
    '''
    for i in range(top_time):
        a = []
        day_t = (datetime.date.today() + datetime.timedelta(days=-i)).strftime("%Y%m%d")
        # print "day_t", day_t
        url = 'http://{RTPMASTER}/StreamCenter/{D}/allstat.html'.format(RTPMASTER=rtpmaster, D=day_t)
        if 404 == urllib.urlopen(url).getcode():
            rec_total = suc_num = failed_num = tokfk_total = tokfk_suc = tokfk_failed = 0
            a = [day_t, rec_total, suc_num, failed_num, tokfk_total, tokfk_suc, tokfk_failed, capture_time, today_month]

        elif 200 == urllib.urlopen(url).getcode():
            web = urllib.urlopen(url).readlines()
            # print web
            tokfk_total = tokfk_suc = tokfk_failed = 0
            for web_index, web_value in enumerate(web):
                if '明细' in web_value:
                    rec_total = int("".join(web[web_index + 1][30:-13].split(",")))
                    suc_num = int("".join(web[web_index + 2][30:-13].split(",")))
                    failed_num = rec_total - suc_num
                else:
                    for tmp in output_kafka.split(","):
                        if tmp in web_value:

                            tokfk_total_tmp = int("".join(web[web_index + 1][30:-13].split(",")))
                            tokfk_suc_tmp = int("".join(web[web_index + 2][30:-13].split(",")))
                            tokfk_total = tokfk_total + tokfk_total_tmp
                            tokfk_suc = tokfk_suc + tokfk_suc_tmp
                    tokfk_failed = tokfk_total - tokfk_suc

            a = [day_t, rec_total, suc_num, failed_num, tokfk_total, tokfk_suc, tokfk_failed, capture_time, today_month]
        r.append(a)
    tornado_data['result_tornado'] = r
    print tornado_data
    return tornado_data


def main():
    apm = NSConf()

    tornado_data = gettornadodata(apm.rtpmaster, apm.output_kafka)

    put_tornado_data(apm.server_ip, apm.server_port, tornado_data)


if __name__ == '__main__':
    main()
