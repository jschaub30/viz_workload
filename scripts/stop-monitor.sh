#!/bin/bash
# USAGE: ./stop-monitor.sh MONITOR HOST [RUN_ID TARGET_DIR]
# This script uses ssh to:
# 1. kill the start-${MONITOR}.sh script on $HOST
# 2. (optional) copy the file to $TARGET_DIR on the local host

[ $# -lt 2 ] && echo Usage: "$0 MONITOR HOST [RUN_ID TARGET_PATH]" && exit 1

MONITOR=`echo $1 | tr '[:upper:]' '[:lower:]' | tr '_' '-'`
HOST=$2

# Kill the ssh process attached to the start script on $HOST
PREFIX=""
SCRIPT=start-${MONITOR}.sh

# Write semaphore to directory, then wait for monitor to stop
DIR=/tmp/${USER}/viz_workload
CMD="mkdir -p ${DIR} && touch ${DIR}/stop-${MONITOR}"
ssh $HOST "$CMD"
sleep 2

# Copy the file from remote host to local target directory
if [ $# -eq 4 ]; then
  RUN_ID=$3
  TARGET_DIR=$4
  DIR=/tmp/${USER}/viz_workload
  REMOTE_FN=${DIR}/${RUN_ID}.${HOST}.${MONITOR}
  echo Copying $MONITOR data from ${HOST}:${REMOTE_FN} to $TARGET_DIR
  scp $HOST:$REMOTE_FN $TARGET_DIR >/dev/null
  RC=$?
  if [ $RC -eq 0 ]; then
    # remove remote file
    ssh $HOST "$PREFIX rm $REMOTE_FN"
  else
    echo Problem copying ${HOST}:${REMOTE_FN} to $TARGET_DIR Exiting...
    exit 1
  fi
fi

