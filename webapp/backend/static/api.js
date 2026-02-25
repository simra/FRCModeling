
/* TODO:
    the list should be sorted by OPR descending
    alt-text on mouse over to display opr
    heat map the colors of the cells based on OPR
    add a button to clear the alliances
    add a button to run the bracket
    a separate set of fields to choose the event and pull the teams for that event
*/

helpers = {
    data: [],
    row_labels : ['1', '2', '3', '4', '5', '6', '7', '8'],
    col_labels : ['1', '2', '3'],
        
    set_data: function(_data) {
        this.data = _data;
        this.minOpr = Math.min(...helpers.data.map(item => item.stats.opr));
        this.maxOpr = Math.max(...helpers.data.map(item => item.stats.opr));

    },
    add_to_team_list: function(team) {
        var teamList = $('#teams ul');
        var li = $('<li>').appendTo(teamList);
        li.text(team['team']);
        // set the alt text for the team to be the OPR
        li.attr('title', team['stats']['opr']);
        li.attr('draggable', 'true');
        li.attr('id', 'team-' + team['team']);
        li.on('dragstart', function(event) {
            event.originalEvent.dataTransfer.setData('text', event.target.id);
        });
        this.set_list_colors(li, team);
    },
    
    remove_from_team_list: function(team) {
        $('#team-' + team).remove();
    },

    set_list_colors: function(li, team) {
        
        // Function to interpolate between two values
        function interpolate(a, b, t) {
            return a + (b - a) * t;
        }

        // Function to calculate color based on opr
        function calculateColor(opr) {
            //console.log(opr);
            var t = (opr - helpers.minOpr) / (helpers.maxOpr - helpers.minOpr);
            var r = Math.round(interpolate(0, 255, t));
            var g = Math.round(interpolate(255, 0, t));
            return 'rgb(' + r + ', ' + g + ', 0)';
        }

        var color = calculateColor(team.stats.opr);
        //console.log(color);
        li.css('background-color', color);        
    },

    render_bracket: function(data) {
        // show the results in the bracket_results div.
        // for data.density we have the format:
        // match_id: {[alliance]: count, ...}
        // iterate through match ids 1 through 16 and populate a table row with the alliance counts
        $('#bracket_results').empty();
        var table = $('<table>').appendTo('#bracket_results');
        for (var i = 1; i <= 16; i++) {
            var row = $('<tr>').appendTo(table);
            row.append($('<th>').text(i));
            var row_data = data.density[i];
            var text = ''
            for (var k in row_data) {
                text += k + ': ' + row_data[k] + ' ';
            }
            var td = $('<td>').appendTo(row);
            td.text(text);            
        }

        // populate the outcomes
        for (var k in data.overall) {
            $('#outcome-' + k).text(data.overall[k]);        
        }
    },

    clear_alliance_table: function() {
        // clear the alliance table
        var row_labels = this.row_labels;
        var col_labels = this.col_labels;
        for (var i = 0; i < row_labels.length; i++) {
            for (var j = 0; j < col_labels.length; j++) {
                $('#cell-' + row_labels[i] + '-' + col_labels[j]).text('');
            }
        }
    },

    create_alliance_table: function() {
        $('#brackets').empty();
        // in div with id 'brackets', populate an 8 by 3 table with row labels 1-8
        // and column labels '1', '2', '3'
        var table = $('<table>').appendTo('#brackets');
        var tbody = $('<tbody>').appendTo(table);
        console.log('populating table');
        var row_labels = this.row_labels;
        var col_labels = this.col_labels;
        for (var i = 0; i < row_labels.length; i++) {
            var tr = $('<tr>').appendTo(tbody);
            var th = $('<th>').appendTo(tr);
            th.text('A' + row_labels[i]);
            for (var j = 0; j < col_labels.length; j++) {
                var td = $('<td><div></div></td>').appendTo(tr);
                td.attr('id', 'cell-' + row_labels[i] + '-' + col_labels[j]);
                //td.text(row_labels[i] + '-' + col_labels[j]);
            }
            // append a td at the end of the row to record outcomes
            var td = $('<td><div></div></td>').appendTo(tr);
            td.attr('id', 'outcome-A' + row_labels[i]);
        }

        $('td').on('dragover', function(event) {
            event.preventDefault(); // Allow dropping        
        });

        $('td').on('drop', function(event) {
            event.preventDefault();
            var data = event.originalEvent.dataTransfer.getData('text');
            var team = $('#' + data).text();

            var existingTeam = $(event.target).text();
            if (existingTeam) {
                // TODO: cludge
                // look up existingTeam in helpers.data
                // find the team in the list and add it back to the list of teams
                for (var i = 0; i < helpers.data.length; i++) {
                    if (helpers.data[i]['team'] === existingTeam) {
                        helpers.add_to_team_list(helpers.data[i]);
                        break;
                    }
                }            
            }
            helpers.remove_from_team_list(team);
            $(event.target).text(team);
        });
    }    
};

