'use strict';

/* Controllers */

var vizWorkloadControllers = angular.module('vizWorkloadControllers', []);

vizWorkloadControllers.controller('summaryCtrl', ['$http', '$location', '$timeout',
  function($http, $location, $timeout) {
    // Read the summary file, and redirect to the first measurement
    $http.get('summary.json').success(function(data){
      var runId = data[0].run_id,
        host = data[0].hosts[0],
        url = '/measurement/' + runId + '/' + host;
        $timeout(function() {
          $location.path(url);
        }, 400);
    }
    )
  }
])

vizWorkloadControllers.controller('detailCtrl', ['$scope', '$routeParams', 
    '$http', '$location',
    function($scope, $routeParams, $http, $location) {
      var counter = 0,
      parseTimeFile = function(measurement){
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
          counter += 1;
          updatePage();
        })
      },
      updateDescription = function(){
        $scope.measurements.forEach(function(meas){
          // Update the description, etc to display this measurements attributes
          if (meas.run_id == $scope.runId) {
            $scope.description = meas.description;
            $scope.timestamp = meas.timestamp;
            $scope.hosts = meas.hosts;
          }
        });
      },
      drawCharts = function(runId){
        $http.get(runId + '.json').success(function(chartdata){
          $scope.measurement = chartdata;
          $scope.allTimeCharts = Object.keys($scope.measurement).filter(
              function(key){
                return $scope.measurement[key].type == "timeseries";
              });
          $scope.allHeatmaps = Object.keys($scope.measurement).filter(
              function(key){
                return $scope.measurement[key].type == "heatmap";
              });
          $scope.allTimeCharts.forEach(function(chart){
            drawTimeseries('id_' + chart, $scope.measurement[chart],
                $scope.host);
          });
          $scope.allHeatmaps.forEach(function(chart){
            drawHeatmap('id_' + chart, $scope.measurement[chart],
                $scope.host);
          });
        });
      },
      checkURL = function(){
        if ($scope.hosts.indexOf($scope.host) == -1){
          // Bad URL.  Redirect to valid host
          $scope.host = $scope.hosts[0];
          var url = '/measurement/' + $scope.runId + '/' + $scope.hosts[0];
          $location.path(url);
          console.log('Redirect to ' + url);
          return null;
        }
        return true;
      },
      updatePage = function(){
        if (counter === $scope.measurements.length){
          updateDescription();
          if (checkURL()){
            summaryChart($scope.measurements);
            drawCharts($scope.runId);
          }
        }
      };

      $scope.runId = $routeParams.runId;
      $scope.host = $routeParams.host;

      // Add summary measurements to scope
      $http.get('summary.json').success(function(data){
        $scope.measurements = data;
        $scope.measurements.forEach(parseTimeFile);
      });
    }
]);
