'use strict';

/* Controllers */

var workloadMonitorApp = angular.module('workloadMonitorApp', []);

workloadMonitorApp.controller('MonitorListCtrl', function($scope, $http) {
    $scope.init = function() {
      // Create the chart divs
        var monitor,
            htmlString;

        for (var i = 0; i < $scope.monitors.length; i++) {
            monitor = $scope.monitors[i];
            // console.log(monitor);
            htmlString = '<div class="col-md-6 chart" id="id_';
            htmlString += $scope.monitors[i].name + '"></div>';
            console.log(htmlString);
            if ((i % 2) === 0) {
                $('.container-fluid').append('<div class="row"></div>');
            }
            $('.row').last().append(htmlString);
        }
    };

    $scope.drawCharts = function() {
        var monitor;

        for (var i = 0; i < $scope.monitors.length; i++) {
            monitor = $scope.monitors[i];
            // console.log(monitor);
            switch (monitor.type) {
                case 'timeseries':
                    // console.log('Calling timeseries');
                    load_csv($scope.currentID, $scope.currentHost, monitor);
                    break;
                case 'heatmap':
                    console.log('Calling heatmap');
                    break;
            }
        }
    };

    $http.get('config.json').success(function(data) {
        $scope.runIDs = data.runIDs;
        $scope.hosts = data.slaves;
        $scope.currentHost = $scope.hosts[0];
        $scope.currentID = $scope.runIDs[0];
        $scope.monitors = data.monitors;
        $scope.init();
        $scope.drawCharts();
    });

});
