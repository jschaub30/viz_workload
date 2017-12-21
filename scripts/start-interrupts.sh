#!/bin/bash

[ $# -ne 2 ] && echo USAGE: $0 TARGET_FN DELAY_SEC && exit 1
TARGET_FN=$1
DELAY_SEC=$2

rm -f $TARGET_FN
STOP_FN=/tmp/${USER}/viz_workload/stop-interrupts
while true
do 
    if [ -e $STOP_FN ]; then
        rm $STOP_FN
        exit 0
    fi
    echo "##TIMESTAMP## $(date +"%Y%m%d-%H%M%S")" >> $TARGET_FN
    cat /proc/interrupts >> $TARGET_FN
    sleep $DELAY_SEC
done
