'use strict';

/* App Module */

var vizWorkloadApp = angular.module('vizWorkloadApp', [
    'ngRoute',
    'vizWorkloadControllers'
]);

vizWorkloadApp.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/summary', {
        templateUrl: 'partials/measurement-summary.html',
        controller: 'summaryCtrl'
      }).
      when('/measurement/:runId/:host', {
        templateUrl: 'partials/measurement-combined.html',
        controller: 'detailCtrl'
      }).
      when('/measurement/:runId/', {
        redirectTo: '/measurement/:runId/0'
      }).
      otherwise({
        redirectTo: '/summary'
      });
  }]);
