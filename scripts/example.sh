#!/bin/bash

# Required
export WORKLOAD_NAME=CPU                  # A short name for this type of workload
export DESCRIPTION="Artificial CPU load"  # A description of this particular workload
export WORKLOAD_CMD="./load_cpu.sh"       # The workload to run

# Optional
export WORKLOAD_DIR="."             # The workload working directory
export MEAS_DELAY_SEC=1             # Delay between each measurement
export VERBOSE=1
#export SOURCES="host1 host2"        # space delimited
#export RUNDIR=rundir/EXAMPLE/20161007-162550

./run-and-measure.sh

