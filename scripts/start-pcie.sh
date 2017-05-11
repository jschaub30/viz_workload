#!/bin/bash

[ $# -ne 2 ] && echo USAGE: $0 TARGET_FN DELAY_SEC && exit 1

TARGET_FN=$1
DELAY_SEC=$2

# A=`which fal_app`
[ ! -e /usr/sbin/fal_app ] && echo "ERROR: /usr/sbin/fal_app not found on $HOSTNAME" && exit 1

# Record route data at the top of file
/usr/sbin/fal_app show 9797 route > $TARGET_FN

STOP_FN=/tmp/${USER}/viz_workload/stop-pcie

# Record loading data in loop
while [ true ]
do
  if [ -e $STOP_FN ]; then
    rm $STOP_FN
    exit 0
  fi
  TS=`date +%Y%m%d-%H%M%S`
  echo "TIMESTAMP=${TS}" >> $TARGET_FN
  /usr/sbin/fal_app show 9797 loading >> $TARGET_FN
  sleep $DELAY_SEC
done

