#!/usr/bin/env python

'''
Input:  dstat cpu csv data (e.g. "dstat -t --cpu -C 0,1 --output dstat_fn 1"
Output: json file
'''

import sys
import os
import json
from datetime import datetime
from common import csv_to_json

def parse_line(line):
    fields = line.split(',')
    t = datetime.strptime(fields.pop(0), '%d-%m %H:%M:%S')
    vals = []
    # for each CPU, fields are:
    # "usr","sys","idl","wai","hiq","siq"
    while fields:
        cpu_usr = float(fields[0])
        cpu_sys = float(fields[1])
        val = cpu_usr + cpu_sys
        vals.append(val)
        fields = fields[6:]
    return (t, vals)

def main(dstat_fn):
    '''
    First parse into CSV string, then convert to JSON
    '''
    with open(dstat_fn, 'r') as fid:
        blob = fid.read()
    fid.close()
    blob = "system" + blob.split('"system"')[1].strip()
    lines = blob.split('\n')
    line = lines.pop(0)
    cpu_list = [i.strip(' usage",,,,,') for i in line.split(',"')[1:]]
    csv_str = 'time.sec,' + ','.join(cpu_list) + '\n'
    line = lines.pop(0)  # header row
    # Parse first line and set t0
    (t0, vals) = parse_line(lines.pop(0))
    csv_str += '0,' + ','.join([str(val) for val in vals]) + '\n'

    while lines:
        (t, vals) = parse_line(lines.pop(0))
        csv_str += str(round((t - t0).total_seconds(), 1)) + ',' 
        csv_str += ','.join([str(val) for val in vals]) + '\n'

    out_fn = dstat_fn.replace('data/raw', 'data/final')
    out_fn += '.csv'
    with open(out_fn, 'w') as fid:
        fid.write(csv_str)
    
    # Convert and save JSON object
    obj = csv_to_json(csv_str)
    out_fn = out_fn.replace('.csv', '.json')
    with open(out_fn, 'w') as fid:
        fid.write(json.dumps(obj))

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        sys.stderr.write("USAGE: ./parse_cpu_heatmap.py <fn>\n")
        sys.exit(1)
    main(sys.argv[1])
