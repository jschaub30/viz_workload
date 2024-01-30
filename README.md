# viz_workload
Measure, view and share data-rich, interactive timeseries charts of
system performance while running a single- or multi-node linux workload.

This tool is useful for identifying performance bottlenecks for, say,
[setting the sort benchmark record](https://sortbenchmark.org/).

Verson 1.1.0

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
sudo apt-get install -y time git python3 hwloc
```

### Install `dool`
The `viz_workload` tool was originally develeped by gathering data via the
[`dstat`](https://github.com/dstat-real/dstat) utility, which stopped development due to a
conflict with Redhat.

The current project is has been renamed to [`dool`](https://github.com/scottchiefbaker/dool).

Here's how to install `dool` as the root user.
```sh
git clone git@github.com:scottchiefbaker/dool.git --branch v1.3.1 /tmp/doolinstall

sudo /tmp/doolinstall/install.py
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
[available]: https://github.com/jschaub30/viz_workload/blob/master/scripts/available-measurements.md

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
