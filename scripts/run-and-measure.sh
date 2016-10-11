#!/bin/bash

#################### FUNCTION DEFINITIONS ####################


usage() {
  echo '# Example usage:'
  echo 'export WORKLOAD_NAME=EXAMPLE'
  echo 'export DESCRIPTION="Example 10sec sleep command"'
  echo 'export WORKLOAD_CMD="sleep 10"'
  echo $0
  exit 1
}

debug_message(){
  LEVEL=$1
  MESSAGE=`echo "$@" | cut -d' ' -f2-`
  if [ $LEVEL -le $VERBOSE ]; then
    [ $LEVEL -ne -1 ] && echo "#### VIZ_WORKLOAD ####: $MESSAGE"
    [ $LEVEL -eq -1 ] && echo "#### VIZ_WORKLOAD ERROR! ####: $MESSAGE"
  fi
}

check_pids() { 
  for PID2CHECK in "$@"
  do
    CURRENT_SOURCE=${SOURCE_ARRAY[$PID2CHECK]}
    wait $PID2CHECK
    if [ $? -ne 0 ]
    then 
      debug_message -1 "$CURRENT_SOURCE did not complete successfully. Exiting..."
      exit 1
    fi
  done
}

define_filenames() {
  RAWDIR=${RUNDIR}/data/raw
  DSTAT_FN=${RAWDIR}/${RUN_ID}.${SOURCE}.dstat.csv
}

start_monitors() {
  debug_message 0 "Starting monitors"
  PIDS=()
  SOURCE_ARRAY=()
  for SOURCE in $SOURCES; do
    define_filenames
	debug_message 1 "Starting monitors"
    if [ "$MEAS_DSTAT" == 1 ]; then
      debug_message 1 "Starting dstat on $SOURCE"
      ./start_monitor.sh dstat $SOURCE $DSTAT_FN $MEAS_DELAY_SEC &
      CURRPID=$!
    fi
    SOURCE_ARRAY[$CURRPID]=$SOURCE
    PIDS="$PIDS $CURRPID"
  done
  check_pids ${PIDS[@]}
}

stop_monitors() {
  debug_message 0 "Stopping monitors"
  for SOURCE in $SOURCES; do
    define_filenames
    [ "$MEAS_DSTAT" == 1 ] && debug_message 1 "Stopping dstat on $SOURCE" && \
      ./stop_monitor.sh dstat $SOURCE $DSTAT_FN &
  done
  wait
}

run_workload(){
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
    bash -c "$WORKLOAD_CMD 2> >(tee $WORKLOAD_STDERR) 1> >(tee $WORKLOAD_STDOUT)" &
  TIME_PID=$!
  debug_message 0 "Waiting for workload (pid $TIME_PID) to finish"
  wait $TIME_PID
}

parse_results() {
  for SOURCE in $SOURCES; do
	define_filenames
    debug_message 1 "Parsing dstat data on $SOURCE"
	[ $MEAS_DSTAT -eq 1 ] && debug_message 1 "Parsing dstat data on $SOURCE" && \
      ./parse_dstat.py $DSTAT_FN &
  done
  wait
}

setup_webserver() {
  echo "cd $RUNDIR/html; python -m SimpleHTTPServer 12121" > webserver.sh
  chmod u+x webserver.sh

  # For python simple webserver to work, need soft link to data directory
  CWD=`pwd`
  cd $RUNDIR
  [ ! -e data ] && ln -sf ../data 
  cd $CWD

  IP=$(hostname -I | cut -d' ' -f1)
  echo
  debug_message 0 "All data saved to $RUNDIR"
  debug_message 0 "View the html output using the following command:"
  debug_message 0 "$ ./webserver.sh"
  debug_message 0 "Then navigate to http://${IP}:12121"
  echo
}
stop_all() {
    debug_message -1 "Stopping measurement"
    kill -9 $TIME_PID 2>> $WORKLOAD_STDERR &  # Kill main process if ctrl-c
}

#################### END OF FUNCTIONS ####################

# Required
[ -z "$WORKLOAD_CMD" ] && usage
[ -z "$WORKLOAD_NAME" ] && usage
[ -z "$DESCRIPTION" ] && usage

# Optional
[ -z "$WORKLOAD_DIR" ] && export WORKLOAD_DIR=`pwd`
[ -z "$RUN_ID" ] && export RUN_ID=RUN1
[ -z "$SOURCES" ] && export SOURCES=$(hostname -s)
[ -z "$MEAS_DELAY_SEC" ] && MEAS_DELAY_SEC=1
[ -z "$VERBOSE" ] && VERBOSE=0     # 0|1|2  Higher==more messages

trap 'stop_all' SIGTERM SIGINT # Kill process monitors if killed early

WORKLOAD_NAME=`echo "$WORKLOAD_NAME" | perl -pe "s/ /_/g"` # remove whitespace
export MEAS_DSTAT=1  # Capture dstat traces for cpu, mem, io & network

RUNDIR=`./setup_measurement.py`
[ $? -ne 0 ] && debug_message -1 "Problem setting up measurement. Exiting..." && exit 1
debug_message 0 "All data will be saved in $RUNDIR"


#record_state
start_monitors
run_workload
stop_monitors
parse_results
setup_webserver

