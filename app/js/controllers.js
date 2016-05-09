'use strict';

/* Controllers */

var macroscopeControllers = angular.module('macroscopeControllers', []);

macroscopeControllers.controller('summaryCtrl', ['$scope', 'Measurement',
    function($scope, Measurement) {
        $scope.measurements = Measurement.query();
        $scope.measurements.$promise.then(function(result) {
            // Now read each measurement and extract filenames for table
            for (var i = 0; i < result.length; i++) {
                result[i]['monitors'] = Measurement.get({
                        runId: result[i].runId
                    });
            }
        });
    }
]);

macroscopeControllers.controller('detailCtrl', ['$scope', '$routeParams', 'Measurement',
    function($scope, $routeParams, Measurement) {

        $scope.runId = $routeParams.runId;
        $scope.sourceIdx = $routeParams.sourceIdx;
        $scope.measurement = Measurement.get({
                runId: $routeParams.runId
            },
            function(measurement) {
                // console.log(measurement);

                function getMonitorsBySource(measurement) {
                    var keys = Object.keys(measurement),
                        allMonitors = [],
                        obj;
                    for (var i = 0; i < keys.length; i++) {
                        obj = measurement[keys[i]];
                        if (obj.sources) {
                            obj['divId'] = 'id_' + keys[i];
                            allMonitors.push(obj);
                        }
                    }
                    return allMonitors;
                };

                $scope.allMonitors = getMonitorsBySource(measurement);
                // console.log($scope.allMonitors);
                $scope.sources = $scope.allMonitors[0].sources;
                $scope.drawCharts();
            }
        );

        $scope.drawCharts = function() {
            for (var i = 0; i < $scope.allMonitors.length; i++) {
                drawMonitor($scope.allMonitors[i],
                    $scope.sources[$scope.sourceIdx]);
            }
        };
    }
]);
