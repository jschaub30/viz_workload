#!/bin/bash

# Default values
threads=2
duration=10
hostnames="localhost"

# Usage information
usage() {
    echo "Simulate a high CPU workload across multiple nodes"
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -t <num>    Number of threads (default: 2)"
    echo "  -d <seconds> Duration in seconds (default: 10)"
    echo "  -h          Display this help and exit"
    echo "  -H <hosts>  Hostnames, separated by commas (default: localhost)"
    echo "              ***configure password-less ssh when invoking multiple nodes***"
    exit 1
}

# Parse options
while getopts ":t:d:H:h" opt; do
    case ${opt} in
        t )
            threads=$OPTARG
            ;;
        d )
            duration=$OPTARG
            ;;
        H )
            hostnames=$OPTARG
            ;;
        h )
            usage
            ;;
        \? )
            echo "Invalid Option: -$OPTARG" 1>&2
            usage
            ;;
        : )
            echo "Invalid Option: -$OPTARG requires an argument" 1>&2
            usage
            ;;
    esac
done
shift $((OPTIND -1))

# Split hostnames into an array
IFS=',' read -r -a hostname_array <<< "$hostnames"

# shellcheck disable=SC2029
for thread in $(seq "$threads"); do
    for HOST in "${hostname_array[@]}"; do
        echo "Loading CPU for $duration seconds on $HOST"
        CMD="taskset -c $(( thread - 1 )) bash -c 'while true; do true; done'"
        ssh "$HOST" "timeout $duration $CMD" &
    done
done

wait
