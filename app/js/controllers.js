'use strict';

/* Controllers */

var vizWorkloadControllers = angular.module('vizWorkloadControllers', []);

vizWorkloadControllers.controller('summaryCtrl', ['$http', '$location',
  function($http, $location) {
    // Read the summary file, and redirect to the first measurement
    $http.get('summary.json').success(function(data){
      var runId = data[0].run_id,
        host = data[0].hosts[0],
        url = '/measurement/' + runId + '/' + host;
      $location.path(url);
    }
    )
  }
])

vizWorkloadControllers.controller('detailCtrl', ['$scope', '$routeParams', 
  '$http', '$location',
  function($scope, $routeParams, $http, $location) {
    $scope.runId = $routeParams.runId;
    $scope.host = $routeParams.host;

    function parseTimeFile(measurement){
      $http.get(measurement.time.filename).success(function(data){
        var hr=0,
          min,
          sec,
          arr,
          len;
        arr = data.match(/([0-9]:)+[0-9]+\.+[0-9]+/)[0].split(':');
        len = arr.length;
        if (len === 3) {hr = parseInt(arr[0]);}
        min = parseInt(arr[len-2]);
        sec = parseFloat(arr[len-1]);
        measurement.time.elapsed_time_sec = (hr*60*60 + min*60 + sec).toString();
        measurement.time.exit_status = data.split('Exit status: ')[1].split('\n')[0];
        measurement.time.exit_clean = measurement.time.exit_status === '0';
      })
    }

    function loadChartData(runId){
      $http.get(runId + '.json').success(function(chartdata){
        $scope.measurement = chartdata;
        // Create "allCharts"--an array of measurement detail objects 
        // add allCharts to scope so that divs can be created prior to plotting
        var keys = Object.keys(chartdata),
          allCharts = [],
          obj;
        for (var i = 0; i < keys.length; i++) {
          obj = $scope.measurement[keys[i]];
          if (obj.hosts) {
            //Only keys that have the 'hosts' field can be plotted
            obj['divId'] = 'id_' + keys[i];
            allCharts.push(obj);
          }
        }

        $scope.allCharts = allCharts;
        $scope.drawCharts();
      }
      );

      $scope.drawCharts = function() {
        for (var i = 0; i < $scope.allCharts.length; i++) {
          drawMonitor($scope.allCharts[i],
            $scope.host);
        }
      };
    }
    // Add summary measurements to scope
    $http.get('summary.json').success(function(data){
      $scope.measurements = data;
      $scope.measurements.forEach(parseTimeFile);
      $scope.measurements.forEach(function(meas){
        if (meas.run_id == $scope.runId) {
          $scope.description = meas.description;
          $scope.timestamp = meas.timestamp;
          $scope.hosts = meas.hosts;
        }
      });
      if ($scope.hosts.indexOf($scope.host) == -1){
        // Redirect to valid host
        $scope.host = $scope.hosts[0];
        var url = '/measurement/' + $scope.runId + '/' + $scope.hosts[0];
        $location.path(url);
        console.log('Redirect to ' + url);
      }
      loadChartData($scope.runId);
    });

  }
]);
