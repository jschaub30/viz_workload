"use strict";

var timeseries_chart = function(data, monitor) {
        console.log('Calling timeseries_chart');
        // console.log(monitor);
        var chart = new Dygraph(
            document.getElementById('id_' + monitor.name),
            data, {
                // labels: labels,
                // colors: chart_colors,
                xlabel: "Elapsed time [ sec ]",
                ylabel: monitor.units,
                strokeWidth: 2,
                legend: 'always',
                labelsDivWidth: 500,
                title: monitor.title
            }
        );
        return chart;
    },
    load_csv = function(id, host, monitor) {
        // console.log('Calling load_csv');
        // console.log(monitor);
        var url = 'data/final/';

        url += id + '.' + host + '.' + monitor.name;
        url += '.' + monitor.type + '.' + monitor.ext;
        console.log(url);
        $.ajax({
            type: "GET",
            url: url,
            dataType: "text",
            success: function(data) {
                // console.log(monitor);
                timeseries_chart(data, monitor)
            },
            error: function(request, status, error) {
                console.log(status);
                console.log(error);
            }
        });
    },
    calc_cumsum = function(data) {
        var new_array = [],
            dt;
        for (var i = 0; i < data.length; i++) {
            new_array.push(data[i].slice(0));
        }
        for (i = 1; i < new_array.length; i++) {
            dt = new_array[i][0] - new_array[i - 1][0];
            for (var j = 1; j < new_array[0].length; j++) {
                new_array[i][j] = new_array[i - 1][j] + dt * new_array[i][j];
            }
        }
        return new_array;
    };