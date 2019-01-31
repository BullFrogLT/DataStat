# 基于 python 的 bottle 库实现的数据量统计应用

>需求背景：因公司运维需求，需要对某产品底层数据处理及存储层做数据量统计，需求不多，只是要求在尽量短的时间内，完成各模块数据量统计的趋势图即可。
介于此类研发场景，做为一枚测试人员，需要挑选方便安装、研发成本低的轻量级架构实现需求。

>Bottle是一个简单高效的遵循WSGI的微型python Web框架。说微型，是因为它只有一个文件，除Python标准库外，它不依赖于任何第三方模块，所以部署于 linux 环境中不需要再安装第三方库，只需要将 py 文件复制到程序中引用即可。便于安装、实现简单，使用python 轻量级的 web 开发框架 `bottle`，即可快速实现需求。

# 一、系统架构
待补充

# 二、基本需求梳理
>虽然说初始需求只要求尽快的满足数据量统计趋势图即可，但是为提高现场环境实用性，决定增加数据量异常预警。


*  :white_check_mark: 主程序 `ns_stat_server.py`负责接收各 agent 发向服务端的请求；
```
@app.route('/index/', method='GET')
@app.route('/', method="GET")
```

*  :white_check_mark: 根据角色定义统计 agent 程序，分别安装部署在各个模块角色中，负责收集统计信息，上报给 server 端

*  :white_check_mark: 使用 sqlite 数据库保存数据，数据保存30天，过期自动删除

*  :white_check_mark: 支持一键化安装部署，可检测 linux 服务器间信任链接

*  :white_check_mark: 各统计模块采用 crond 定时任务，每小时定时拉起 agent 采集程序

*  :white_check_mark: 选用 echarts 快速实现趋势图需求



# 三、程序设计
## 数据抓取 agent 简述
* ### 抓取数据接入数据量： interds

  `interds_agent` 调用日志分析工具 DSRunStat，分析返回结果

  `tornado_agent` 使用urllib.urlopen 爬取 tornado 统计界面中数据

  `crius_agent` 调用日志分析工具，分析日志结果

  `ares_agent` 分析入库统计日志数据

  `es_agent` 爬取 Elasticsearch 统计页面数据


# 四、效果展示
### 各模块数据量统计图
![数据总条数.png](https://github.com/BullFrogLT/stat/blob/master/pic/数据总条数.png "数据总条数.png")

### interds数据量统计图
![interds数据量统计.png](https://github.com/BullFrogLT/stat/blob/master/pic/interds数据量统计.png "interds数据量统计.png")

### tornado数据量统计图
![tornado数据量统计.png](https://github.com/BullFrogLT/stat/blob/master/pic/tornado数据量统计.png "tornado数据量统计.png")

### topic数据量统计图
![topic数据量统计.png](https://github.com/BullFrogLT/stat/blob/master/pic/topic数据量统计.png "topic数据量统计.png")

### crius数据量统计图
![crius数据量统计.png](https://github.com/BullFrogLT/stat/blob/master/pic/crius数据量统计.png "crius数据量统计.png")

### ares数据量统计图
![ares数据量统计.png](https://github.com/BullFrogLT/stat/blob/master/pic/ares数据量统计.png "ares数据量统计.png")

### elasticsearch数据量统计图
![elasticsearch数据量统计.png](https://github.com/BullFrogLT/stat/blob/master/pic/es数据量统计.png "es数据量统计.png")

### 按协议统计图
![按协议统计.png](https://github.com/BullFrogLT/stat/blob/master/pic/按协议统计.png "按协议统计.png")

### 数据量异常预警界面
![预警界面.png](https://github.com/BullFrogLT/stat/blob/master/pic/预警界面.png "预警界面.png")

### 预警规则
![预警规则.png](https://github.com/BullFrogLT/stat/blob/master/pic/预警规则.png "预警规则.png")

# 五、部分代码演示
### init_db.py 创建统计表
![init_db.py](https://github.com/BullFrogLT/stat/blob/master/pic/创建数据库代码.png "initdb.png")





