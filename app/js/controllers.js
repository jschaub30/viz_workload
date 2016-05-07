'use strict';

/* Controllers */

var macroscopeControllers = angular.module('macroscopeControllers', []);

macroscopeControllers.controller('summaryCtrl', ['$scope', '$http',
    function($scope, $http) {
        $scope.init = function() {
            $http.get('measurements/runs.json').success(function(data) {
                $scope.measurements = data.measurements;
                console.log(data.scopes);
                $scope.sources = data.sources; // typically hostnames
                $scope.allScopes = data.scopes;
                $scope.allMeasurements = Object.keys(data.measurements);
                $scope.currentMeasurement = $scope.allMeasurements[0];
                $scope.currentSource = data.sources[0];
                // $scope.drawCharts();
                $scope.loadMeasurements();
            })
        };
        $scope.drawCharts = function() {
            for (var i = 0; i < $scope.allScopes.length; i++) {
                drawScope($scope.allScopes[i], $scope.measurements,
                    $scope.currentMeasurement, $scope.currentSource);
            }
        };
        var idx = 0; // Allows scope data to be bound to measurements object
        $scope.loadMeasurements = function() {
            // Load json for all runs into measurements object
            var keys = Object.keys($scope.measurements);
            for (var i = 0; i < keys.length; i++) {
                $http.get($scope.measurements[keys[i]].url)
                    .success(function(data) {
                        $scope.measurements[keys[idx]].scopes = data;
                        idx++;
                        if(idx == keys.length){
                          console.log($scope.measurements);
                          // $scope.drawCharts();
                        }
                    });
            }
        };

        $scope.init();
    }
]);
