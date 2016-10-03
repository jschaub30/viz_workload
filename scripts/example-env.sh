#!/bin/bash

export WORKLOAD_NAME=EXAMPLE
export DESCRIPTION="Example workload using dd command"
export WORKLOAD_DIR="."             # The workload working directory
export WORKLOAD_CMD="./dd_test.sh"  # The workload to run
export MEAS_DSTAT=1                 # Capture dstat traces for cpu, mem, io & network
export HOSTS="localhost"  # optional
export MEAS_DELAY_SEC=1             # Delay between each measurement

./run-and-measure.sh
