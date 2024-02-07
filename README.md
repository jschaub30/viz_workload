# viz_workload
Measure, view and share data-rich, interactive timeseries charts of
system performance metrics while running single- or multi-node linux workloads.

This tool:
1. gathers system information from each node
2. starts up system monitors (cpu, mem, etc.)
3. executes a given workload
4. stops the system monitors
5. gathers data and creates interactive web pages displaying system performance while the workload was running.

Steps 2-4 above can also be repeated while sweeping a workload parameter, and
the pages created in step 5 will include the parameter sweep.

[Here's an example output](https://jeremyschaub.us/demos/viz_workload/cluster_cpu_sweep/html/) with:
- 2 nodes, each with 4 threads and 14-16GB RAM
- high CPU workload
- sweeping a parameter (number of threads 1/2/4)
- CPU heatmap measurement enabled

This tool is useful for identifying performance bottlenecks for, say,
[setting the sort benchmark record](https://sortbenchmark.org/).

Verson 1.1.1

## Setup password-less SSH
These scripts use ssh to start/stop monitors and run the workload, even when
only running on 1 host.  To avoid having to type a password each time, setup
password-less ssh.  Here are simple instructions for 1 host:
```sh
ssh-keygen -t rsa  # Press enter at the prompts (no passphrase!)
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```
To copy the public key to another server, use the following command:
```sh
ssh-copy-id <user_name>@<server_name>
```
Now verify that you don't need to type a password:
```sh
ssh localhost
ssh $(hostname)
```

## Try it out
If you are running a multi-node/cluster workload, follow the installation instructions below on
every host in the cluster.

### Install prerequisites
Ubuntu / Debian
```sh
sudo apt-get install -y time python3  # required
sudo apt-get install -y hwloc         # optional--uses the `lstopo` tool in system summaries
```

### Install `dool`
The `viz_workload` tool was originally developed by gathering data via the
[`dstat`](https://github.com/dstat-real/dstat) utility, which stopped development due to a
conflict with Redhat.

The current project is has been renamed to [`dool`](https://github.com/scottchiefbaker/dool).

Installing `dool`
```sh
git clone git@github.com:scottchiefbaker/dool.git --branch v1.3.1 /tmp/doolinstall

sudo /tmp/doolinstall/install.py  # to install as root
/tmp/doolinstall/install.py       # install as user--make sure the `dool` script is in your PATH variable
```

### Install `viz_workload`
```sh
git clone https://github.com/jschaub30/viz_workload
cd viz_monitor/scripts
cp example.sh your_workload.sh
## Now edit your_workload.sh
./your_workload.sh
./webserver.sh  # To view/share this measurement
```
## Available measurement groups

Each measurement group enables collection and display of 1 or more charts

| Group name   | Description                                              |
| ------------ | ---------------------------------------------------------|
| sys-summary  | enabled by default. CPU, memory, IO and network          |
| cpu-heatmap  | heatmap of CPU usage on each thread                      |
| interrupts   | heatmap of interrupts on each CPU                        |
| gpu          | for systems with Nvidia GPU's and [CUDA][cuda] installed |


More details described [here][available].

[cuda]: https://developer.nvidia.com/cuda-downloads
[available]: blob/master/doc/available-measurements.md

## Example scripts
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
[example-pcie]: https://github.com/jschaub30/viz_workload/blob/master/scripts/example-pcie.sh

## Optional.  Setup your webserver
To permanently share all measurements, enable a web server.

Ubuntu
```
sudo apt-get install apache2
cd /var/www/html
sudo ln -sf [full path to viz_workload/scripts/rundir directory]
```
CentOS
```
sudo yum install httpd
sudo systemctl start httpd
cd /var/www/html
sudo ln -sf [full path to viz_workload/scripts/rundir directory]
```
