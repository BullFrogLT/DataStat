#!/usr/bin/env python
# -*- coding:utf-8 -*-
# __author__ = tliu

import sqlite3
import inspect


class NSSTATDB:
    def __init__(self):
        self.db_name = "nsstat.db"
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()

    def init_db_ares(self):
        init_sql = """
        CREATE TABLE IF NOT EXISTS ns_stat_ares (
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          STATTIME TEXT NUL NULL,
          TOTALCOUNT INTEGER NOT NULL,
          SUCCOUNT INTEGER NOT NULL,
          FAILCOUNT INTEGER NOT NULL,
          CAPTURETIME INTEGER NOT NULL,
          DATE TEXT NOT NULL
        )
                """
        self.cur.execute(init_sql)
        self.conn.commit()


    def init_db_ares_type(self):
        # 新增 TABLECATEGORY、STORESIZE
        init_sql = """
        CREATE TABLE IF NOT EXISTS ns_stat_ares_type (
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          STATTIME TEXT NUL NULL,
          TABLECATEGORY TEXT NUL NULL,
          TOTALCOUNT INTEGER NOT NULL,
          SUCCOUNT INTEGER NOT NULL,
          FAILCOUNT INTEGER NOT NULL,
          STORESIZE TEXT NUL NULL,
          CAPTURETIME INTEGER NOT NULL,
          DATE TEXT NOT NULL
        )
                """
        self.cur.execute(init_sql)
        self.conn.commit()


    def init_db_es(self):
        init_sql = """
        CREATE TABLE IF NOT EXISTS ns_stat_es (
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          TABLENAME TEXT NOT NULL,
          TABLENUM INTEGER NOT NULL,
          CAPTURETIME INTEGER NOT NULL,
          TABLESIZE TEXT,
          DATE TEXT NOT NULL
        )
                """
        self.cur.execute(init_sql)
        self.conn.commit()

    def init_db_crius(self):
        init_sql = """
        CREATE TABLE IF NOT EXISTS ns_stat_crius (
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          IMPORT_DATE TEXT NOT NULL,
          TABLE_CATEGORY TEXT NOT NULL,
          SUCCESS_COUNT INTEGER NOT NULL,
          CAPTURETIME INTEGER NUL NULL,
          FAILED_COUNT INTEGER NOT NULL,
          LOADTYPE TEXT NOT NULL,
          DATE TEXT NOT NULL
        )
        """
        self.cur.execute(init_sql)
        self.conn.commit()


    def init_db_top(self):
        init_sql = """
        CREATE TABLE IF NOT EXISTS ns_stat_top (
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          TABLENAME TEXT NOT NULL,
          TABLENUM INTEGER NOT NULL,
          CAPTURETIME INTEGER NUL NULL,
          DATE TEXT NOT NULL
        )
        """
        self.cur.execute(init_sql)
        self.conn.commit()


    def init_db_interds(self):
        init_sql = """
        CREATE TABLE IF NOT EXISTS ns_stat_interds (
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          DATATYPE TEXT NOT NULL,
          READNUM INTEGER NOT NULL,
          RESULTNUM INTEGER NOT NULL,
          CONDROPNUM INTEGER NOT NULL,
          OUTSUCCNUM INTEGER NOT NULL,
          OUTFAILEDNUM INTEGER NOT NULL,
          OUTDROPNUM INTEGER NOT NULL,
          CAPTURETIME INTEGER NUL NULL,
          DATE TEXT NOT NULL
        )
        """
        self.cur.execute(init_sql)
        self.conn.commit()


    def init_db_tornado_type(self):
        """
        ID:自增
        CITY:上传地市
        DATASOURCE：数据源
        DATATYPE：协议
        DATAFLAG：数据标示
        REC_TOTAL：接收总量/条
        MAKE_TOTAL：生成总量/条
        LEGA_TOTAL：合法总量/条
        SUC_NUM：输出成功/条
        FAILED_NUM：失败总量/条
        DROP_NUM：丢弃总量/条
        AVA_SIZE:平均大小/KB
        OUTPUTKAFKA:KAFKA_DTSK
        STATTIME：数据时间，年月日格式
        CAPTURETIME
        DATE：程序执行日期，年月日格式
        :return:
        """
        init_sql = """
        CREATE TABLE IF NOT EXISTS ns_stat_tornado_type (
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          CITY TEXT NUL NULL,
          DATASOURCE TEXT NUL NULL,
          DATATYPE TEXT NUL NULL,
          DATAFLAG TEXT NUL NULL,
          REC_TOTAL INTEGER NUL NULL,
          MAKE_TOTAL INTEGER NUL NULL,
          LEGA_TOTAL INTEGER NUL NULL,
          SUC_NUM INTEGER NUL NULL,
          FAILED_NUM INTEGER NUL NULL,
          DROP_NUM INTEGER NUL NULL,
          AVA_SIZE TEXT NUL NULL,
          OUTPUTKAFKA TEXT NUL NULL,
          STATTIME TEXT NUL NULL,
          CAPTURETIME INTEGER NUL NULL,
          DATE TEXT NOT NULL
        )
        """
        self.cur.execute(init_sql)
        self.conn.commit()



    def init_db_tornado(self):
        init_sql = """
        CREATE TABLE IF NOT EXISTS ns_stat_tornado (
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          STATTIME TEXT NUL NULL,
          REC_TOTL INTEGER NUL NULL,
          SUC_NUM INTEGER NUL NULL,
          FAILED_NUM INTEGER NUL NULL,
          TOKFK_TOTAL INTEGER NUL NULL,
          TOKFK_SUC INTEGER NUL NULL,
          TOKFK_FAILED INTEGER NUL NULL,
          CAPTURETIME INTEGER NUL NULL,
          DATE TEXT NOT NULL
        )
        """
        self.cur.execute(init_sql)
        self.conn.commit()


    def init_db_interds_type(self):
        # 新增 DATASOURCE、OUTPUTTYPE
        init_sql = """
        CREATE TABLE IF NOT EXISTS ns_stat_interds_type (
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          DATASOURCE TEXT NOT NULL,
          DATATYPE TEXT NOT NULL,
          READNUM INTEGER NOT NULL,
          RESULTNUM INTEGER NOT NULL,
          CONDROPNUM INTEGER NOT NULL,
          OUTPUTTYPE TEXT NOT NULL,
          OUTSUCCNUM INTEGER NOT NULL,
          OUTFAILEDNUM INTEGER NOT NULL,
          OUTDROPNUM INTEGER NOT NULL,
          CAPTURETIME INTEGER NUL NULL,
          DATE TEXT NOT NULL
        )
        """
        self.cur.execute(init_sql)
        self.conn.commit()


    def run_all_init_func(self):
        """
        自动获取 NSSTATDb 类里的所有init_db_xxx方法，依次执行建表
        """
        for func in inspect.getmembers(self, predicate=inspect.ismethod):
            if func[0][:7] == 'init_db':
                func[1]()

