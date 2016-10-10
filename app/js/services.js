'use strict';

/* Services */

var macroscopeServices = angular.module('macroscopeServices', ['ngResource']);

macroscopeServices.factory('Measurement', ['$resource',
    function($resource) {
        return $resource(':runId.json', {}, {
            query: {
                method: 'GET',
                params: {
                    runId: 'measurements'
                },
                isArray: true
            }
        });
    }
]);

macroscopeServices.service('tests', 'Test');
