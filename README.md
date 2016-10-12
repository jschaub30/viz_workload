# viz_workload
Quickly measure, view and share your single- or multi-node linux workload 
in data-rich, interactive charts

#Setup
These scripts use ssh to start/stop monitors and run the workload, even when
only running on 1 host.  To avoid having to type a password each time, setup
password-less ssh.  Here are simple instructions for 1 host:
```
ssh-keygen -t rsa  # Press enter at the prompts
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys'
chmod 600 ~/.ssh/authorized_keys
```

#Try it out
```
sudo apt-get install -y dstat time
git clone https://github.com/jschaub30/viz_workload
cd viz_monitor/scripts
cp example.sh your_workload.sh
[ Edit your_workload.sh ]
./your_workload.sh
./webserver.sh  # To view/share this measurement
```

#Example scripts
- [example.sh][example] Simple CPU load example
- [example-sweep.sh][example-sweep] Sweeping a parameter
- [example-cluster.sh][example-cluster] 2 hosts at a time
- [example-cluster-sweep.sh][example-cluster-sweep] Sweep a parameter on 2 hosts

[example]: [scripts/example.sh]
[example-sweep]: [../blob/master/scripts/example-sweep.sh]
[example-cluster]: [../blob/master/scripts/example-cluster.sh]
[example-cluster-sweep]: [../blob/master/scripts/example-cluster-sweep.sh]

## Optional.  Setup your webserver
To permanently share all measurements, enable a web server.
On Ubuntu, this is as simple as
```
sudo apt-get install apache2
cd /var/www/html
sudo ln -sf [full path to viz_workload/scripts/rundir directory]
```


Copyright IBM 2016
