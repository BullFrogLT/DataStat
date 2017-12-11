#!/usr/bin/env python
# -*- coding: utf8 -*-
# __author__ = tliu


import sqlite3
import datetime
import time


class NSSTATConf:
    def __init__(self):
        self.db_name = "nsstat.db"
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()

        # 取知识库表-1 或 -2
        self.dayCount = (int(time.time()) / 86400)
        self.tableNo = self.dayCount % 2 + 1

        # 取海量当天表的日期： 20170818
        self.today = datetime.datetime.now().strftime("%Y%m%d")
        self.today_month = self.today[:-2]

    def query_es_today_total(self):
        es_stat = {}
        # 取知识库表-1 或 -2
        # dayCount = (int(time.time()) / 86400)
        # tableNo = dayCount % 2 + 1

        # 取海量当天表的日期： 20170818
        # today = datetime.datetime.now().strftime("%Y%m%d")
        # today_month = today[:-2]


        # 统计-1(或-2)表、海量当天表数据总量
        query_es_h = "SELECT sum(TABLENUM) " \
                       "FROM ns_stat_ares " \
                       "WHERE (TABLENAME like '%-{A}' OR TABLENAME like '%{B}') " \
                       "AND CAPTURETIME = ( " \
                       "SELECT max(CAPTURETIME) " \
                       "FROM ns_stat_ares " \
                       ")".format(A=self.tableNo, B=self.today)

        # 统计月表当天数据量，按CAPTURETIME分组统计总量，并返回CAPTURETIME最迟的数据量
        query_es_d = "SELECT CAPTURETIME, sum(TABLENUM) " \
                     "FROM ns_stat_ares " \
                     "WHERE TABLENAME like '%-{C}' " \
                     "AND DATE = '{D}' " \
                     "GROUP BY CAPTURETIME " \
                     "ORDER BY CAPTURETIME " \
                     "DESC limit 1".format(C=self.today_month, D=self.today)

        try:
            db.cur.execute(query_es_h)
            m_num = db.cur.fetchall()[0][0]

            db.cur.execute(query_es_d)
            d_num = db.cur.fetchall()[0][1]

            total_num = m_num + d_num
            es_stat['es_today_total'] = total_num

            return es_stat
        except Exception, e:
            print e

    def query_crius_today_total(self):
        crius_stat = {}
        query_crius = "select sum(SUCCESS_COUNT) " \
                      "from ns_stat_crius " \
                      "where  DATE = '{E}' " \
                      "AND CAPTURETIME = ( " \
                      "SELECT max(CAPTURETIME) " \
                      "FROM ns_stat_crius) ".format(E=self.today)
        db.cur.execute(query_crius)
        c_num = db.cur.fetchall()[0][0]
        crius_stat['crius_today_todal'] = c_num
        return crius_stat

db = NSSTATConf()


def main():
    # 分析 nsstat.db 中数据，并输出到文件中
    result_total = {}

    # 当日inter_ds解析数据量统计


    # 当日inter_ds发tornado数据量统计

    # 当日tornado接收数据量统计

    # 当日tornado输出kafka数据量统计

    # 当日TOPIC数据量统计

    # 统计crius当天入库总量
    result_total['crius_stat'] = db.query_crius_today_total()
    print result_total      # {'crius_stat': {'crius_today_todal': 46}, 'es_stat': {'es_today_total': 0}}

    # 当天ES入库数据量统计
    result_total['es_stat'] = db.query_es_today_total()




if __name__ == '__main__':
    # NS平台数据流统计
    main()
