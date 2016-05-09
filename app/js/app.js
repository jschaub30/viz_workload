'use strict';

/* App Module */

var macroscopeApp = angular.module('macroscopeApp', [
    'ngRoute',
    'macroscopeControllers',
    'macroscopeServices'
]);

macroscopeApp.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/summary', {
        templateUrl: 'partials/measurement-summary.html',
        controller: 'summaryCtrl'
      }).
      when('/measurement/:runId/:sourceIdx', {
        templateUrl: 'partials/measurement-detail.html',
        controller: 'detailCtrl'
      }).
      when('/measurement/:runId/', {
        redirectTo: '/measurement/:runId/0'
      }).
      otherwise({
        redirectTo: '/summary'
      });
  }]);
