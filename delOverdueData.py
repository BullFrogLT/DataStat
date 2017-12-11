#!/usr/bin/env python
# -*- coding: utf8 -*-
# __author__ = tliu

import datetime
import sqlite3
from lib.common_lib import re_joint_dir_by_os, get_conf_pat


class NSSTATDB:
    def __init__(self):
        self.db_name = "nsstat3.db"
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()

class NSSTATConf:
    def __init__(self):
        # 读取conf目录下的ns.ini文件
        ns_conf = re_joint_dir_by_os("conf|ns.ini")
        # 数据库数据保存天数
        self.dbsave = get_conf_pat(ns_conf, "server", "sqlite3savedata")


def deltabledata(table, delday):
    try:
        deldb = NSSTATDB()
        sql = "DELETE FROM {TABLENAME} " \
              "WHERE DATE < '{DAY}' " \
              "".format(TABLENAME=table, DAY=delday)
        deldb.cur.execute(sql)
        deldb.conn.commit()
    except Exception, e:
        print e

def run():
    # 清除sqlite数据库中过期数据，默认保存30天数据
    # 过期天数
    apm = NSSTATConf()
    # overdue_day = (datetime.date.today() + datetime.timedelta(days=-30)).strftime("%Y%m%d")
    overdue_day = (datetime.date.today() + datetime.timedelta(days=-int(apm.dbsave))).strftime("%Y%m%d")

    table_name = ['ns_stat_ares', 'ns_stat_crius', 'ns_stat_es', 'ns_stat_interds', 'ns_stat_top', 'ns_stat_tornado']

    for h, t in enumerate(table_name):
        deltabledata(t, overdue_day)

if __name__ == '__main__':
    run()
