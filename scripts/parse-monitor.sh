#!/bin/bash

[ "$#" -lt "2" ] && echo Usage: "$0 MONITOR HOSTNAME RAW_DIRECTORY" && exit 1

MONITOR=`echo $1 | tr '[:upper:]' '[:lower:]' | tr '_' '-'`
HOST=$2
DIR=$3

FN=${DIR}/${RUN_ID}.${HOST}.${MONITOR}
if [ $MONITOR == "nvprof" ]; then
    # nvprof generates 1 or more files, and adds the PID to the filename
    # pick the largest file and rename it so that the raw file can be 
    # downloaded from the web page
    RAW_FN=`ls -S ${FN}* | head -n 1`
    echo Renaming $RAW_FN to $FN
    mv $RAW_FN $FN
    ./parse_nvprof.py $FN
else
   # All python scripts use underscore not dash
   MONITOR=`echo $MONITOR | tr '-' '_'`
  ./parse_${MONITOR}.py $FN
fi

