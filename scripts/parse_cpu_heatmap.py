#!/usr/bin/python

'''
Input:  dstat cpu csv data (e.g. "dstat -t --cpu -C 0,1 --output dstat_fn 1"
Output: json file
'''

import sys
import os
import json
from datetime import datetime

def main(dstat_fn):
    '''
    '''
    with open(dstat_fn, 'r') as fid:
        blob = fid.read()
    fid.close()
    blob = "system" + blob.split('"system"')[1].strip()
    lines = blob.split('\n')
    num_cpu = (len(lines[0].split(',')) - 1)/6 # subtract 1 for time vector
    val_array = [[] for i in range(num_cpu)]
    START = True
    PRINT = False
    HEADER = True
    fields = ['TIME_SEC']
    lines = lines[2:]  # skip 2 header rows
    td_array = []
    for line in lines:
        vals = line.split(',')
        t = datetime.strptime(vals[0], '%d-%m %H:%M:%S')
        if START:
            t0 = t
            START = False
        td_array.append((t - t0).total_seconds())
        for cpu in range(num_cpu):
            cpu_usr = float(vals[cpu*6 + 1])
            cpu_sys = float(vals[cpu*6 + 2])
            val = cpu_usr + cpu_sys
            val_array[cpu].append(val)
    obj = {"labels": td_array}
    obj["datasets"] = []

    for cpu in range(num_cpu - 1, -1, -1):
        data = map(lambda(x): round(x, 1), val_array[cpu])
        obj["datasets"].append({"label": str(cpu), "data": data})
    out_fn = dstat_fn.replace('data/raw', 'data/final')
    out_fn += '.json'
    with open(out_fn, 'w') as fid:
        fid.write(json.dumps(obj))

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        sys.stderr.write("USAGE: ./parse_cpu_heatmap.py <fn>\n")
        sys.exit(1)
    main(sys.argv[1])
