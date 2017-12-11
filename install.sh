#!/bin/bash
#auth:!leC

NebulaSolarDash_PATH=`grep "shell_path" conf/ns.ini | awk -F"=" '{print $2}'`
# all_ip 是所有IP变量，用于机器连通性检测
all_ip=()
# 机器角色变量，用于安装top、ares、interds
all_app=()
all_app[0]=install_top_stat_agent
all_app[1]=install_ares_stat_agent
all_app[2]=install_interds_stat_agent


show_info()
{
  message="$1"
  echo -e "\033[32;49;1mInfo:${message}\033[39;49;0m"
}

show_err()
{
  message="${1}"
  echo -ne "\033[31;49;1mError:\033[0m"
  echo -e "\033[31;49m ${message}\033[0m"
  exit 1
}

check_env()
{
  # check_ip_file 判断文件是否存在，不存在则退出
  FILE=./conf/ns.ini
  if [ ! -f "$FILE" ]
    then
      show_err " can not find ./conf/ns.ini path, please check file."
      exit 1
  fi

  # get_ip
  # hadoop 集群主节点
  hm_ip=`grep "hm" conf/ns.ini | awk -F"=" '{print $2}'`
  # ES 集群主节点
  es_ip=`grep "es_ip" conf/ns.ini | awk -F"=" '{print $2}'`
  # interds 的IP，会有多值
  interds_ip=`grep "interds" conf/ns.ini | awk -F"=" '{print $2}'`
  interds_ips=${interds_ip//,/ }

  # check_value
  all_ip[0]=$hm_ip
  all_ip[1]=$es_ip
  all_ip[2]=$interds_ips
  for node in ${all_ip[*]}
  do
    echo ">>>> 正在检查本机到 $node 服务器信任:"
    ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no $node 'exit'
    if(($?!=0))
    then
      show_err " can not login $node without passwd, Or Connection closed by remote host"
      exit 1
    else
      show_info " connect $node successful."
    fi
  done
}

install_top_stat_agent()
{
  echo ">>>> top_stat_agent install starting..."
  ssh $hm_ip "source /etc/profile; rm -rf $NebulaSolarDash_PATH; mkdir -p $NebulaSolarDash_PATH"
  ssh $hm_ip "rm -rf /etc/cron.d/daemon_start_topic_agent"
  scp -r * root@$hm_ip:$NebulaSolarDash_PATH 1>/dev/null 2>/dev/null
  scp $NebulaSolarDash_PATH/lib/common_lib_nooracle.py root@$hm_ip:$NebulaSolarDash_PATH/lib/common_lib.py 1>/dev/null 2>/dev/null
  ssh $hm_ip "source /etc/profile; cp -r $NebulaSolarDash_PATH/crond/daemon_start_topic_agent /etc/cron.d/ && service crond restart 1>/dev/null 2>/dev/null"
  show_info " install top_stat_agent successful."
}

install_ares_stat_agent()
{
  echo ">>>> ares_stat_agent install starting..."
  ssh $es_ip "source /etc/profile; rm -rf $NebulaSolarDash_PATH; mkdir -p $NebulaSolarDash_PATH"
  ssh $es_ip "rm -rf /etc/cron.d/daemon_start_ares_agent"
  scp -r * root@$es_ip:$NebulaSolarDash_PATH 1>/dev/null 2>/dev/null
  scp $NebulaSolarDash_PATH/lib/common_lib_nooracle.py root@$es_ip:$NebulaSolarDash_PATH/lib/common_lib.py 1>/dev/null 2>/dev/null
  ssh $es_ip "source /etc/profile; cp -r $NebulaSolarDash_PATH/crond/daemon_start_ares_agent /etc/cron.d/ && service crond restart 1>/dev/null 2>/dev/null"
  show_info " install ares_stat_agent successful."
}

install_interds_stat_agent()
{
  for int in $interds_ips
  do
    echo ">>>> interds_stat_agent install starting..."
    ssh $int "source /etc/profile; rm -rf $NebulaSolarDash_PATH; mkdir -p $NebulaSolarDash_PATH"
    ssh $int "rm -rf /etc/cron.d/daemon_start_interds_agent"
    scp -r * root@$int:$NebulaSolarDash_PATH 1>/dev/null 2>/dev/null
    scp $NebulaSolarDash_PATH/lib/common_lib_nooracle.py root@$int:$NebulaSolarDash_PATH/lib/common_lib.py 1>/dev/null 2>/dev/null
    ssh $int "source /etc/profile; cp -r $NebulaSolarDash_PATH/crond/daemon_start_interds_agent /etc/cron.d/ && service crond restart 1>/dev/null 2>/dev/null"
    show_info " install interds_stat_agent successful."
  done
}

install_cx_Oracle()
{
  cd $NebulaSolarDash_PATH/lib/ && tar xzvf cx_Oracle-5.1.2.tar.gz 1>/dev/null 2>/dev/null && cd cx_Oracle-5.1.2/ && /usr/bin/python setup.py install 1>/dev/null 2>/dev/null
}

# 加载环境变量
script_init()
{
  source /etc/profile
}

install_local()
{
  # 安装 cx_Oracle 库
  install_cx_Oracle
  # 判断是否安装成功，后续再写

  # daemon_start_crius_agent、daemon_start_es_agent、daemon_start_tornado_agent、daemon_deloverduedata 安装在本机
  echo ">>>> crius_stat_agent es_stat_agent tornado_stat_agent install starting..."

  # crontab文件传创建方式为echo
  echo "58 * * * * root source /etc/profile && cd /home/NebulaSolarStat/sh && sh start_crius_agent.sh" > /etc/cron.d/daemon_start_crius_agent
  echo "58 * * * * root source /etc/profile && cd /home/NebulaSolarStat/sh && sh start_es_agent.sh" > /etc/cron.d/daemon_start_es_agent
  echo "58 * * * * root source /etc/profile && cd /home/NebulaSolarStat/sh && sh start_tornado_agent.sh" > /etc/cron.d/daemon_start_tornado_agent
  echo "0 1 * * * root source /etc/profile && cd /home/NebulaSolarStat/ && /usr/bin/python delOverdueData.py" > /etc/cron.d/daemon_deloverduedata

  # crontab文件传创建方式为cp
  # cp $NebulaSolarDash_PATH/crond/daemon_start_crius_agent /etc/cron.d/ 1>/dev/null 2>/dev/null
  # cp $NebulaSolarDash_PATH/crond/daemon_start_es_agent /etc/cron.d/ 1>/dev/null 2>/dev/null
  # cp $NebulaSolarDash_PATH/crond/daemon_start_tornado_agent /etc/cron.d/ 1>/dev/null 2>/dev/null
  # cp $NebulaSolarDash_PATH/crond/daemon_deloverduedata /etc/cron.d/ 1>/dev/null 2>/dev/null

  source /etc/profile && service crond restart 1>/dev/null 2>/dev/null
  show_info " install crius_stat_agent es_stat_agent tornado_stat_agent daemon_deloverduedata successful."
}

install()
{
  for install_app in ${all_app[*]}
  do
    $install_app
  done

  # 安装本机监控程序
  install_local
}

main()
{
  script_init
  check_env
  install
  # echo "daemon_start_crius_agent、daemon_start_es_agent、daemon_start_tornado_agent 安装在本机，需要手动执行下，以防止由于环境问题脚本无法执行"
}

main