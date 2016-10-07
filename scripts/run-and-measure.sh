#!/bin/bash

# Required
[ -z "$WORKLOAD_CMD" ] && usage
[ -z "$WORKLOAD_NAME" ] && usage
[ -z "$DESCRIPTION" ] && usage

# Optional
[ -z "$WORKLOAD_DIR" ] && export WORKLOAD_DIR=`pwd`
[ -z "$RUN_ID" ] && export RUN_ID=RUN1
[ -z "$SOURCES" ] && export SOURCES=$(hostname -s)
[ -z "$MEAS_DELAY_SEC" ] && MEAS_DELAY_SEC=1

WORKLOAD_NAME=`echo "$WORKLOAD_NAME" | perl -pe "s/ /_/g"` # remove whitespace
export MEAS_DSTAT=1  # Capture dstat traces for cpu, mem, io & network

RUNDIR=`./setup_measurement.py`
[ $? -ne 0 ] && echo "Problem setting up measurement. Exiting..." && exit 1

debug_message(){
  if [ "$VERBOSE" == 1 ]; then
    echo "#### PID MONITOR ####: $@"
  fi
}

check_pids() { 
  for PID2CHECK in "$@"
  do
    wait $PID2CHECK
    if [ $? -ne 0 ]
    then 
      echo "Process $PID2CHECK did not complete successfully. Exiting..."
      exit 1
    fi
  done
}

define_filenames() {
  RAWDIR=${RUNDIR}/data/raw
  DSTAT_FN=${RAWDIR}/${RUN_ID}.${SOURCE}.dstat.csv
}

start_monitors() {
  debug_message "Starting monitors"
  unset PIDS
  for SOURCE in $SOURCES; do
    define_filenames
    [ "$MEAS_DSTAT" == 1 ] && \
      ./start_monitor.sh dstat $SOURCE $DSTAT_FN $MEAS_DELAY_SEC &
    PIDS="$PIDS $!"
  done
  check_pids $PIDS
}

stop_monitors() {
  debug_message "Stopping monitors"
  for SOURCE in $SOURCES; do
    define_filenames
    [ "$MEAS_DSTAT" == 1 ] && \
      ./stop_monitor.sh dstat $SOURCE $DSTAT_FN &
  done
  wait
}

run_workload(){
  debug_message "Working directory: $WORKLOAD_DIR"
  debug_message "Running this command: $WORKLOAD_CMD"
  cd "$WORKLOAD_DIR"
  [ $? -ne 0 ] && echo "ERROR Problem changing to $WORKLOAD_DIR" && exit 1
  # check for /usr/bin/time
  /usr/bin/time --verbose ls  2>/dev/null 1>/dev/null
  if [ "$?" -ne "0" ]; then
    echo /usr/bin/time not found.  Exiting ... && exit 1
  fi
  WORKLOAD_STDOUT=$RUNDIR/data/raw/${RUN_ID}.workload.stdout.txt
  WORKLOAD_STDERR=$RUNDIR/data/raw/${RUN_ID}.workload.stderr.txt
  TIME_FN=$RUNDIR/data/raw/${RUN_ID}.time.txt
  /usr/bin/time --verbose --output=$TIME_FN \
    bash -c "$WORKLOAD_CMD 2> >(tee $WORKLOAD_STDERR) 1> >(tee $WORKLOAD_STDOUT)" &
  TIME_PID=$!
  debug_message "Waiting for $TIME_PID to finish"
  wait $TIME_PID
}

#record_state
start_monitors

run_workload
stop_monitors
for SOURCE in $SOURCES; do
  define_filenames
  ./parse_dstat.py $DSTAT_FN &
done
wait

