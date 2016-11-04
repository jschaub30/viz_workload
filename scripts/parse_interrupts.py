#!/usr/bin/python

'''
Input:  raw data from /proc/interrupts
Output: json timeseries file with total interrupts per cpu thread
'''

import sys
import os
import json
import re
from datetime import datetime
from common import csv_to_json

t0 = -1
def format_line(lines, prev_interrupts):
    '''
    Parse and calculate raw interrupt count for each CPU, then return csv string
    with difference between current and previous count
    '''
    global t0
    # Read timestamp
    t = datetime.strptime(lines[0], '%Y%m%d-%H%M%S')
    if t0 == -1: t0 = t
    t_sec = (t - t0).total_seconds()

    # Read number of cpus
    cpu_list = lines[1].split()
    num_cpu = len(cpu_list)
    interrupts = False
    irqs = []  # IRQ number in each row

    # Parse raw interrupt count for each IRQ. Sum all together for each core
    for line in lines[2:]:
        regex_str = '\s*(\w+):\s+(.*)'
        m = re.match(regex_str, line)
        if m:
            # Raw interrupt count for this IRQ at this time
            vals = map(int, m.groups()[1].split()[:num_cpu])
            if not interrupts:
                # First line
                irqs.append(m.groups()[0])
                interrupts = vals
            else:
                # Sum interrupts generated on each core
                interrupts = [i + j for i, j in zip(vals, interrupts)]

    if prev_interrupts:
        # Calculate the difference between current and previous interrupts
        data = ([i - j for i, j in zip(interrupts, prev_interrupts)])
        csv_line = '%g,%s\n' % (t_sec, ",".join([str(i) for i in data]))
        return (csv_line, interrupts)
    else:
        #t0 = -1  # Reset once since we start on 2nd timestamp
        return ('', interrupts)

def main(fn):
    '''
    First sum all the interrupts on a given CPU thread for a particular timestamp
    Then subtract the total interrupts from previous timestamp
    '''
    with open(fn, 'r') as fid:
        blob = fid.read()
    blobs = blob.split('##TIMESTAMP## ')[1:]
    lines = blobs[0].split('\n')
    cpu_list = lines[1].split()
    csv_str = 'time.sec,' + ','.join(cpu_list) + '\n'
    interrupts = False
    for blob in blobs:
        try:
           (csv_line, interrupts) = format_line(blob.split('\n'), interrupts)
           csv_str += csv_line
        except Exception as e:
            err_str = "Problem extracting entry from %s\n" % fn
            err_str += "Error is %s\nEntry is %s\n" % (str(e), blob[:400])
            sys.stderr.write(err_str)
            sys.exit(1)

    out_fn = fn.replace('data/raw', 'data/final')
    out_fn += '.csv'
    with open(out_fn, 'w') as fid:
        fid.write(csv_str)

    obj = csv_to_json(csv_str)
    out_fn = out_fn.replace('.csv', '.json')
    with open(out_fn, 'w') as fid:
        fid.write(json.dumps(obj))

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        sys.stderr.write("USAGE: ./parse_interrupts.py <fn>\n")
        sys.exit(1)
    main(sys.argv[1])
