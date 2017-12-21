#!/bin/bash

[ $# -ne 2 ] && echo USAGE: $0 TARGET_FN DELAY_SEC && exit 1
TARGET_FN=$1
DELAY_SEC=$2

STOP_FN=/tmp/${USER}/viz_workload/stop-nmon
rm -f $STOP_FN
rm -f $TARGET_FN

A=`which nmon`
[ "$?" -ne 0 ] && echo ERROR: nmon not found on $HOSTNAME. Exiting... && exit 1
nmon -f -c 10000 -F $TARGET_FN -s $DELAY_SEC &
PID=$!

trap "kill $PID; exit 1" SIGTERM SIGINT # Kill PID on CTRL-C
# Kill on semaphore
while [ ! -e $STOP_FN ]; do
    sleep 1
done

kill $PID
rm -f $STOP_FN

