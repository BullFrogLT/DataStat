#!/bin/bash

SETCOLOR_SUCCESS="echo -en \\033[1;32m"
SETCOLOR_FAILURE="echo -en \\033[1;31m"
SETCOLOR_WARNING="echo -en \\033[1;33m"
SETCOLOR_NORMAL="echo -en \\033[0;39m"

# 定义记录日志的函数
LogMsg()
{
    time=`date "+%D %T"`
    echo "[$time] : INFO    : $*"
    ${SETCOLOR_NORMAL}
}

LogWarnMsg()
{
    time=`date "+%D %T"`
    ${SETCOLOR_WARNING}
    echo "[$time] : WARN    : $*"
    ${SETCOLOR_NORMAL}
}

LogSucMsg()
{
    time=`date "+%D %T"`
    ${SETCOLOR_SUCCESS}
    echo "[$time] : SUCCESS : $*"
    ${SETCOLOR_NORMAL}
}

LogErrorMsg()
{
    time=`date "+%D %T"`
    ${SETCOLOR_FAILURE}
    echo "[$time] : ERROR   : $*"
    ${SETCOLOR_NORMAL}
}

INSTALL_PATH="/home/NebulaSolarStat"
start_ares_agent()
{
	agent_pid=`ps aux | grep "ares_stat_agent.py" | grep -v grep | awk -F " " '{print $2}'`
	if [ "$agent_pid" = "" ]
	then
		cd ${INSTALL_PATH} && source /etc/profile && nohup /usr/bin/python ares_stat_agent.py > log_of_ares_stat_agent 2>&1 &
		cd ${INSTALL_PATH} && source /etc/profile && nohup /usr/bin/python ares_stat_agent_type.py > log_of_ares_stat_agent 2>&1 &
	else
		exit 1
	fi
}

start_ares_agent
