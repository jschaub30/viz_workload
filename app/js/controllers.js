'use strict';

/* Controllers */

var vizWorkloadControllers = angular.module('vizWorkloadControllers', []);

/*vizWorkloadControllers.controller('summaryCtrl', ['$scope', 'Measurement',
  function($scope, Measurement) {
  $scope.measurements = Measurement.query();
  }
  ]);*/

vizWorkloadControllers.controller('summaryCtrl', ['$scope', '$http',
    function($scope, $http) {
      function parseTimeFile(measurement){
        $http.get(measurement.time.filename).success(function(data){
          var hr=0,
          min,
          sec,
          arr,
          len;
          // matching "Elapsed (wall clock) time (h:mm:ss or m:ss): 0:10.01"
          arr = data.match(/([0-9]:)+[0-9]+\.+[0-9]+/)[0].split(':');
          len = arr.length;
          if (len === 3) {hr = parseInt(arr[0]);}
          min = parseInt(arr[len-2]);
          sec = parseFloat(arr[len-1]);
          measurement.time.elapsed_time_sec = (hr*60*60 + min*60 + sec).toString();
        })
      }

      $http.get('summary.json').success(function(data){
        $scope.measurements = data;
        var fn;
        for (var i = 0; i < data.length; i++){
          fn = data[i].time.filename;
          //$scope.measurements[i].time.elapsed_time = parseTimeFile($scope.measurements[i]);
          parseTimeFile($scope.measurements[i]);
        }
      })
    }
]);

vizWorkloadControllers.controller('detailCtrl', ['$scope', '$routeParams', 'Measurement',
    function($scope, $routeParams, Measurement) {

      $scope.runId = $routeParams.runId;
      $scope.sourceIdx = $routeParams.sourceIdx;
      $scope.measurement = Measurement.get({
        runId: $routeParams.runId
      },
      function(measurement) {
        // Create "allMonitors"--an array of measurement detail objects 
        // add allMonitors to scope so that divs can be created prior to plotting
        var keys = Object.keys(measurement),
        allMonitors = [],
        obj;
        for (var i = 0; i < keys.length; i++) {
          obj = measurement[keys[i]];
          if (obj.hosts) {
            //Only keys that have the 'hosts' field can be plotted
            obj['divId'] = 'id_' + keys[i];
            allMonitors.push(obj);
          }
        }

        $scope.allMonitors = allMonitors;
        $scope.hosts = $scope.allMonitors[0].hosts;
        $scope.drawCharts();
      }
      );

      $scope.drawCharts = function() {
        for (var i = 0; i < $scope.allMonitors.length; i++) {
          //Only keys that have the 'hosts' field can be plotted
          drawMonitor($scope.allMonitors[i],
              $scope.hosts[$scope.sourceIdx]);
        }
      };
    }
]);
