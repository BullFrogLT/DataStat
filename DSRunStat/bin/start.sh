#!/bin/sh

#如果传递进来的参数个数不等于1，则记录错误并退出
if [ $# -ne 5 ]; then
	#格式为sh start.sh 执行命令 目录
	echo "Input error ! You must input 3 agrs !"
	echo "For example: [sh start.sh /home/nebula/inter_ds/fileprocess/log/dc/ 2016-12-05 16:29:01 2016-12-06 24:00:00]"
	#退出
	exit 1
fi

logfile=$1
startTime=$2" "$3
endTime=$4" "$5


export LANG=en_US.UTF-8
export LC_CTYPE=en_US.UTF-8
CLASSPATH="$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar:$JAVA_HOME/lib/mysql.jar"
export CLASSPATH
PATH=$JAVA_HOME/bin
export PATH
SCRIPT=$0
SCRIPT_PATH=${SCRIPT%/*}
if [ $SCRIPT_PATH == "start.sh" ];
then
SCRIPT_PATH=$PWD
fi

PROGRAM_PATH=$SCRIPT_PATH/../
cd $PROGRAM_PATH

# 脚本该处需要添加环境变量，否则会报错
/opt/FUDE-1.1/java/java/bin/java -jar ./bin/DSRunStat-1.0.3.jar $logfile $startTime $endTime

