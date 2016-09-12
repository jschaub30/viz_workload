'use strict';

var timeseries_chart = function(data, divId, plotOptions) {
        var chart = new Dygraph(
            document.getElementById(divId),
            data, plotOptions
        );
        return chart;
    },
    drawMonitor = function(monitor, source) {

        // var url = measurements[currentMeasurement].monitors[monitor].data[currentSource].finalFilename;
        // console.log('url is ' + url);
        $.ajax({
            type: "GET",
            url: monitor.data[source].finalFilename,
            dataType: "text",
            success: function(data) {
                // console.log(monitor);
                var plotOptions = new TimeseriesPlotOptions,
                    divId = monitor.divId;
                plotOptions.title = monitor.plotOptions.title;
                timeseries_chart(data, divId, plotOptions)
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
