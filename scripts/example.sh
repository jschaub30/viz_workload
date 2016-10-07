#!/bin/bash

# Required
export WORKLOAD_NAME=SLEEP
export DESCRIPTION="Example sleep command"
export WORKLOAD_CMD="sleep 20"  # The workload to run

# Optional
export WORKLOAD_DIR="."             # The workload working directory
export MEAS_DELAY_SEC=1             # Delay between each measurement
export VERBOSE=1
#export SOURCES="host1 host2"        # space delimited
#export RUNDIR=rundir/EXAMPLE/20161007-162550

./run-and-measure.sh

