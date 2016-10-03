#!/bin/bash

# Required
export WORKLOAD_NAME=EXAMPLE
export DESCRIPTION="Example workload using dd command"
export WORKLOAD_DIR="."             # The workload working directory
export WORKLOAD_CMD="./dd_test.sh"  # The workload to run

# Optional
export HOSTS="host1"                # Defaults to "hostname -s"
export MEAS_DELAY_SEC=1             # Delay between each measurement

# Measurements
export MEAS_DSTAT=1                 # Capture dstat traces for cpu, mem, io & network
export MEAS_NMON=1                  # Capture nmon spreadsheet format
