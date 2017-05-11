#!/usr/bin/env python

'''
Input:  raw data from /proc/interrupts
Output: json timeseries file with total interrupts per cpu thread
'''

import sys
import json
import re
from datetime import datetime
from common import csv_to_json

def parse_raw_interrupts(raw_fn):
    '''
    Read file, parse each entry at a particular timestamp, sum for each CPU,
    and calculate the difference from the previous timestamp
    '''
    with open(raw_fn, 'r') as fid:
        blob = fid.read()
    blobs = blob.split('##TIMESTAMP## ')[1:]
    lines = blobs.pop(0).split('\n')
    time0, prev_interrupts = parse_blob(lines)
    cpu_list = lines[1].split()
    csv_str = 'time.sec,' + ','.join(cpu_list) + '\n'  # Header
    for blob in blobs:
        try:
            time, interrupts = parse_blob(blob.split('\n'))
            t_sec = (time - time0).total_seconds()
            data = ([i - j for i, j in zip(interrupts, prev_interrupts)])
            csv_line = '%g,%s\n' % (t_sec, ",".join([str(i) for i in data]))
            csv_str += csv_line
            prev_interrupts = interrupts
        except Exception as error:
            err_str = "Problem extracting entry from %s\n" % raw_fn
            err_str += "Error is %s\nEntry is %s\n" % (str(error), blob[:400])
            sys.stderr.write(err_str)
            sys.exit(1)
    return csv_str

def parse_blob(lines):
    '''
    Parse and calculate raw interrupt count for each CPU, summed over all
    interrupts
    '''
    # Read timestamp
    time = datetime.strptime(lines[0], '%Y%m%d-%H%M%S')

    # Read number of cpus
    cpu_list = lines[1].split()
    num_cpu = len(cpu_list)
    interrupts = False

    # Parse raw interrupt count for each IRQ. Sum all together for each core
    for line in lines[2:]:
        if ':' in line:
            line = line.split(':')[1].split()
            # Raw interrupt count for this IRQ at this time
            try:
                vals = [int(line[i]) for i in range(num_cpu)]
            except:
                continue
            if not interrupts:
                # First line
                interrupts = vals
            else:
                # Sum interrupts generated on each core
                interrupts = [i + j for i, j in zip(vals, interrupts)]

    return (time, interrupts)

def main(raw_fn):
    '''
    First sum all the interrupts on a given CPU thread for a particular timestamp
    Then subtract the total interrupts from previous timestamp
    '''
    csv_str = parse_raw_interrupts(raw_fn)

    out_fn = raw_fn.replace('data/raw', 'data/final')
    out_fn += '.csv'
    with open(out_fn, 'w') as fid:
        fid.write(csv_str)

    obj = csv_to_json(csv_str)
    out_fn = out_fn.replace('.csv', '.json')
    with open(out_fn, 'w') as fid:
        fid.write(json.dumps(obj))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("USAGE: ./parse_interrupts.py <fn>\n")
        sys.exit(1)
    main(sys.argv[1])
