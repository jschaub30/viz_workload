'use strict';

/* Controllers */

var workloadMonitorApp = angular.module('workloadMonitorApp', []);

workloadMonitorApp.controller('MonitorListCtrl', ['$scope', '$http',
    function($scope, $http) {
        $scope.init = function() {
            $http.get('measurements/runs.json').success(function(data) {
                $scope.measurements = data;
                $scope.currentRunIndex = 0;
                // $scope.drawCharts();
                $scope.loadJSON();
            })
        };
        $scope.drawCharts = function() {
            // Load json for current run
            // console.log($scope);
            // console.log($scope.currentRunIndex)
            $http.get('measurements/' + $scope.measurements[$scope.currentRunIndex].filename)
                 .success(function(data) {
                // console.log(data);
                $scope.monitors = data;
            });
        };
        $scope.loadJSON = function() {
            // Load json for all runs into measurements object
            for( var i = 0; i < $scope.measurements.length; i++){
              $http.get('measurements/' + $scope.measurements[i].filename)
                   .success(function(data) {
                     $scope.measurements[$scope.currentRunIndex].monitors = data;
                     $scope.currentRunIndex ++;
                    });
            }
        };

        $scope.init();
    }
]);
