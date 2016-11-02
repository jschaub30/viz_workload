#!/bin/bash

[ $# -ne 2 ] && echo USAGE: $0 TARGET_FN DELAY_SEC && exit 1
TARGET_FN=$1
DELAY_SEC=$2

# Check if dstat is installed
A=`which dstat`
[ "$?" -ne 0 ] && echo ERROR: dstat not found on $HOSTNAME. Exiting... && exit 1

# Check if a copy of this script is already running
NUM=`ps -efa | grep $0 | grep -v "vim\|grep\|ssh" | wc -l`
[ $NUM -gt 2 ] && echo WARNING: $0 appears to be running on $HOSTNAME

# Start dstat capture of all cpu threads
CPU_LIST=`cat /proc/cpuinfo | grep processor | cut -d':' -f2 | perl -pe "s/\s(\d+)\n/\1,/g" | perl -pe "s/,$//"`
rm -f $TARGET_FN

dstat --time --cpu -C $CPU_LIST --output $TARGET_FN $DELAY_SEC 1>/dev/null

