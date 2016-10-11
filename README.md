# viz_workload
Quickly measure, view and share your single- or multi-node linux workload 
in data-rich, interactive charts

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
- [example.sh](https://github.com/jschaub30/viz_workload/blob/master/scripts/example.sh) Simple CPU load example
- [example-sweep.sh](https://github.com/jschaub30/viz_workload/blob/master/scripts/example-sweep.sh) Sweeping a parameter

## Optional.  Setup your webserver
To permanently share all measurements, enable a web server.
On Ubuntu, this is as simple as
```
sudo apt-get install apache2
cd /var/www/html
sudo ln -sf [full path to viz_workload/scripts/rundir directory]
```

Copyright IBM 2016
