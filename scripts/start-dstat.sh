#!/bin/bash

[ $# -ne 2 ] && echo USAGE: $0 TARGET_FN DELAY_SEC && exit 1
TARGET_FN=$1
DELAY_SEC=$2

rm -f $TARGET_FN
A=`which dstat`
[ "$?" -ne 0 ] && echo ERROR: Problem starting dstat. Exiting... && exit 1
NUM=`ps -efa | grep dstat | grep -v 'grep\|vim\|start' | wc -l`
[ $NUM -ne 0 ] && echo WARNING: dstat appears to be running on $HOSTNAME

DIRNAME=`dirname $TARGET_FN`
mkdir -p $DIRNAME

dstat --time -v --net --output $TARGET_FN $DELAY_SEC 1>/dev/null

