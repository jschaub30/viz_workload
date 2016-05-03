'use strict';

/* Controllers */

var workloadMonitorApp = angular.module('workloadMonitorApp', []);

const scaleGB = 1/1024/1024/1024;

workloadMonitorApp.controller('MonitorListCtrl', function($scope, $http) {
  $http.get('config.json').success(function(data) {
    $scope.runIDs = data.runIDs;
    $scope.hosts = data.slaves;
    $scope.currentHost = $scope.hosts[0];
    $scope.currentID = $scope.runIDs[0];
  });

  $scope.monitors = [
    {'name': 'cpu', 'title': 'CPU', 'yScale': 1, 'type': "timeseries", 'ext': 'csv'},
    {'name': 'io', 'title': 'IO', 'yScale': scaleGB, 'type': "timeseries", 'ext': 'csv'},
    {'name': 'mem', 'title': 'Memory', 'yScale': scaleGB, 'type': "timeseries", 'ext': 'csv'},
    {'name': 'net', 'title': 'Network', 'yScale': scaleGB, 'type': "timeseries", 'ext': 'csv'}
  ];
  // $scope.runIDs = [
  //   {'name': 'RUN1'},
  //   {'name': 'RUN2'}
  // ];
  // $scope.hosts = [
  //   {'name': 'HOST1'},
  //   {'name': 'HOST2'}
  // ];
});
