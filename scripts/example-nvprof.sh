#!/bin/bash

# Required variables
export WORKLOAD_NAME=EXAMPLES             # A short name for this type of workload
export DESCRIPTION="nvprof measurement example"
export WORKLOAD_CMD="/usr/local/cuda-8.0/samples/1_Utilities/p2pBandwidthLatencyTest/p2pBandwidthLatencyTest"

# Optional variables (defaults shown here)
export WORKLOAD_DIR="."             # The workload working directory
export MEAS_DELAY_SEC=1             # Delay in seconds between each measurement
export VERBOSE=0                    # Verbosity level 0|1|2  Higher==more messages
# What measurements to collect (space delimited). See 'available-measurements.txt'
export MEASUREMENTS="sys-summary nvprof"         # cpu, memory, io and network vs time

./run-and-measure.sh

