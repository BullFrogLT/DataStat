#!/usr/bin/env python
# -*- coding: utf8 -*-
# __author__ = tliu

import sqlite3
import time
import datetime


class NSSTATDB:
    def __init__(self):
        self.db_name = "nsstat_20171101_njsj.db"    # 配置db文件名称
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()


class stat_daytable_increment(object):
    '''
            查询ES当天数据量

            --- 天表增量： 找出每天的天表数据量，可以算作每天的增量
            --- 今天增量：
            SELECT *
            FROM ns_stat_es
            WHERE DATE = '20170822' --- 默认这里都取今天时间
            AND TABLENAME like '%-20170822'  -- 取今天日期
            AND CAPTURETIME = (
            SELECT MAX(CAPTURETIME)
            FROM ns_stat_es
            WHERE DATE = '20170822'   -- 默认这里都取今天时间
            )

            --- 昨日增量：
            SELECT *
            FROM ns_stat_es
            WHERE DATE = '20170822'
            AND TABLENAME like '%-20170821'      # 取昨日日期
            AND CAPTURETIME = (
            SELECT MAX(CAPTURETIME)
            FROM ns_stat_es
            WHERE DATE = '20170822'
            )



            --- 月表增量：
            --- 1. 当天是1号，则统计当月的表
            --- 2. 当天不是1号，月表 今天量 -  昨日量
            --- 当天是1号，今天的月表增量:
            if day.endswitch("01"):
            SELECT *
            FROM ns_stat_es
            WHERE DATE = '20170822'       # 取今天的日期
            AND TABLENAME like '%-201708'    # 取当天的月
            AND CAPTURETIME = (
            SELECT MAX(CAPTURETIME)
            FROM ns_stat_es
            WHERE DATE = '20170822'       # 取今天的日期
            )

            else:
            FROM ns_stat_es
            WHERE DATE = '20170822'       # 取今日的日期
            AND TABLENAME like '%-201708'    # 取当天的月
            AND CAPTURETIME = (
            SELECT MAX(CAPTURETIME)
            FROM ns_stat_es
            WHERE DATE = '20170822'      # 取今日的日期
            赋值给MONTH1

            FROM ns_stat_es
            WHERE DATE = '20170821'       # 取昨日的日期
            AND TABLENAME like '%-201708'    # 取当天的月
            AND CAPTURETIME = (
            SELECT MAX(CAPTURETIME)
            FROM ns_stat_es
            WHERE DATE = '20170821'      # 取昨日的日期
            赋值给MONTH2
            今天的增量 = MONTH1 - MONTH2

            --- 昨日的月表增量：
            if day.endswitch("01"):
            SELECT *
            FROM ns_stat_es
            WHERE DATE = '20170821'       # 取昨日的日期
            AND TABLENAME like '%-201708'    # 取当天的月
            AND CAPTURETIME = (
            SELECT MAX(CAPTURETIME)
            FROM ns_stat_es
            WHERE DATE = '20170821'       # 取昨日的日期

            else：
            FROM ns_stat_es
            WHERE DATE = '20170821'       # 取昨日的日期
            AND TABLENAME like '%-201708'    # 取当天的月
            AND CAPTURETIME = (
            SELECT MAX(CAPTURETIME)
            FROM ns_stat_es
            WHERE DATE = '20170821'      # 取今日的日期
            赋值给MONTH1

            FROM ns_stat_es
            WHERE DATE = '20170820'       # 取前日的日期
            AND TABLENAME like '%-201708'    # 取当天的月
            AND CAPTURETIME = (
            SELECT MAX(CAPTURETIME)
            FROM ns_stat_es
            WHERE DATE = '20170820'      # 取前日的日期
            赋值给MONTH2
            今天的增量 = MONTH1 - MONTH2


            --- 总表增量：
            --- 1.  当日增量统计： 统计-1/-2
            --- 2.  不是当日，后一天history表数据量  -  前一天history表数据量

            统计今天总表的增量：
            FROM ns_stat_es
            WHERE DATE = '20170822'       # 取当日的日期
            AND TABLENAME like '%-1'    # 取当天的-1/-2 表
            AND CAPTURETIME = (
            SELECT MAX(CAPTURETIME)
            FROM ns_stat_es
            WHERE DATE = '20170822'      # 取当日的日期

            统计昨日总表的增量：
            FROM ns_stat_es
            WHERE DATE = '20170821'       # 取昨日的日期
            AND TABLENAME like '%-history'    # 取当天的-1/-2 表
            AND CAPTURETIME = (
            SELECT MAX(CAPTURETIME)
            FROM ns_stat_es
            WHERE DATE = '20170821'      # 取昨日的日期
            赋值给H1

            FROM ns_stat_es
            WHERE DATE = '20170820'       # 取前日的日期
            AND TABLENAME like '%-history'    # 取当天的-1/-2 表
            AND CAPTURETIME = (
            SELECT MAX(CAPTURETIME)
            FROM ns_stat_es
            WHERE DATE = '20170820'      # 取前日的日期
            赋值给H2
            昨日的增量 = H1 - H2

    '''

    db = NSSTATDB()

    def today_stat(self, table_name):
        _today = datetime.datetime.now().strftime("%Y%m%d")

        sql = "SELECT sum(TABLENUM) " \
            "FROM ns_stat_es " \
            "where DATE = '{TODAY}' " \
            "AND TABLENAME like '%-{DAY}' " \
            "AND CAPTURETIME = ( " \
            "SELECT MAX(CAPTURETIME) " \
            "FROM ns_stat_es " \
            "WHERE DATE = '{TODAY}' " \
            ")".format(TODAY=_today, DAY=table_name)
        self.db.cur.execute(sql)

        sum_t = self.db.cur.fetchall()[0][0]
        if sum_t == None:
            sum_t = 0
        return sum_t

    def month_stat(self, table_name, first_day):
        # 如果是1号，则今天的表就是当日增量
        day_month = table_name[:-2]
        if table_name.endswith("01"):
            sql = "SELECT sum(TABLENUM) " \
                "FROM ns_stat_es " \
                "where DATE = '{TODAY}' " \
                "AND TABLENAME like '%-{DAY}' " \
                "AND CAPTURETIME = ( " \
                "SELECT MAX(CAPTURETIME) " \
                "FROM ns_stat_es " \
                "WHERE DATE = '{TODAY}' " \
                ")".format(TODAY=table_name, DAY=day_month)
            # print "sql:", sql
            self.db.cur.execute(sql)
            sum_m = self.db.cur.fetchall()[0][0]
            if None == sum_m:
                sum_m = 0
            return sum_m
        # 如果今日不是1号，需要用今日月表数据量-昨日月表数据量
        else:
            sql1 = "SELECT sum(TABLENUM) " \
                "FROM ns_stat_es " \
                "where DATE = '{TODAY}' " \
                "AND TABLENAME like '%-{DAY}' " \
                "AND CAPTURETIME = ( " \
                "SELECT MAX(CAPTURETIME) " \
                "FROM ns_stat_es " \
                "WHERE DATE = '{TODAY}' " \
                ")".format(TODAY=table_name, DAY=day_month)
            # print "sql1:", sql1
            self.db.cur.execute(sql1)
            num_1 = self.db.cur.fetchall()[0][0]
            if None == num_1:
                num_1 = 0

            sql2 = "SELECT sum(TABLENUM) " \
                "FROM ns_stat_es " \
                "where DATE = '{TODAY}' " \
                "AND TABLENAME like '%-{DAY}' " \
                "AND CAPTURETIME = ( " \
                "SELECT MAX(CAPTURETIME) " \
                "FROM ns_stat_es " \
                "WHERE DATE = '{TODAY}' " \
                ")".format(TODAY=first_day, DAY=day_month)
            # print "sql2:", sql2
            self.db.cur.execute(sql2)
            num_2 = self.db.cur.fetchall()[0][0]
            if None == num_2:
                num_2 = 0

            sum_m = num_1 - num_2
            return sum_m

    def total_stat(self, table_name, first_day):
        # 取知识库-1 或 -2表数据量
        if table_name == datetime.datetime.now().strftime("%Y%m%d"):
            dayCount = (int(time.time()) / 86400)
            tableNo = dayCount % 2 + 1
            sql = "SELECT sum(TABLENUM) " \
                "FROM ns_stat_es " \
                "where DATE = '{TODAY}' " \
                "AND TABLENAME like '%-{NO}' " \
                "AND CAPTURETIME = ( " \
                "SELECT MAX(CAPTURETIME) " \
                "FROM ns_stat_es " \
                "WHERE DATE = '{TODAY}' " \
                ")".format(TODAY=table_name, NO=tableNo)
            self.db.cur.execute(sql)
            sum_t = self.db.cur.fetchall()[0][0]
            if None == sum_t:
                sum_t = 0
            return sum_t
        # 今日history数据量-昨日history数据量
        else:
            sql1 = "SELECT sum(TABLENUM) " \
                "FROM ns_stat_es " \
                "where DATE = '{TODAY}' " \
                "AND TABLENAME like '%-history' " \
                "AND CAPTURETIME = ( " \
                "SELECT MAX(CAPTURETIME) " \
                "FROM ns_stat_es " \
                "WHERE DATE = '{TODAY}' " \
                ")".format(TODAY=table_name)
            # print "sql1:", sql1, table_name
            self.db.cur.execute(sql1)
            sum_1 = self.db.cur.fetchall()[0][0]
            if None == sum_1:
                sum_1 = 0

            sql2 = "SELECT sum(TABLENUM) " \
                "FROM ns_stat_es " \
                "where DATE = '{TODAY}' " \
                "AND TABLENAME like '%-history' " \
                "AND CAPTURETIME = ( " \
                "SELECT MAX(CAPTURETIME) " \
                "FROM ns_stat_es " \
                "WHERE DATE = '{TODAY}' " \
                ")".format(TODAY=first_day)
            self.db.cur.execute(sql2)
            sum_2 = self.db.cur.fetchall()[0][0]
            if None == sum_2:
                sum_2 = 0

            sum_t = sum_1 - sum_2
            return sum_t


def main():
    table_name = "20171101"  # 需要统计几号就填几号日期
    first_day = "20171030"   # 上面的日期减一天

    st = stat_daytable_increment()
    es_data = {}

    # 天表增量
    day_table_increment = st.today_stat(table_name)
    print "day_table_increment:", day_table_increment

    # 月表增量
    month_table_increment = st.month_stat(table_name, first_day)
    print "month_table_increment:", month_table_increment

    # 总表增量
    total_table_inceement = st.total_stat(table_name, first_day)
    print "total_table_inceement:", total_table_inceement

    # 增量的和
    total_tmp = day_table_increment + month_table_increment + total_table_inceement
    es_data[table_name] = total_tmp

    print es_data

if __name__ == '__main__':
    '''
    统计ES界面中当日数据量
    '''
    main()
