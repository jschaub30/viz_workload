'use strict';

function TimeseriesPlotOptions() {
      // labels: labels,
      // colors: chart_colors,
      this.xlabel = "Elapsed time [ sec ]";
      // ylabel: monitor.units,
      this.strokeWidth = 2;
      this.legend = 'always';
      // this.labelsDivWidth = 500;
      this.title = "";
      //http://colorbrewer2.org/
      this.colors = ['rgb(228,26,28)', 'rgb(55,126,184)', 'rgb(77,175,74)',
                        'rgb(152,78,163)', 'rgb(255,127,0)', 'rgb(141,211,199)'];
}
