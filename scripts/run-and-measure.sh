#!/bin/bash

#################### FUNCTION DEFINITIONS ####################

usage() {
  echo '# Example usage:'
  echo 'export WORKLOAD_NAME=EXAMPLE'
  echo 'export DESCRIPTION="Example 10sec sleep command"'
  echo 'export WORKLOAD_CMD="sleep 10"'
  echo "$0"
  echo
  echo See example*.sh
  exit 1
}

# Required parameters
[ -z "$WORKLOAD_CMD" ] && usage
[ -z "$WORKLOAD_NAME" ] && usage
[ -z "$DESCRIPTION" ] && usage

# Optional parameters.  Define default values
[ -z "$MEASUREMENTS" ] && export MEASUREMENTS=`sys-summary`
[ -z "$WORKLOAD_DIR" ] && export WORKLOAD_DIR=`pwd`
[ -z "$RUN_ID" ] && export RUN_ID=RUN1
[ -z "$HOSTS" ] && export HOSTS=$(hostname -s)
[ -z "$MEAS_DELAY_SEC" ] && MEAS_DELAY_SEC=1
[ -z "$VERBOSE" ] && VERBOSE=0     # 0|1|2  Higher==more messages

WORKLOAD_NAME=`echo "$WORKLOAD_NAME" | perl -pe "s/ /_/g"` # remove whitespace
CWD=`pwd`

######## Functions ########
debug_message(){
  LEVEL=$1
  MESSAGE=`echo "$@" | cut -d' ' -f2-`
  if [ $LEVEL -le $VERBOSE ]; then
    datetime="$(date +'%Y-%m-%d %H:%M:%S')"  # Get current date and time
    [ $LEVEL -ne -1 ] && echo "#### VIZ_WORKLOAD [$datetime] ####: $MESSAGE"
    [ $LEVEL -eq -1 ] && echo "#### VIZ_WORKLOAD ERROR! [$datetime] ####: $MESSAGE"
  fi
}

check_pids() {
  for PID2CHECK in "$@"
  do
    CURRENT_MSG=${MSG_ARRAY[$PID2CHECK]}
    wait $PID2CHECK
    RC=$?
    if [ $RC -ne 0 ]
    then
      debug_message -1 "$CURRENT_MSG did not complete successfully."
      if [ -z "$CONTINUE_ON_ERROR" ]; then
        debug_message -1 "Return code=$RC   Exiting..."
        exit 1
      else
        debug_message -1 "Continuing despite error"
      fi
    fi
  done
}

# $HOSTS is a comma-delimited string
IFS=',' read -r -a hostname_array <<< "$HOSTS"

system_snapshot() {
  debug_message 0 "Collecting system snapshot of $HOSTS"
  PIDS=()
  MSG_ARRAY=()
  for HOST in "${hostname_array[@]}"; do
    if [ ! -e "$RUNDIR/html/${HOST}.html" ]; then
      MSG="Collecting system snapshot of $HOST"
      debug_message 1 "$MSG"
      ./start-snapshot.sh "$HOST" "$RUNDIR/html" &
      CURRPID=$!
      MSG_ARRAY[$CURRPID]="$MSG"
      PIDS+=("$CURRPID")
    fi
  done
  check_pids ${PIDS}
}

start_monitors() {
  debug_message 0 "Starting monitors on $HOSTS"
  PIDS=()
  MSG_ARRAY=()
  for HOST in "${hostname_array[@]}"; do
    for MONITOR in $MEASUREMENTS; do
      if [ $MONITOR == "nvprof" ]; then
        export NVPROF=1
      else
        MSG="Starting $MONITOR on host $HOST"
        debug_message 1 $MSG
        ./start-monitor.sh $MONITOR $HOST $RUN_ID $MEAS_DELAY_SEC &
        CURRPID=$!
        MSG_ARRAY[$CURRPID]="$MSG"
        # PIDS="$PIDS $CURRPID"
        PIDS+=("$CURRPID")
      fi
    done
  done
  check_pids ${PIDS}
}

stop_monitors() {
  debug_message 0 "Stopping monitors on $HOSTS"
  PIDS=()
  MSG_ARRAY=()
  for HOST in "${hostname_array[@]}"; do
    for MONITOR in $MEASUREMENTS; do
      if [ $MONITOR != "nvprof" ]; then
        MSG="Starting $MONITOR on host $HOST"
        debug_message 1 $MSG
        ./stop-monitor.sh $MONITOR $HOST $RUN_ID ${RUNDIR}/data/raw &
        CURRPID=$!
        MSG_ARRAY[$CURRPID]="$MSG"
        PIDS="$PIDS $CURRPID"
        sleep 0.2
      fi
    done
  done
  check_pids ${PIDS}
}

