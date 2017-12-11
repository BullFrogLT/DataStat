#!/usr/bin/env python
# -*- coding: utf8 -*-
# __author__ = tliu


import datetime
import time
from lib.alarm import alarm_for_ns


today = datetime.datetime.now().strftime("%Y%m%d")      # 今天日期，格式为 20170913
day_e = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y%m%d")     # 昨日日期，格式为 20170912
first_day = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y%m%d")     # 昨日日期，格式为 20170912

today_c = datetime.date.today() + datetime.timedelta(days=-1)
first_time = int(time.mktime(today_c.timetuple()))
last_time = int(time.mktime(today_c.timetuple()) + 86399)

alarm_for_ns().init_db_tornado_3001_alarm(today)

