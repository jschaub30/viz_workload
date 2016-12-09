# viz_workload
Easily measure, view and share data-rich, interactive timeseries charts that
show system performance while running a single- or multi-node linux workload 

Verson 0.93

#Setup
These scripts use ssh to start/stop monitors and run the workload, even when
only running on 1 host.  To avoid having to type a password each time, setup
password-less ssh.  Here are simple instructions for 1 host:
```
ssh-keygen -t rsa  # Press enter at the prompts
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#Try it out
```
sudo apt-get install -y dstat time git
git clone https://github.com/jschaub30/viz_workload
cd viz_monitor/scripts
cp example.sh your_workload.sh
[ Edit your_workload.sh ]
./your_workload.sh
./webserver.sh  # To view/share this measurement
```
#Available measurement groups

Each measurement group enables collection and display of 1 or more charts

| Group name   | Description                                              |
| ------------ | ---------------------------------------------------------|
| sys-summary  | enabled by default. CPU, memory, IO and network          |
| cpu-heatmap  | heatmap of CPU usage on each thread                      |
| interrupts   | heatmap of interrupts on each CPU                        |
| gpu          | for systems with Nvidia GPU's and [CUDA][cuda] installed |


More details described [here][available].

[cuda]: https://developer.nvidia.com/cuda-downloads
[available]: https://github.com/jschaub30/viz_workload/blob/master/scripts/available-measurements.md

#Example scripts
- [example.sh][example] Simple CPU load example
- [example-sweep.sh][example-sweep] Sweeping a parameter
- [example-cluster-sweep.sh][example-cluster-sweep] Sweep a parameter on 2 hosts
- [example-cpu-heatmap-interrupt.sh][example-cpu-heatmap-interrupt] CPU and interrupt heatmaps
- [example-gpu.sh][example-gpu] Collect data from Nvidia GPU with CUDA installed

[example]: https://github.com/jschaub30/viz_workload/blob/master/scripts/example.sh
[example-sweep]: https://github.com/jschaub30/viz_workload/blob/master/scripts/example-sweep.sh
[example-cpu-heatmap-interrupt]: https://github.com/jschaub30/viz_workload/blob/master/scripts/example-cpu-heatmap-interrupt.sh
[example-cluster-sweep]: https://github.com/jschaub30/viz_workload/blob/master/scripts/example-cluster-sweep.sh
[example-gpu]: https://github.com/jschaub30/viz_workload/blob/master/scripts/example-gpu.sh

## Optional.  Setup your webserver
To permanently share all measurements, enable a web server.
On Ubuntu, this is as simple as
```
sudo apt-get install apache2
cd /var/www/html
sudo ln -sf [full path to viz_workload/scripts/rundir directory]
```


Copyright IBM 2016
