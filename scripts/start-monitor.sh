#!/bin/bash

[ "$#" -ne "4" ] && echo Usage: $0 MONITOR HOST RUN_ID DELAY_SEC && exit 1

MONITOR=`echo $1 | tr '[:upper:]' '[:lower:]' | tr '_' '-'`
HOST=$2
DELAY_SEC=$4
[ "$DELAY_SEC" -lt "1" ] && echo Setting DELAY_SEC to 1 instead of $DELAY_SEC \
  && DELAY_SEC=1
TARGET_FN=/tmp/${USER}/pid_monitor/${RUN_ID}.${HOST}.${MONITOR}.csv


# First copy script to all hosts
SCRIPT=start-${MONITOR}.sh
scp $SCRIPT $HOST:/tmp
RUN_CMD="/tmp/$SCRIPT $TARGET_FN $DELAY_SEC"

# Start $MONITOR
DIRNAME=$(dirname $TARGET_FN)

$(ssh $HOST $RUN_CMD) 2>/dev/null &
RC=$?

[ "$RC" -ne 0 ] && echo Problem starting $MONITOR on $HOST && exit 1
exit $RC

