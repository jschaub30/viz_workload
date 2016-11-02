# Currently available measurements
Here's a description of the currently available measurements.
I'll add more measurements over time.

##sys-summary
This measurement is enabled by default.

Summarizes system behavior in 4 charts
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

#How to enable measurements
Only 'sys-summary' is enabled by default
To enable more measurements in your script, export the MEASUREMENTS variable
Examples:
```
export MEASUREMENTS="sys-summary cpu-heatmap interrupts"
```
```
export MEASUREMENTS="sys-summary gpu"
```
