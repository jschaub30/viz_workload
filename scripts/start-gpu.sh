#!/bin/bash
# Starts the nvidia-smi monitor on the local host
# Measures gpu and memory utilization and power draw

[ $# -ne 2 ] && echo USAGE: $0 TARGET_FN DELAY_SEC && exit 1
TARGET_FN=$1
DELAY_SEC=$2

# Check if CUDA is installed
A=`which nvidia-smi`
[ "$?" -ne 0 ] && echo ERROR: nvprof not found on $HOSTNAME. Exiting... && exit 1

# Check if a copy of this script is already running
NUM=`ps -efa | grep $0 | grep -v "vim\|grep\|ssh" | wc -l`
[ $NUM -gt 2 ] && echo WARNING: $0 appears to be running on $HOSTNAME

# Start nvprof
DIRNAME=`dirname $TARGET_FN`
mkdir -p $DIRNAME
rm -f $TARGET_FN

nvidia-smi \
    --query-gpu=timestamp,index,name,utilization.gpu,utilization.memory,power.draw \
    --format=csv --filename=$TARGET_FN --loop=$DELAY_SEC

