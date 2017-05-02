#!/bin/bash

[ "$#" -lt "2" ] && echo Usage: "$0 MONITOR HOSTNAME RAW_DIRECTORY" && exit 1
MONITOR=`echo $1 | tr '[:upper:]' '[:lower:]' | tr '_' '-'`
HOST=$2
DIR=$3

FN=${DIR}/${RUN_ID}.${HOST}.${MONITOR}
[ $MONITOR == "sys-summary" ] && ./parse_sys_summary.py $FN
[ $MONITOR == "cpu-heatmap" ] && ./parse_cpu_heatmap.py $FN
[ $MONITOR == "interrupts" ] && ./parse_interrupts.py $FN
[ $MONITOR == "gpu" ] && ./parse_gpu.py $FN
[ $MONITOR == "pcie" ] && ./parse_pcie.py $FN

