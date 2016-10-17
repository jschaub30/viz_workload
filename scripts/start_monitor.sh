#!/bin/bash

[ "$#" -ne "4" ] && echo Usage: $0 MONITOR HOSTNAME TARGET_FN DELAY_SEC && exit 1

MONITOR=$1
HOST=$2
DELAY_SEC=$4
[ "$DELAY_SEC" -lt "1" ] && echo Setting DELAY_SEC to 1 instead of $DELAY_SEC \
  && DELAY_SEC=1

TARGET_FN=/tmp/${USER}/pid_monitor/$(basename $3)

[ "$MONITOR" == "dstat" ] && \
  RUN_CMD="dstat --time -v --net --output $TARGET_FN $DELAY_SEC"

[ "$MONITOR" == "nmon" ] && \
  RUN_CMD="nmon -f -c 10000 -F $TARGET_FN -s $DELAY_SEC"

if [ "$MONITOR" == "cpu_heatmap" ]
then
  NUM_CPU=`cat /proc/cpuinfo | grep processor | wc -l`
  CPU_LIST=`seq 0 $((NUM_CPU-1))`
  CPU_LIST=`echo $CPU_LIST | tr ' ' ','`
  RUN_CMD="dstat --time --cpu -C $CPU_LIST --output $TARGET_FN $DELAY_SEC"
  # redefine MONITOR for test below
  MONITOR="dstat"
fi

if [ "$MONITOR" == "gpu" ]
then
  MONITOR="nvidia-smi"
  RUN_CMD="nvidia-smi \
    --query-gpu=timestamp,index,name,utilization.gpu,utilization.memory,power.draw \
    --format=csv --filename=$TARGET_FN --loop=$DELAY_SEC"
fi

# Collect data over ssh.  Store in /tmp directory
# Check if monitor is installed
ssh $HOST "which $MONITOR" > /dev/null
[ "$?" -ne 0 ] && echo ERROR: Problem starting $MONITOR on $HOST. Exiting... \
  && exit 1

# Check to see if monitor is already running
RC=$(ssh $HOST "ps -efa | grep $MONITOR | grep -v 'grep\|vim\|start_monitor' | wc -l")
[ $RC -ne 0 ] && echo WARNING: $MONITOR appears to be running on $HOST.

# Start $MONITOR
DIRNAME=$(dirname $TARGET_FN)
REMOTE_CMD="mkdir -p $DIRNAME; rm -f $TARGET_FN; $RUN_CMD"

$(ssh $HOST $REMOTE_CMD) 2>/dev/null &
RC=$?

[ "$RC" -ne 0 ] && echo Problem starting $MONITOR on $HOST && exit 1
exit $RC
#echo Successfully started $MONITOR on $HOST