$(document).ready(function() {

    $('#district').val(localStorage.getItem('district'));
    $('#model_event').val(localStorage.getItem('model_event'));
    $('#event').val(localStorage.getItem('event'));
    $('#match_type').val(localStorage.getItem('match_type'));

    helpers.create_alliance_table();

    $.ajaxSetup({
        timeout: 20000
      });
    // center a button below the table with the label "RUN BRACKET"
    var button = $('<button>RUN BRACKET</button>').appendTo('#brackets_container');
    button.on('click', function(event) {
        alliances = {}
        // for each row i in the table, gather the three names into a list
        // set alliances['A' + i] to the list
        var row_labels = helpers.row_labels;
        var col_labels = helpers.col_labels;
        for (var i = 0; i < row_labels.length; i++) {
            var alliance = [];
            for (var j = 0; j < col_labels.length; j++) {
                var team = $('#cell-' + row_labels[i] + '-' + col_labels[j]).text();
                if (team) {
                    alliance.push(team);
                }
            }
            alliances['A' + row_labels[i]] = alliance;
        }
        console.log(alliances);
        // POST alliances to /model/district_model_event_match_type/bracket
        var district = $('#district').val();
        var model_event = $('#model_event').val();
        var match_type = $('#match_type').val();
        url = '/model/' + district + '_' + model_event + '_' + match_type + '/bracket';
        // POST the alliances to the url
        $.ajax({
            type: 'POST',
            url: url,
            data: JSON.stringify(alliances),
            success: function(data) { 
                console.log(data); 
                $('#bracket_results').text(data);
                helpers.render_bracket(data);
            },
            contentType: "application/json",
            dataType: 'json'
        });
    });



    $('form').on('submit', function(event) {
        event.preventDefault(); // Prevent the form from submitting normally

        var district = $('#district').val();
        var model_event = $('#model_event').val();
        var match_type = $('#match_type').val();
        var event = $('#event').val();

        // Save the values to localStorage when the form is submitted
        localStorage.setItem('district', district);
        localStorage.setItem('model_event', model_event);
        localStorage.setItem('match_type', match_type);
        localStorage.setItem('event', event);

        var url = '/model/' + district + '_' + model_event + '_' + match_type + '/event/'+event+'/teams';
        console.log(url);
        $.get(url, function(data) {
            // This function is called when the request is successful.
            // 'data' contains the response from the server.

            // Display the list of teams in the 'brackets' div
            console.log(data);
            helpers.set_data(data);
            // remove all the content from the 'brackets' div
            $('#teams').empty();
            $('<ul>').appendTo('#teams');
            
            // first sort the data list by OPR descending
            helpers.data.sort(function(a, b) {
                return b['stats']['opr'] - a['stats']['opr'];
            });
            
            for (var i = 0; i < helpers.data.length; i++) {
                t = helpers.data[i];
                if (t['team'] === '') {
                    continue;
                }
                helpers.add_to_team_list(t);
            }
            // clear the alliance table
            helpers.create_alliance_table();
        });
    });
});