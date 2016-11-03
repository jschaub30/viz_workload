'use strict';

var timeseries_chart = function(data, divId, plotOptions) {
  var chart = new Dygraph(document.getElementById(divId), data, plotOptions);
  return chart;
},
  drawTimeseries = function(divId, chartData, host) {
    $.ajax({
      type: "GET",
      url: chartData[host].finalFilename,
      dataType: "text",
      success: function(data) {
        var plotOptions = new TimeseriesPlotOptions;
        plotOptions.title = chartData.title;
        timeseries_chart(data, divId, plotOptions)
      },
      error: function(request, status, error) {
        console.log(status);
        console.log(error);
      }
    });
  },
  drawHeatmap = function(divId, chartData, host) {
    $.ajax({
      type: "GET",
      url: chartData[host].finalFilename,
      dataType: "json",
      success: function(data) {
        var ctx = document.getElementById(divId).getContext("2d");
        var sampleChart = new Chart(ctx).HeatMap(data, {
          responsive: true,
          maintainAspectRatio: false,
          rounded: false,
          paddingScale: 0.0,
          showLabels: false,
          showScale: false,
          tooltipTemplate: "t: <%= xLabel %> | cpu: <%= yLabel %> | value: <%= value %>",
          colorInterpolation: 'gradient',
          colors: ['rgb(220,220,220)', 'red']
        });
      },
      error: function(request, status, error) {
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
  },
  summaryChart = function(measurements) {
    // First create data object from elapsed time properties
    var data = measurements.map(function(measurement){
      return { x:measurement.run_id,
        y:parseFloat(measurement.time.elapsed_time_sec)};
    });
    //console.log(data);
    var chart = c3.generate({
      bindto: '#id_summary',
      //size: {
      //height: 600
      //},
      data: {
        json: data,
        keys: {
          x: 'x',
          value: ['y']
        },
        names: {
          y: 'Elapsed time [ sec ]'
        },
        type: "bar"
      },
      grid: {
        x: {
          show: true
        },
        y: {
          show: true
        }
      },
      point: {
        r: 5
      },
      axis: {
        x: {
          type: 'category',
          label: {
            //text: xlabel,
            position: 'outer-right'
          }
        },
        y: {
          min: 0,
          label: {
            text: 'Elapsed execution time [ seconds ]',
            position: 'outer-middle'
          }
        },
      }
    });
  };

