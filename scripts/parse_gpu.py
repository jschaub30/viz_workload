#!/usr/bin/python

'''
Input:  raw csv data nvidia-smi
Output: json timeseries file with total interrupts per cpu thread
'''

import sys
import os
import json
import re
from datetime import datetime

def csv_to_json(csv_str):
    '''
    Parses a csv string into json object formatted for heatmap cart

    Input format:
       'time1,val1a,val2a,val3a\n
        time2,val1b,val2b,val3b\n
        time3,val1c,val2c,val3c\n'
    
    Returns object with 2 keys:
        "labels" as first column (time data)
        "datasets" as list of nested objects, one for each remaining column
    obj = {
        "labels": [t1, t2, t3],
        datasets = [
            {"label": gpu1, "data":[val1a, val1b, val1c]},
            {"label": gpu2, "data":[val2a, val2b, val2c]},
            {"label": gpu3, "data":[val3a, val3b, val3c]}
            ]
        }
    '''
    lines = csv_str.strip().split('\n')
    field_names = lines[0].split(',')
    num_cols = len(lines[0].split(',')) - 1  # Subtract first column (time data)
    line = lines.pop(0).split(',')
    # Initialize lists
    times = [float(line.pop(0))]
    # Create a list of lists for datasets
    datasets = [[float(i)] for i in line]
    for line in lines:
        fields = line.split(',')
        times.append(float(fields.pop(0)))
        for col in range(num_cols):
            datasets[col].append(float(fields[col]))
    datasets.reverse()  # Start gpu0 at bottom of heatmap

    # Now construct json object
    cpu = num_cols - 1
    all_datasets = []
    for dataset in datasets:
        all_datasets.append({"label": "gpu%g" % cpu,
                "data": dataset})
        cpu -= 1
    obj = {"labels": times, "datasets": all_datasets}
    return obj

def validate(csv_str):
    '''
    Verify a consistent number of columns in the csv string
    Strip last record if incomplete
    '''
    lines = csv_str.split('\n')
    len0 = len(lines[0].split(','))
    len1 = len(lines[-1].split(','))
    while len0 != len1:
        lines.pop()
        len1 = len(lines[-1].split(','))
    return '\n'.join(lines)

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def calc_avg(gpu_str, mem_str):
    avg_str = ''
    gpu_lines = gpu_str.split('\n')
    mem_lines = mem_str.split('\n')
    while gpu_lines:
        line = gpu_lines.pop(0)
        fields = line.split(',')
        avg_str += '%s,%.1f,' % (fields[0], mean(map(float, fields[1:])))
        line = mem_lines.pop(0)
        fields = line.split(',')
        avg_str += '%.1f\n' % (mean(map(float, fields[1:])))
    return avg_str


def main(fn):
    '''
    '''
    with open(fn, 'r') as fid:
        lines = fid.readlines()
    fields = lines.pop(0)
    t0 = False
    while lines:
        line = lines.pop(0)
        regex_str = '([\d\/ :.]+),\s+(\d+),[\s\w]+,\s*(\d+\.*\d*)\s%,'
        regex_str += '\s*(\d+\.*\d*)\s%,\s*(\d+\.*\d*)\sW'
        try:
            m = re.match(regex_str, line)
            (tstamp, idx, util_gpu, util_mem, power_gpu) = m.groups()
            t = datetime.strptime(tstamp, '%Y/%m/%d %H:%M:%S.%f')
            if not t0:
                t0 = t
                gpu_str = '0'
                mem_str = '0'
                pow_str = '0'
            elif int(idx) == 0:
                t_sec = round((t - t0).total_seconds(), 1)
                gpu_str += '\n%g' % t_sec 
                mem_str += '\n%g' % t_sec 
                pow_str += '\n%g' % t_sec 
            gpu_str += ',' + util_gpu
            mem_str += ',' + util_mem
            pow_str += ',' + power_gpu
        except Exception as e:
            pass
    # Often the last set of data is incomplete. Clean the csv records
    gpu_str = validate(gpu_str)
    mem_str = validate(mem_str)
    pow_str = validate(pow_str)
    ext = ['.gpu', '.mem', '.pow']
    num_gpu = len(gpu_str.split('\n')[0].split(',')) - 1
    header = 'time_sec,' + ','.join(['gpu' + str(i) for i in range(num_gpu)]) 
    header += '\n'
    # Save data for all individual gpu traces
    for csv_str in [gpu_str, mem_str, pow_str]:
        ext_str = ext.pop(0)
        out_fn = fn.replace('data/raw', 'data/final') + ext_str + '.csv'
        with open(out_fn, 'w') as fid:
            fid.write(header + csv_str)
        obj = csv_to_json(csv_str)
        out_fn = fn.replace('data/raw', 'data/final') + ext_str + '.json'
        with open(out_fn, 'w') as fid:
            fid.write(json.dumps(obj))
    # Now calculate average GPU & Memory usage for all traces
    header = 'time_sec,GPU,MEMORY\n'
    avg_str = calc_avg(gpu_str, mem_str)
    out_fn = fn.replace('data/raw', 'data/final') + '.avg.csv'
    with open(out_fn, 'w') as fid:
        fid.write(header + avg_str)

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        sys.stderr.write("USAGE: ./parse_interrupts.py <fn>\n")
        sys.exit(1)
    main(sys.argv[1])
