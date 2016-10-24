#!/bin/bash

[ "$#" -lt "2" ] && echo Usage: "$0 MONITOR HOSTNAME [TARGET_PATH]" && exit 1
MONITOR=`echo $1 | tr '[:upper:]' '[:lower:]'`
HOST=$2
SCRIPT=start-${MONITOR}.sh

[ $MONITOR == "ocount" ] && PREFIX="sudo"
[ $MONITOR == "perf" ] && PREFIX="sudo"
[ $MONITOR == "operf" ] && PREFIX="sudo"
[ $MONITOR == "gpu" ] && MONITOR="nvidia-smi"

ssh $HOST "$PREFIX pkill $SCRIPT"
if [ "$#" -eq "3" ]
then
  TARGET_FN=$3
  REMOTE_FN=/tmp/${USER}/pid_monitor/${RUN_ID}.${HOST}.${MONITOR}.csv
  echo Copying $MONITOR data from $HOST:$REMOTE_FN to $TARGET_FN
  scp -r $HOST:$REMOTE_FN $TARGET_FN
  [ "$?" -eq 0 ] && ssh $HOST "$PREFIX rm $REMOTE_FN"
fi

