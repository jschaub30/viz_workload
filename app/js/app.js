var macroscopeApp = angular.module('macroscopeApp', [
    'ngRoute',
    'macroscopeControllers'
]);


macroscopeApp.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/summary', {
        templateUrl: 'partials/measurement-summary.html',
        controller: 'summaryCtrl'
      }).
      when('/measurement/:runIdx', {
        templateUrl: 'partials/measurement-detail.html',
        controller: 'detailCtrl'
      }).
      otherwise({
        redirectTo: '/summary'
      });
  }]);
