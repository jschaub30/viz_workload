'use strict';

/* Controllers */

var vizWorkloadControllers = angular.module('vizWorkloadControllers', []);

vizWorkloadControllers.controller('detailCtrl', ['$scope', '$routeParams', '$http', 'Measurement',
  function($scope, $routeParams, $http, Measurement) {
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
        measurement.time.exit_status = data.split('Exit status:')[1].split('\n')[0];
      })
    }
    // Add all measurements to scope
    $http.get('summary.json').success(function(data){
      $scope.measurements = data;
      $scope.measurements.forEach(parseTimeFile);
      $scope.measurements.forEach(function(meas){
        if (meas.run_id == $routeParams.runId) {
          $scope.description = meas.description;
          $scope.timestamp = meas.timestamp;
          $scope.hosts = meas.hosts;
        }
      });
    });

    $scope.runId = $routeParams.runId;
    $scope.host = $routeParams.host;
    $scope.measurement = Measurement.get({
      runId: $routeParams.runId
    },
      function(measurement) {
        // Create "allCharts"--an array of measurement detail objects 
        // add allCharts to scope so that divs can be created prior to plotting
        var keys = Object.keys(measurement),
          allCharts = [],
          obj;
        for (var i = 0; i < keys.length; i++) {
          obj = measurement[keys[i]];
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
]);
