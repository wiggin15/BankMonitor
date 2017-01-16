function get_options() {
    return {
        title: {
            text: ''
        },

        xAxis: {
            tickWidth: 0,
            gridLineWidth: 1,
            labels: {
                align: 'left',
                x: 3,
                y: -3
            }
        },

        yAxis: [{ // left y axis
            labels: {
                align: 'left',
                x: 3,
                y: 3,
                formatter: function() {
                    return Highcharts.numberFormat(this.value, 0);
                }
            },
            showFirstLabel: false
        }],

        navigation: {
            buttonOptions: {
                enabled: false
            }
        },

        chart : {
            renderTo : 'container',
            events : {click: null }
        },

        rangeSelector : {
            selected : 5
        },

        series : [],
        series_template : {
            // cloned by the code in index.html, and added as one series to 'series'
            connectNulls: true,
            tooltip: {
                valueDecimals: 2
            },
            marker : {
                enabled : true,
                radius : 2,
                symbol : 'circle'
            },
            point: {events: {}}
        },
        colors: ["#7cb5ec"]

    }
}
