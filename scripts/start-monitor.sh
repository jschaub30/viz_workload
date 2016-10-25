#!/bin/bash
# ./start-monitor MONITOR HOST RUN_ID DELAY_SEC
# This script uses ssh to
# 1. copy the start-${MONITOR}.sh script to the target $HOST
# 2. start the start-${MONITOR}.sh on the target $HOST

[ "$#" -ne "4" ] && echo Usage: $0 MONITOR HOST RUN_ID DELAY_SEC && exit 1

MONITOR=`echo $1 | tr '[:upper:]' '[:lower:]' | tr '_' '-'`
HOST=$2
RUN_ID=$3
DELAY_SEC=$4

SCRIPT=start-${MONITOR}.sh
[ ! -e $SCRIPT ] && echo "File $SCRIPT does not exist. Exiting..." && exit 1

# Create remote directory
DIR=/tmp/${USER}/viz_workload
ssh $HOST "mkdir -p $DIR"
[ $? -ne 0 ] && echo "ERROR: Problem creating remote directory. Exiting..." \
  && exit 1

# Copy script to all hosts
scp $SCRIPT ${HOST}:${DIR} > /dev/null
[ $? -ne 0 ] && echo "ERROR: Problem copying $SCRIPT to $HOST:$DIR. Exiting..."\
  && exit 1

# Start $MONITOR
[ $DELAY_SEC -lt 1 ] && echo Setting DELAY_SEC to 1 instead of $DELAY_SEC \
  && DELAY_SEC=1
TARGET_FN=${DIR}/${RUN_ID}.${HOST}.${MONITOR}.csv
CMD="${DIR}/${SCRIPT} $TARGET_FN $DELAY_SEC"
ssh -t -t $HOST $CMD &
# Using -t -t option from http://bit.ly/2eGy8iE

PID=$!

sleep 0.25 # Sleep 250ms then check if PID still exists before exiting
[ ! -e /proc/$PID ] && echo ERROR: Problem starting $MONITOR on $HOST && exit 1
exit 0
