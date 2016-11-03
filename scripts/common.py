#!/usr/bin/python

'''
Common functions
'''

import sys
import os
import json
import re
from datetime import datetime

def csv_to_json(csv_str, label):
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
            {"label": cpu1, "data":[val1a, val1b, val1c]},
            {"label": cpu2, "data":[val2a, val2b, val2c]},
            {"label": cpu3, "data":[val3a, val3b, val3c]}
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
    datasets = [[int(float(i))] for i in line]
    for line in lines:
        fields = line.split(',')
        times.append(float(fields.pop(0)))
        for col in range(num_cols):
            datasets[col].append(int(float(fields[col])))
    datasets.reverse()  # Start cpu0 at bottom of heatmap

    # Now construct json object
    cpu = num_cols - 1
    all_datasets = []
    for dataset in datasets:
        label_str = "%s%g" % (label, cpu)
        all_datasets.append({"label": label_str,
                "data": dataset})
        cpu -= 1
    obj = {"labels": times, "datasets": all_datasets}
    return obj

