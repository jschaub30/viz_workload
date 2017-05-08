#!/bin/bash
# This script demonstrates how to collect PCIE measurements across 2 hosts
# using the CONTINUE_ON_ERROR option (needed when pcie app is only available
# on 1 host.
#
# It's recommended that you setup password-less ssh between all
# machines in your cluster prior to running this script.


# Required variables are WORKLOAD_NAME, DESCRIPTION, & WORKLOAD_CMD
export WORKLOAD_NAME=EXAMPLES
export DESCRIPTION="CPU load using $CPU CPUs on 2 hosts"
export WORKLOAD_CMD="sleep 10"

# Optional variables (defaults shown here)
export WORKLOAD_DIR="."             # The workload working directory
export MEAS_DELAY_SEC=1             # Delay in seconds between each measurement
export VERBOSE=0                    # Verbosity level 0|1|2  Higher==more messages
# What measurements to collect (space delimited). See 'available-measurements.txt'
export MEASUREMENTS="sys-summary pcie"
export CONTINUE_ON_ERROR=1  # continue when some hosts can't start monitor

export HOSTS="localhost pcie_host"

./run-and-measure.sh

