Stats = function() {
    /*function type(d) {
        d.value = +d.value; // coerce to number
        return d;
    }*/
    return {
        datasource: d3.tsv("data/stats_2020.tsv"),
        mode: "team",
        init_canvas: function() {
            if (this.chart) {
                this.chart.destroy();
            }
            if (!this.ctx) {
                this.ctx = document.getElementById('myChart').getContext('2d');
            } 
            //ctx.canvas.width = 300;
            //ctx.canvas.height = 300;
            //console.log(d3.map(data, function (d) { return d.name;}).keys());
            Chart.defaults.global.defaultFontSize = 10;     
             
        },
        render: function() {
            console.log("render: "+this.mode);
            var self = this;
            self.init_canvas();
            self.datasource.then(function (data) {                
                if (self.mode === "compare") {
                    self.render_compare(self.ctx, data);
                } else if (self.mode === "team") {
                    self.render_team(self.ctx, data);
                }
            });
        },
        populateteams: function(id, change_cb) {
            this.datasource.then(function (data) { 
                data.sort(function (x,y) {
                    return d3.ascending(+x.team.replace('frc',''), +y.team.replace('frc',''));
                });
                var combo = d3.select('#'+id)       
                .append('select')        
                .attr('size',37)
                .attr('multiple','')
                .attr('name', 'name-list')
                .attr('id', id+'select')
                .on('change', change_cb);
                
                var options = combo.selectAll("option")
                .data(data)
                .enter()
                .append("option");
                options.text(function(d) {
                    return d.team.replace('frc','')+': '+d.name;
                     })
                       .attr("value", function(d) {
                    return d.team;
                       });
            });
        },        
        _getSelectValues: function(id) {
            var result = [];
            var select = document.getElementById(id);
            var options = select && select.options;
            var opt;
            if (!options) {
                console.log("can't find "+id);
            }
            console.log(options.length);
            for (var i=0, iLen=options.length; i<iLen; i++) {
                opt = options[i];

                if (opt.selected) {
                    console.log(opt.selected);
                    result.push(opt.value || opt.text);
                }
            }
            console.log('result: '+result.length+' '+result.join(','));
            return result;
        },
        render_team: function(ctx, data) {
            console.log('render_team');
            //var team=d3.select("#teamid").attr("value"); // || "";
            var redteams = this._getSelectValues("redteamsselect");
            var blueteams = this._getSelectValues("blueteamsselect");
            //var redteams = redteam.split(',');
            //var blueteams = blueteam.split(',');
            //console.log('selected "'+redteams+'"');
            data.sort(function(x, y){
                return d3.descending(+x.win_rating, +y.win_rating);
             })
            /*
            var table = d3.select("#data");//.append("table");
            table.selectAll("tr").remove();
            var thead  = table.append("thead");
            var tbody = table.append("tbody");
            var columns = data.columns;
            console.log(columns);            
            thead.append("tr")
            .selectAll("th")
            .data(columns)
            .enter()
            .append("th")
            .text(function(column) { return column; });
            
            var rows = tbody.selectAll("tr")
                .data(data)
                .enter()
                .append("tr")
                .filter(function (d) {return teams==="" || teams.includes(d.team)});
                
        
            // create a cell in each row for each column
            var cells = rows.selectAll("td")
                .data(function(row) {
                    return columns.map(function(column) {
                        return {column: column, value: row[column]};
                    });
                })
                .enter()
                .append("td")
                .attr("style", "font-family: Courier")
                .html(function(d) { return d.value; });   
            */
            //if (team==="") return;
            //var max = d3.max(data, function (d){return +d.op_rating;});
            //console.log(teams.length);
            var datapoints = ['op_rating','rp_rating','win_rating','dp_rating'];
            var accumulator = {};
            datapoints.forEach(function (k) { accumulator['max'+k]=0.0; accumulator['min'+k]=0.0})
            var minmax = data.reduce(function (accumulated, current) {
                //console.log(accumulated);
                datapoints.forEach(e => {
                    accumulated['max'+e] = Math.max(accumulated['max'+e], +current[e]);
                    accumulated['min'+e] = Math.min(accumulated['min'+e], +current[e]);
                });
                return accumulated;
            }, accumulator);
            console.log(minmax);
            var redfiltered =data.filter(function(d){  return redteams.includes(d.team);});                 
            console.log('redteams *'+redteams.join()+'* redfiltered: '+redfiltered);
            var redtorender = redfiltered
                .map(function(e) { 
                    result = {}
                    datapoints.forEach(k => {
                        result[k]=-(e[k]-minmax['min'+k])/(minmax['max'+k]-minmax['min'+k]);
                    })                    
                    return result});
            var rednames = redfiltered.map(e=>e.team);
            var bluefiltered =data.filter(function(d){ return blueteams.includes(d.team)});
            var bluetorender = bluefiltered
                .map(function(e) { 
                    result = {}
                    datapoints.forEach(k => {
                        result[k]=(e[k]-minmax['min'+k])/(minmax['max'+k]-minmax['min'+k]);
                    })                    
                    return result});
            var bluenames = bluefiltered.map(e=>e.team);
            
            var redFillColors = [
                'rgba(255, 99, 132, 0.2)',
                'rgba(255, 132, 99, 0.2)',
                'rgba(255, 50, 50, 0.2)',
                /*'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'*/
            ];
            var blueFillColors = [
                'rgba(132, 99, 255, 0.2)',
                'rgba(235, 162, 255, 0.2)',
                'rgba(86, 206, 255, 0.2)',
            ];
            if (!(redtorender && redtorender.length>0) || !(bluetorender && bluetorender.length>0)) {
                console.log("No data.");
                return;
            }
            this.chart = new Chart(ctx, {
                    type: 'horizontalBar',                    
                    data: {
                        labels: Object.keys(redtorender[0]),
                        datasets: redtorender.map(function (e,i) {
                            console.log(Object.values(e));
                            console.log(i);
                            return {label: rednames[i], data: Object.values(e), backgroundColor: redFillColors[i%redFillColors.length]}
                        }).concat(
                            bluetorender.map(function (e,i) {
                                console.log(Object.values(e));
                                console.log(i);
                                return {label: bluenames[i], data: Object.values(e), backgroundColor: blueFillColors[i%blueFillColors.length]}
                            }))
                    },
                    options: {
                        scales: {
                            xAxes: [{
                                stacked: true,
                                ticks: { 
                                    min: -3.0,
                                    max: 3.0
                                }
                            }],
                            yAxes: [ {stacked: true }]
                        },
                        // Elements options apply to all of the options unless overridden in a dataset
                        // In this case, we are setting the border of each horizontal bar to be 2px wide
                        elements: {
                            rectangle: {
                                borderWidth: 2,
                                height: 50
                            }
                        },
                        responsive: true,
                        legend: {
                            position: 'right',
                        },
                        title: {
                            display: true,
                            text: redteams.join()+" vs "+blueteams.join()
                        },
                    
                        aspectRatio: 2,
                        maintainAspectRatio: false,
                        /*scales: {
                            scaleLabel: { fontSize: 16 },
                            yAxes: [{
                                ticks: {
                                    beginAtZero: true
                                }
                            }]                    
                        }  */              
                    }
                });
        }, 
        render_compare: function(ctx, data) {
            console.log("render_compare");
            var self = this;
            data.sort(function(x, y){
                return d3.descending(+x.op_rating, +y.op_rating);
             })
             
            var myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    /* todo: map is the wrong function here */
                    labels: d3.map(data, function (d) { return d.name;}).keys(),
                    datasets: [{
                        label: 'OPR',
                        data: d3.map(data, function (d) { return +d.op_rating;}).keys(),
                        /*backgroundColor: [
                            'rgba(255, 99, 132, 0.2)',
                            'rgba(54, 162, 235, 0.2)',
                            'rgba(255, 206, 86, 0.2)',
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(153, 102, 255, 0.2)',
                            'rgba(255, 159, 64, 0.2)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],*/
                        borderWidth: 1
                    }]
                },
                options: {
                    aspectRatio: 2,
                    maintainAspectRatio: false,
                    scales: {
                        scaleLabel: { fontSize: 16 },
                        yAxes: [{
                            ticks: {
                                beginAtZero: true
                            }
                        }]                    
                    }
                }
            });
        }
    }
};
    
        //console.log(data);
        // use data here
        //console.log(JSON.stringify(data));
