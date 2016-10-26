#!/usr/bin/python

'''
Input:  raw data from /proc/interrupts
Output: json file
'''

import sys
import os
import json
import re
from datetime import datetime


def main(fn):
    '''
    First sum all the interrupts on a given CPU thread for a particular timestamp
    Then subtract the total interrupts from previous timestamp
    '''
    with open(fn, 'r') as fid:
        lines = fid.readlines()
    vals = -1
    num_cpu = -1
    t0 = -1
    interrupts = False
    all_interrupts = []
    all_times = []
    datasets = []
    for line in lines:
        if re.match('##TIMESTAMP##', line):
            t = datetime.strptime(line.split(' ')[1].strip(), '%Y%m%d-%H%M%S')
            if t0 == -1: t0 = t
            all_times.append((t - t0).total_seconds())
            start_line = True
            if interrupts and prev_interrupts:
                # Calculate difference in count from previous timestamp
                data = ([i - j for i, j in zip(interrupts, prev_interrupts)])
                datasets.append({"data": data, "label": all_times[-1]})
        elif num_cpu == -1 and re.match('\s+CPU', line):
            num_cpu = len(line.split('CPU')) - 1
        else:
            m = re.match('\s*(\w+):\s+(\d+)\s+(\d+)\s+(.*)', line)
            if m:
                # Raw interrupt count for this IRQ at this time
                vals = map(int, m.groups()[1:num_cpu + 1])
                if start_line:
                    prev_interrupts = interrupts
                    interrupts = vals
                    start_line = False
                else:
                    # Total interrupt count for each CPU thread
                    interrupts = [i + j for i, j in zip(vals, interrupts)]

    if interrupts and prev_interrupts:
        # Get last data point
        data = ([i - j for i, j in zip(interrupts, prev_interrupts)])
        datasets.append({"data": data, "label": all_times[-1]})
    obj = {"labels": all_times, "datasets": datasets}
    out_fn = fn.replace('data/raw', 'data/final') + '.json'
    with open(out_fn, 'w') as fid:
        fid.write(json.dumps(obj))

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        sys.stderr.write("USAGE: ./parse_interrupts.py <fn>\n")
        sys.exit(1)
    main(sys.argv[1])
