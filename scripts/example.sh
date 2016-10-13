#!/bin/bash

# Required variables
export WORKLOAD_NAME=EXAMPLES             # A short name for this type of workload
export DESCRIPTION="Artificial CPU load"  # A description of this particular workload
export WORKLOAD_CMD="./load_cpu.sh"       # The workload to run

# Optional variables (defaults shown here)
export WORKLOAD_DIR="."             # The workload working directory
export MEAS_DELAY_SEC=1             # Delay in seconds between each measurement
export VERBOSE=0                    # Verbosity level 0|1|2  Higher==more messages

./run-and-measure.sh

