#!/bin/bash
# Create artificial CPU load for 10 seconds
# 1 copy takes 100% of 1 thread (typically)
#
# USAGE: ./load-cpu.sh NUM_COPIES [HOSTS]
# Examples: 
# ./load-cpu.sh 2 # load 2 threads on localhost
# ./load-cpu.sh 1 host1 host2  # load 1 thread each on host1 and host2

[ $# -eq 0 ] && echo "USAGE: ./load-cpu.sh NUM_COPIES [HOSTS]" && exit 1
NUM_COPIES=$1
if [ $# -eq 1 ]; then 
  HOSTS="$(hostname)"
else
  HOSTS=`echo $@ | cut -d' ' -f2-`
fi

kill_pids(){
    echo Stopping CPU loading
    kill ${PIDS[@]}
}
PIDS=()
trap "kill_pids" SIGTERM SIGINT # Kill loads if stopped early

for N in `seq $NUM_COPIES`; do
  for HOST in $HOSTS; do
    echo Loading CPU for 10 seconds on $HOST
    ssh -t -t $HOST "while true; do true; done" &
    PIDS+=( $! )
  done
done

sleep 10
kill_pids
