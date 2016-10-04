#!/bin/bash

[ -z "$SLAVES" ] && export SLAVES=$(hostname -s)
[ -z "$MEAS_DELAY_SEC" ] && MEAS_DELAY_SEC=1

./setup_measurement.py > /dev/null

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
  DSTAT_FN=${RAWDIR}/${RUN_ID}.${SLAVE}.dstat.txt
}

start_monitors() {
  debug_message "Starting monitors"
  unset PIDS
  for SLAVE in $SLAVES; do
    define_filenames
    [ "$MEAS_DSTAT" == 1 ] && \
      ./start_monitor.sh dstat $SLAVE $DSTAT_FN $MEAS_DELAY_SEC &
    PIDS="$PIDS $!"
  done
  check_pids $PIDS
}

stop_monitors() {
  debug_message "Stopping monitors"
  unset PIDS
  for SLAVE in $SLAVES; do
    define_filenames
    [ "$MEAS_DSTAT" == 1 ] && \
      ./stop_monitor.sh dstat $SLAVE $DSTAT_FN &
  done
  wait
}

run_workload(){
  debug_message "Working directory: $WORKLOAD_DIR"
  cd "$WORKLOAD_DIR"
  [ $? -ne 0 ] && echo "ERROR Problem changing to $WORKLOAD_DIR" && exit 1
  # check for /usr/bin/time
  /usr/bin/time --verbose ls  2>/dev/null 1>/dev/null
  if [ "$?" -ne "0" ]; then
    echo /usr/bin/time not found.  Exiting ... && exit 1
  fi

  /usr/bin/time --verbose --output=$TIME_FN \
    "$WORKLOAD_CMD 2> >(tee $WORKLOAD_STDERR) 1> >(tee $WORKLOAD_STDOUT)" &
  TIME_PID=$!
  debug_message "Waiting for $TIME_PID to finish"
  wait $TIME_PID
}

#record_state
start_monitors
run_workload
stop_monitors

