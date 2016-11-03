#!/bin/bash
# ./start-summary.sh HOST TARGET_DIR
# This script uses ssh to
# 1. copy the system-summary.sh script to the target $HOST
# 2. capture the system summary on the target $HOST
# 3. copy the resulting html summary to the TARGET_DIR on the local host

[ $# -ne 2 ] && echo Usage: $0 HOST TARGET_DIR && exit 1

HOST=$1
TARGET_DIR=$2
SCRIPT=system-snapshot.sh

# Create remote directory
DIR=/tmp/${USER}/viz_workload
ssh $HOST "mkdir -p $DIR"
[ $? -ne 0 ] && echo "ERROR: Problem creating remote directory. Exiting..." \
  && exit 1

# Copy script to all hosts
scp $SCRIPT ${HOST}:${DIR} > /dev/null
[ $? -ne 0 ] && echo "ERROR: Problem copying $SCRIPT to $HOST:$DIR. Exiting..."\
  && exit 1
# Copy template to all hosts
scp summary-template.html ${HOST}:${DIR} > /dev/null
[ $? -ne 0 ] && echo "ERROR: Problem copying $SCRIPT to $HOST:$DIR. Exiting..."\

# Start script
TARGET_FN=${DIR}/${HOST}.html
CMD="cd ${DIR}; ./${SCRIPT} $TARGET_FN"
ssh $HOST $CMD
[ $? -ne 0 ] && echo "ERROR: Problem running $SCRIPT on $HOST" && exit 1

# Copy file back to local host
scp $HOST:$TARGET_FN $TARGET_DIR >/dev/null
[ $? -ne 0 ] && echo "ERROR: Problem copying $HOST:$TARGET_FN to $TARGET_DIR" && exit 1
exit 0
