#!/usr/bin/python

'''
Common functions
'''

import sys
import os
import json
import re
from datetime import datetime


def mean_int(numbers):
    '''
    Take mean of array, rounded to the nearest int
    '''
    return int(round(sum(numbers) / max(len(numbers), 1)))


def slice_array(arr, step=2):
    '''
    reduce the length of array by step, taking the mean of each block of data
    '''
    return [mean_int(arr[idx:idx + step]) for idx in range(0, len(arr), step)]


def csv_to_json(csv_str):
    '''
    Parses a csv string into json object formatted for heatmap cart

    Input format:
       'time,cpu1,cpu2,cpu3\n
        time1,val1a,val2a,val3a\n
        time2,val1b,val2b,val3b\n
        time3,val1c,val2c,val3c\n'
    
    Returns object with 2 keys:
        "labels" as first column (time data)
        "datasets" as list of nested objects, one for each remaining column
    obj = {
        "labels": [time1, time2, time3],
        datasets = [
            {"label": "cpu1", "data":[val1a, val1b, val1c]},
            {"label": "cpu2", "data":[val2a, val2b, val2c]},
            {"label": "cpu3", "data":[val3a, val3b, val3c]}
            ]
        }
    '''
    lines = csv_str.strip().split('\n')
    labels = lines.pop(0).split(',')[1:]
    num_cols = len(lines[0].split(',')) - 1  # Subtract first column (time data)
    line = lines.pop(0).split(',')
    # Initialize lists
    times = [int(line.pop(0))]
    # Create a list of lists for datasets
    datasets = [[int(float(i))] for i in line]
    for line in lines:
        fields = line.split(',')
        times.append(int(fields.pop(0)))
        for col in range(num_cols):
            datasets[col].append(int(float(fields[col])))
    datasets.reverse()  # Start cpu0 at bottom of heatmap

    # Now construct json object
    idx = num_cols - 1
    all_datasets = []
    matrix_size = len(datasets) * len(times)
    while matrix_size > 3000:
        print('Matrix size ({}) larger than threshold. Reducing by 2'.format(matrix_size))
        times = slice_array(times)
	for col, dataset in enumerate(datasets):
            datasets[col] = slice_array(dataset)
        matrix_size = len(datasets) * len(times)
    print('Final matrix is ' + str(matrix_size))
    for dataset in datasets:
        all_datasets.append({"label": labels[idx],
                "data": dataset})
        idx -= 1
    obj = {"labels": times, "datasets": all_datasets}
    return obj

