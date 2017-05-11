#!/bin/bash
# Starts the dstat monitor on the local host
# Measures system cpu, memory, io and network activity

[ $# -ne 2 ] && echo USAGE: $0 TARGET_FN DELAY_SEC && exit 1
TARGET_FN=$1
DELAY_SEC=$2

# Check if dstat is installed
A=`which dstat`
[ "$?" -ne 0 ] && echo ERROR: dstat not found on $HOSTNAME. Exiting... && exit 1
STOP_FN=/tmp/${USER}/viz_workload/stop-sys-summary
rm -f $STOP_FN

# Check if a copy of this script is already running
NUM=`ps -efa | grep $0 | grep -v "vim\|grep\|ssh" | wc -l`
[ $NUM -gt 2 ] && echo WARNING: $0 appears to be running on $HOSTNAME

# Start dstat
DIRNAME=`dirname $TARGET_FN`
mkdir -p $DIRNAME
rm -f $TARGET_FN

dstat --time -v --net --output $TARGET_FN $DELAY_SEC 1>/dev/null &
PID=$!

trap "kill $PID; exit 1" SIGTERM SIGINT # Kill PID on CTRL-C
# Kill on semaphore
while [ ! -e $STOP_FN ]; do
    sleep 1
done

kill $PID
rm -f $STOP_FN

