#!/bin/bash

NUM_COPIES=1
[ $# -gt 0 ] && NUM_COPIES=$1

load_cpu() {
    while true
    do
      true
    done
}

PIDS=()
for N in `seq $NUM_COPIES`; do
  echo Loading CPU for 10 seconds
  load_cpu &
  PIDS+=( $! )
done
sleep 10
echo Stopping CPU load
kill ${PIDS[@]}

