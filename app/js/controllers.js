'use strict';

/* Controllers */

var vizWorkloadControllers = angular.module('vizWorkloadControllers', []);

vizWorkloadControllers.controller('summaryCtrl', ['$scope', 'Measurement',
    function($scope, Measurement) {
      $scope.measurements = Measurement.query();
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
