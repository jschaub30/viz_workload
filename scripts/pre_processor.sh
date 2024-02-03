#!/bin/bash

#################### FUNCTION DEFINITIONS ####################

usage() {
  echo 'Requires var. PREP_SCRIPT to be defined/1'
  echo "$0"
  echo
  exit 1
}

#################### END OF FUNCTIONS ####################

[ -z "$PREP_SCRIPT" ] && usage                 ## required!
[ -z "$HOSTS" ] && HOSTS=$(hostname -s) && export HOSTS ## can be localhost only

## simple functionality
##  copy the prep_script to each machine, and run

WORK_DIR=/tmp/${USER}/viz_preprocessor
EXEC_NAME=$(basename "$PREP_SCRIPT")

IFS=',' read -r -a hostname_array <<< "$HOSTS"

# shellcheck disable=SC2029
for HOST in "${hostname_array[@]}"; do
  ssh "$HOST" "mkdir -p $WORK_DIR"
  scp "$PREP_SCRIPT" "${HOST}:${WORK_DIR}/${EXEC_NAME}" >/dev/null
  ssh "$HOST" "chmod 755 ${WORK_DIR}/${EXEC_NAME}"
  ssh "$HOST" "${WORK_DIR}/${EXEC_NAME}"
done


## end
