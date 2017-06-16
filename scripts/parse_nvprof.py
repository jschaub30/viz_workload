#!/usr/bin/env python3

'''
Parse raw nvprof measurement file, take sum of each column for every
second, then save tidy CSV files for both 'size' and 'rate' columns
'''

import sys
import os
import subprocess
import re

def parse_header(line, pattern):
    '''
    Find columns for each data type
    '''
    columns = [col for col, label in enumerate(line)
               if re.search(pattern, label)]
    labels = [line[idx] for idx in columns]
    return (columns, labels)


def summarize(second, fields):
    '''
    fields is list of lists.  take sum
    >>> summarize(7, [[1.1, 3.2], [2.1], [], [4.1, 5.2, 6.3]])
    ['7', '4.300', '2.100', '0', '15.600']
    '''
    
    sum_fields = [str(second)] + ['{:.3f}'.format(sum(field))
                                  if field else '0'
                                  for field in fields]
    return sum_fields

def sum_columns(blob):
    '''
    Take the sum value of each column for every second
    First column is time in seconds
    Time column may not be monotonically increasing
    >>> blob='
    t,name1,name2,name3,name4
    2.1,30,,,
    2.2,,40,,
    2.4,,,85,
    2.8,57,28,,
    3.5,11,,,
    3.9,,22,33,44'
    >>> sum_columns(blob)
    [['t', 'name1', 'name2', 'name3', 'name4'], ['2', '87.000', '58.000', '85.000', '0'], ['3', '11.000', '22.000', '33.000', '44.000']]
    '''
    lines = blob.strip().split('\n')
    header = lines.pop(0).strip().split(',')
    summary = [[name for name in header if name]]
    num_fields = len(summary[0])
    current_second = -1
    all_seconds = []
    data = []
    for i, line in enumerate(lines):
        fields = line.split(',')
        if len(fields) != num_fields:
            print('Header length ({}) != line {} length ({})\n{}'.format(num_fields,
                  i, len(fields), line))
            sys.exit(1)
        t = int(float(fields.pop(0)))
        if t not in all_seconds:
            all_seconds.append(t)
            data.append([[float(x)] if x else [] for x in fields])
        else:
            second_idx = all_seconds.index(t)
            for idx, field in enumerate(fields):
                if field:
                    data[second_idx][idx].append(float(field))

    for second, fields in zip(all_seconds, data):
        summary.append(summarize(second, fields))
    return summary
    

def main(raw_fn):
    '''
    Call parse_nvprof_init.py written by mhchen
    Tidy the data by taking sum across all columns for each second
    Then split into 'size' and 'rate' files
    '''
    actual_fn = raw_fn
    if not os.path.isfile(raw_fn):
        import glob
        files = glob.glob(raw_fn + '*')
        if len(files) > 1:
            sys.stderr.write('WARNING: more than 1 nvprof file found + \n')
        actual_fn = files[0]
    blob = subprocess.getoutput('python parse_nvprof_init.py -t ' + actual_fn) + '\n'
    blob += subprocess.getoutput('python parse_nvprof_init.py ' + actual_fn)
    all_data = sum_columns(blob)
    header = all_data[0]
    base_fn = raw_fn.replace('data/raw', 'data/final').split('.csv')[0]
    suffixes = ['size', 'rate']
    for suffix in suffixes:
        fn = '{}.{}.csv'.format(base_fn, suffix)
        pattern = 'GPU.*{}.*'.format(suffix)
        columns, labels = parse_header(header, pattern)
        max_col = max(columns)
        assert len(columns) > 0
        #labels = ['elapsed time'] + labels
        #lines_str = ','.join(labels) + '\n'
        lines_str = ''
        for line in all_data:
            # sometimes last line is truncated
            line = [line[0]] + [line[idx] for idx in columns]
            lines_str += ','.join(line) + '\n'
        with open(fn, 'w') as fid:
            fid.write(lines_str)
            fid.flush()
        print('Data written to {}'.format(fn))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('USAGE: {} filename\n'.format(sys.argv[0]))
        sys.exit(1)
    main(sys.argv[1])

