'use strict';

/* Services */

var vizWorkloadServices = angular.module('vizWorkloadServices', ['ngResource']);

vizWorkloadServices.factory('Measurement', ['$resource',
    function($resource) {
        return $resource(':runId.json', {}, {
            query: {
                method: 'GET',
                params: {
                    runId: 'summary'
                },
                isArray: true
            }
        });
    }
]);

vizWorkloadServices.service('tests', 'Test');
