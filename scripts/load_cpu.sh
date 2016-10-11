#!/bin/bash

load_cpu() {
    while true
    do
      true
    done
}

echo Loading CPU for 10 seconds
load_cpu &
PID=$!
sleep 10
echo Stopping CPU load
kill $PID

