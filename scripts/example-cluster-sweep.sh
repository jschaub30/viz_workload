#!/bin/bash
# This script demonstrates how to sweep a parameter on 2 hosts
# and access/view all resulting data from the same web page
#
# It's recommended that you setup password-less ssh between all
# machines in your cluster prior to running this script.


# Required variables are WORKLOAD_NAME, DESCRIPTION, & WORKLOAD_CMD
export WORKLOAD_NAME=CLUSTER-SWEEP  # A short name for this type of workload

# Optional variables (defaults shown here)
export WORKLOAD_DIR="."             # The workload working directory
export MEAS_DELAY_SEC=1             # Delay in seconds between each measurement
export VERBOSE=0                    # Verbosity level 0|1|2  Higher==more messages
# What measurements to collect (space delimited). See 'available-measurements.txt'
export MEASUREMENTS="sys-summary"   # cpu, memory, io and network vs time

# To run on hosts other than the local node, export the "HOSTS" variable
# We will simulate this by running on "localhost" and the string returned by
# the "hostname" command
HOSTS="localhost $(hostname)"    # space delimited
export HOSTS

# For sweeps, create a run directory where all files will be saved
# Specify it directly, like this:
#export RUNDIR=path/to/your/directory
# or use this script to create one automatically (recommended)
RUNDIR=$(./create-rundir.sh)
export RUNDIR

## optional: run a preprocessor to avoid measurements being skewed.
##   a good example is to clear the cache
##   the process is run out of the main measurement step
## enable this function by setting up an env. var. w/ name = PREP_SCRIPT
##export PREP_SCRIPT="./example-prep.sh"

for CPU in 1 2 4; do
  # determine whether we need to run preprocessorg
  [ -n "$PREP_SCRIPT" ] && ./pre_processor.sh

  export WORKLOAD_CMD="./load-cpu.sh $CPU"   # The workload to run
  export RUN_ID="NUM_CPU=$CPU"               # Unique for this run
  # A description of this particular workload
  export DESCRIPTION="CPU load using $CPU CPUs on 2 hosts"
  ./run-and-measure.sh
done