/*        var table = d3.select("#data");//.append("table");
        var thead  = table.append("thead");
        var tbody = table.append("tbody");
        var columns = data.columns;
        console.log(columns);
        thead.append("tr")
        .selectAll("th")
        .data(columns)
        .enter()
        .append("th")
            .text(function(column) { return column; });
        
        var rows = tbody.selectAll("tr")
            .data(data)
            .enter()
            .append("tr");
    
        // create a cell in each row for each column
        var cells = rows.selectAll("td")
            .data(function(row) {
                return columns.map(function(column) {
                    return {column: column, value: row[column]};
                });
            })
            .enter()
            .append("td")
            .attr("style", "font-family: Courier")
                .html(function(d) { return d.value; });
*/
        
        /*
            
        var width = 960;
        var height = 500;
        var adj = 20;
        // we are appending SVG first
        var svg = d3.select("div#container").append("svg")
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("viewBox", "-" + adj + " -"+ adj + " " + (width + adj) + " " + (height + adj))
        .style("padding", 5)
        .style("margin", 5)
        .classed("svg-content", true);
        svg.selectAll("div")
        .data(data)
        .enter()
            .append("rect")
        .attr("class", "bar")
        .attr("x", function (d, i) {
            for (i>0; i < data.length; i++) {
                //onsole.log(i);
                return i*21;
            }
        })
        .attr("y", function (d) {
            //console.log(d);
            return height - d.op_rating;
        })
        .attr("width", 20)
        .attr("height", function (d) {
            //console.log(d);
            return d.op_rating;
        });
        */
        
window.onload = function() {
    var stats = Stats();    
    /*d3.select("#redteamid").on("input", function() { stats.render();});
    d3.select("#blueteamid").on("input", function() { stats.render();});*/
    stats.populateteams('redteams', function() { stats.render();});
    stats.populateteams('blueteams', function() { stats.render();});
    //console.log('select: '+d3.select('#redteamsselect').on);
    //document.getElementById('redteamsselect').onChange=function(e) {alert('foo');};
    //d3.select("#redteamsselect").on('change', function() {alert('foo');stats.render();});
    //console.log(document.getElementById('redteamsselect'));
    //console.log(d3.select('#redteamsselect').node());
    //d3.select("#blueteamsselect").on('change', function() {alert('bar');stats.render();});
    //stats.render();
    //return stats;
}
