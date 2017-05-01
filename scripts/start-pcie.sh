#!/bin/bash

[ $# -ne 2 ] && echo USAGE: $0 TARGET_FN DELAY_SEC && exit 1

TARGET_FN=$1
DELAY_SEC=$2

[ ! -e /usr/sbin/fal_app ] && echo "/usr/sbin/fal_app not found" && exit 1

while [ true ]
do
  /usr/sbin/fal_app show 9797 loading >> $TARGET_FN
  sleep $DELAY_SEC
done