parse_results() {
  cd $CWD
  debug_message 0 "Parsing results on $HOSTS"
  PIDS=()
  MSG_ARRAY=()
  for HOST in "${hostname_array[@]}"; do
    for MONITOR in $MEASUREMENTS; do
      MSG="Parsing $MONITOR on host $HOST"
      debug_message 1 $MSG
      ./parse-monitor.sh $MONITOR $HOST ${RUNDIR}/data/raw
      CURRPID=$!
      MSG_ARRAY[$CURRPID]="$MSG"
      PIDS="$PIDS $CURRPID"
    done
  done
  check_pids ${PIDS}
}

run_workload(){
  if [ "$NVPROF" == 1 ]; then
    NVBIN="/usr/local/cuda-8.0/bin/nvprof"
    if [ ! -e $NVBIN ]; then
      NVBIN=`which nvprof`
      [ $? -ne 0 ] && debug_message -1 "Didn't find nvprof binary" && exit 1
    fi
    HOST=`echo $HOSTS | cut -d " " -f 1`
    NVLOG=$RUNDIR/data/raw/${RUN_ID}.${HOST}.nvprof.'%p'
    WORKLOAD_CMD="$NVBIN --csv --print-gpu-trace --log-file $NVLOG $WORKLOAD_CMD"
  fi
  debug_message 0 "Working directory: $WORKLOAD_DIR"
  debug_message 0 "Running this command: $WORKLOAD_CMD"
  cd "$WORKLOAD_DIR"
  [ $? -ne 0 ] && debug_message -1 "Problem changing to $WORKLOAD_DIR" && exit 1
  # check for /usr/bin/time
  /usr/bin/time --verbose ls  2>/dev/null 1>/dev/null
  if [ "$?" -ne "0" ]; then
    MSG="/usr/bin/time not found.  Run 'sudo apt-get install time' Exiting..."
    debug_message -1 $MSG && exit 1
  fi
  WORKLOAD_STDOUT=$RUNDIR/data/raw/${RUN_ID}.stdout.txt
  WORKLOAD_STDERR=$RUNDIR/data/raw/${RUN_ID}.stderr.txt
  TIME_FN=$RUNDIR/data/raw/${RUN_ID}.time.txt
  /usr/bin/time --verbose --output=$TIME_FN \
    bash -c "${WORKLOAD_CMD[@]} 2> >(tee $WORKLOAD_STDERR) 1> >(tee $WORKLOAD_STDOUT)" &
  TIME_PID=$!
  debug_message 0 "Waiting for workload (pid $TIME_PID) to finish"
  wait $TIME_PID
  RC=$?
  [ $RC -ne 0 ] && debug_message 0 "WARNING: Non-zero exit status (=$RC) from workload"
  cd $CWD
}

setup_webserver() {
  echo "cd $RUNDIR/html; python3 -m http.server 12121" > webserver.sh
  chmod u+x webserver.sh

  # For python simple webserver to work, need soft link to data directory
  cd $RUNDIR
  [ ! -e data ] && ln -sf ../data
  cd $CWD

  IP=$(hostname -I | cut -d' ' -f1)
  echo
  debug_message 0 "All data saved to $RUNDIR"
  debug_message 0 "View the html output using the following commands:"
  debug_message 0 "cd $CWD"
  debug_message 0 "$ ./webserver.sh"
  debug_message 0 "Then navigate to http://${IP}:12121"
  echo
}

stop_all() {
  debug_message -1 "Stopping workload"
  pkill -TERM -P $TIME_PID 2>> $WORKLOAD_STDERR & # Kill main process if ctrl-c
}

#################### END OF FUNCTIONS ####################
trap 'stop_all' SIGTERM SIGINT # Kill process monitors if killed early
RUNDIR=`./setup_measurement.py`
[ $? -ne 0 ] && debug_message -1 "Problem setting up measurement. Exiting..." && exit 1
debug_message 0 "All data will be saved in $RUNDIR"

system_snapshot
start_monitors
run_workload
stop_monitors
parse_results
setup_webserver

