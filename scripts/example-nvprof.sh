#!/bin/bash
# Example script using the NVIDIA nvprof profiling tool

# Required variables
export WORKLOAD_NAME=EXAMPLES             # A short name for this type of workload
export DESCRIPTION="nvprof measurement example"
export WORKLOAD_CMD="/usr/local/cuda-8.0/samples/1_Utilities/p2pBandwidthLatencyTest/p2pBandwidthLatencyTest"
export MEASUREMENTS="sys-summary nvprof"

./run-and-measure.sh

