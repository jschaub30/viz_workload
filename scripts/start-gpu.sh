#!/bin/bash
# Starts the nvidia-smi monitor on the local host
# Measures gpu and memory utilization and power draw

[ $# -ne 2 ] && echo USAGE: $0 TARGET_FN DELAY_SEC && exit 1
TARGET_FN=$1
DELAY_SEC=$2

# Check if CUDA is installed
A=`which nvidia-smi`
[ "$?" -ne 0 ] && echo ERROR: nvidia-smi not found on $HOSTNAME. Exiting... && exit 1

# Check if a copy of this script is already running
NUM=`ps -efa | grep $0 | grep -v "vim\|grep\|ssh" | wc -l`
[ $NUM -gt 2 ] && echo WARNING: $0 appears to be running on $HOSTNAME

STOP_FN=/tmp/${USER}/viz_workload/stop-gpu
rm -f $STOP_FN

# Start nvprof
DIRNAME=`dirname $TARGET_FN`
mkdir -p $DIRNAME
rm -f $TARGET_FN

nvidia-smi \
    --query-gpu=timestamp,index,name,utilization.gpu,utilization.memory,power.draw \
    --format=csv --loop=$DELAY_SEC > $TARGET_FN &
PID=$!

trap "kill $PID; exit 1" SIGTERM SIGINT # Kill PID on CTRL-C
# Kill on semaphore
while [ ! -e $STOP_FN ]; do
    sleep 1
done

kill $PID
rm -f $STOP_FN

