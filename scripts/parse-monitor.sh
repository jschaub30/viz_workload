#!/bin/bash

[ "$#" -lt "2" ] && echo Usage: "$0 MONITOR HOSTNAME RAW_DIRECTORY" && exit 1
MONITOR=`echo $1 | tr '[:upper:]' '[:lower:]' | tr '_' '-'`
HOST=$2
DIR=$3

FN=${DIR}/${RUN_ID}.${HOST}.${MONITOR}.csv
[ $MONITOR == "dstat" ] && ./parse_dstat.py $FN
[ $MONITOR == "cpu-heatmap" ] && ./parse_cpu_heatmap.py $FN

