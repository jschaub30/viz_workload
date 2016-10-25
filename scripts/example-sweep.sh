#!/bin/bash
# This script demonstrates how to sweep a parameter
# and access/view all resulting data from the same web page

# Required variables are WORKLOAD_NAME, DESCRIPTION, & WORKLOAD_CMD
export WORKLOAD_NAME=EXAMPLES        # A short name for this type of workload

# Optional variables (defaults shown here)
export WORKLOAD_DIR="."             # The workload working directory
export MEAS_DELAY_SEC=1             # Delay in seconds between each measurement
export VERBOSE=0                    # Verbosity level 0|1|2  Higher==more messages
# What measurements to collect (space delimited). See 'available-measurements.txt'
export MEASUREMENTS="dstat"         # cpu, memory, io and network vs time

# For sweeps, create a run directory where all files will be saved
# Specify it directly, like this:
#export RUNDIR=path/to/your/directory
# or use this script to create one automatically (recommended)
export RUNDIR=`./create-rundir.sh`

for CPU in 1 2 4; do
  export WORKLOAD_CMD="./load-cpu.sh $CPU"   # The workload to run
  export RUN_ID="NUM_CPU=$CPU"               # Unique for this run
  export DESCRIPTION="CPU load using $CPU CPUs"  # A description of this particular workload
  ./run-and-measure.sh
done

