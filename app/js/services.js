'use strict';

/* Services */

var macroscopeServices = angular.module('macroscopeServices', ['ngResource']);

macroscopeServices.factory('Measurement', ['$resource',
    function($resource) {
        return $resource('measurements/:runId.json', {}, {
            query: {
                method: 'GET',
                params: {
                    runId: 'runs'
                },
                isArray: true
            }
        });
    }
]);

macroscopeServices.service('tests', 'Test');
