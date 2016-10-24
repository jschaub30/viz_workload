#!/bin/bash

[ $# -ne 2 ] && echo USAGE: $0 TARGET_FN DELAY_SEC && exit 1
TARGET_FN=$1
DELAY_SEC=$2

rm -f $TARGET_FN

nmon -f -c 10000 -F $TARGET_FN -s $DELAY_SEC

