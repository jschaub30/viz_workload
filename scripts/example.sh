#!/bin/bash

export WORKLOAD_NAME=EXAMPLE
export DESCRIPTION="Example workload using dd command"
export WORKLOAD_DIR="."             # The workload working directory
export WORKLOAD_CMD="sleep 20"  # The workload to run
export MEAS_DSTAT=1                 # Capture dstat traces for cpu, mem, io & network
export MEAS_DELAY_SEC=1             # Delay between each measurement
export RUNDIR=rundir/EXAMPLE/20161004-115026
#export RUNDIR=$(./setup_measurement.py)
#echo $RUNDIR

./run-and-measure.sh

