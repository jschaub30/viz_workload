#!/bin/bash

[ $# -ne 2 ] && echo USAGE: $0 TARGET_FN DELAY_SEC && exit 1
TARGET_FN=$1
DELAY_SEC=$2

rm -f $TARGET_FN

NUM_CPU=`cat /proc/cpuinfo | grep processor | wc -l`
CPU_LIST=`seq 0 $((NUM_CPU-1))`
CPU_LIST=`echo $CPU_LIST | tr ' ' ','`
dstat --time --cpu -C $CPU_LIST --output $TARGET_FN $DELAY_SEC

