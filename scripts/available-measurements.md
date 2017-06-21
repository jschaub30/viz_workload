# Currently available measurements
Here's a description of the currently available measurements.
I'll add more measurements over time.

##sys-summary
This measurement is enabled by default.

Summarizes system behavior in 4 charts:

1. System CPU [%]
2. System memory usage
3. System IO usage
4. System network usage

##cpu-heatmap 
Heatmap of all cpu threads vs. time

##interrupts  
Heatmap of interrupts summed for each cpu thread vs. time

##gpu
For systems with Nvidia GPU's and CUDA installed.

Creates 4 charts:

1. Avg GPU/MEMORY utilization
2. Power of each GPU
3. Detail GPU utilization (heatmap)
4. Detail GPU memory utilization (heatmap)

##nvprof
Data size from NVIDIA nvprof tool

##pcie
Capture PCIE data where /usr/sbin/fal_app is present
use "export CONTINUE_ON_ERROR=1" if tool is not present on all hosts

Creates 8 charts:
1. Host Utilization In
2. Host Utilization Out
3. Host Data Size In
4. Host Data Size Out
5. Device Utilization In
6. Device Utilization Out
7. Device Data Size In
8. Device Data Size Out

##ib
Mellanox Infiniband data

#How to enable measurements
Only 'sys-summary' is enabled by default. To enable more measurements in your 
script, export the MEASUREMENTS variable as shown below.

Examples:
```
export MEASUREMENTS="sys-summary cpu-heatmap interrupts"
```
```
export MEASUREMENTS="sys-summary gpu"
```
