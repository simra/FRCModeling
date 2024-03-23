from collections import Counter
import logging
import pickle
import os
from time import strftime, gmtime
from dotenv import load_dotenv
import numpy as np
from tqdm import tqdm
from flask_cors import CORS
import scipy.stats as stats 
from OPR import OPR
from TBA import TBA
from flask import Flask, jsonify, request, render_template, send_from_directory


# TODO:
# Periodic match refresh
# Other model types
# model selection for brackets
# Overall OPR rankings page
# Fix the best 2 of 3 bracket?
# button to auto-populate alliances
# dropdown for event selection
# improved layout
# enable arbitrary district selection, all district selection

# model/match data somewhere that doesn't trigger reload.
load_dotenv()
logging.basicConfig(level=logging.DEBUG)

DATA_FOLDER = os.getenv('DATA_FOLDER', '../')
logging.info('Using data folder: %s', DATA_FOLDER)
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

models = {}
tba = TBA(year=2024, district='pnw')
all_matches = tba.matches

app = Flask(__name__, static_folder='static/build')
CORS(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    logging.info('Serving %s', path)
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
    
def create_model(district, event, match_type, force_recompute=False):
    '''
    district: string, the district to filter by. eg 'pnw', 'all' for all districts
    event: string, the event to filter by. eg. '2024wasno', 'all' for all events
    match_type: string, the match type to filter by. eg. 'qm', 'all' for all match types
    force_recompute: bool, if True, recompute the model even if it already exists
    '''

    model_key=f'{district}_{event}_{match_type}'
    model_fn = f'{DATA_FOLDER}/model_{model_key}.pkl'
            

    #if all_matches is None:
    #    filename = f'{DATA_FOLDER}/matches_2024.pkl'        
    #    with open(filename, 'rb') as f:
    #        all_matches = pickle.load(f)
    #        # stat the matches file to get its last modified time and set it on all_matches
    #        all_matches['last_modified'] = os.stat(filename).st_mtime
    
    if not os.path.exists(model_fn) or force_recompute or all_matches['last_modified'] > os.stat(model_fn).st_mtime:
        selected_district = [m.key for m in all_matches['events']] if district == 'all' else \
            [m.key for m in all_matches['events'] if m.district and m.district.abbreviation==district]
        
        print(f'{len(all_matches["matches"])} events')

        data = [m for k in all_matches['matches'] for m in all_matches['matches'][k]]
        data = [m for m in data if m.winning_alliance!='' and m.score_breakdown is not None]
        print(f'Found {len(data)} matches')

        def in_scope(m):
            return ((event == 'all' and m.event_key in selected_district) \
                or (m.event_key == event)) \
                    and (match_type == 'all' or m.comp_level == match_type)

        selected_matches = list(filter(in_scope, data))

        teams = set()
        for m in selected_matches:
            for t in m.alliances.red.team_keys:
                teams.add(t)
            for t in m.alliances.blue.team_keys:
                teams.add(t)

        teams = list(sorted(teams))
        logging.debug('Teams: %s', len(teams))
        
        opr = OPR(selected_matches, teams)
        opr.data_timestamp = all_matches['last_modified']
        logging.debug('Saving %s', model_fn)
        with open(model_fn, 'wb') as f:
            pickle.dump(opr, f)

    with open(model_fn, 'rb') as f:
        logging.debug('Loading %s', model_fn)
        models[model_key] = pickle.load(f)

def get_model(model_key):
    if model_key not in models:
        create_model(*model_key.split('_'))
    assert model_key in models
    return models[model_key]

@app.route('/model/<model_key>')
def get_model_info(model_key):
    '''
    model_key: string, the key for the model to get info for
    returns: a json object with the model info
    '''
    opr = get_model(model_key)
    (district, events, match_type) = model_key.split('_')
    timestamp = strftime('%Y-%m-%d %H:%M:%S', gmtime(opr.data_timestamp))
    return jsonify({
        'district': district, 'event': events, 'match_type': match_type, 'teams': len(opr.opr_lookup), 'last_modified': timestamp})

@app.route('/model/<model_key>/refresh')
def refresh_model(model_key):
    '''
    model_key: string, the key for the model to refresh
    returns: a json object with the model info
    '''
    global all_matches
    global models
    # TODO this must run async: https://stackoverflow.com/questions/14384739/how-can-i-add-a-background-thread-to-flask
    TBA.fetch_all_matches(2024, 'pnw')
    all_matches = TBA.matches
    models = {}
    return jsonify({'all_matches': len(all_matches['matches'])})

# pass in the team id and get back the stats for that team.
@app.route('/model/<model_key>/team/<team_id>')
def get_opr(model_key, team_id):
    '''
    model_key: string, the key for the model to use
    team_id: string, the team id to get the stats for
    '''
    opr=get_model(model_key)
    return jsonify({f"{team_id}": opr.opr_lookup[team_id]})

@app.route('/model/<model_key>/predict/<red>/<blue>/<method>')
def get_prediction(model_key, red,blue, method):
    '''
    model_key: string, the key for the model to use
    red: string, a comma separated list of red teams
    blue: string, a comma separated list of blue teams
    method: opr, dpr, or tpr
    returns: a json object with the predicted spread 
        and standard deviation in favor of the red alliance    
    '''
    red = red.split(',')
    blue = blue.split(',')
    opr = get_model(model_key)
    (spread, sigma) = opr.predict(red,blue, method=method)
    pRed = 1.0-stats.norm.cdf(0, loc=spread, scale=sigma)
    return jsonify({'red': red, 'blue': blue, 'spread':spread, 'sigma':sigma, 'pRed':pRed})

@app.route('/model/<model_key>/teams')
def get_teams(model_key):
    '''
    model_key: string, the key for the model to use
    returns: a json object with the list of teams in the model
    '''
    opr = get_model(model_key)
    return jsonify({'teams': list(opr.opr_lookup.keys())})

@app.route('/model/<model_key>/event/<event_key>/teams')
def get_event_teams(model_key, event_key):
    '''
    model_key: string, the key for the model to use
    event_key: string, the key for the event to get the teams for
    returns: a json object with the list of teams in the event
    '''
    logging.info('Getting teams for model %s event %s', model_key, event_key)
    opr = get_model(model_key)    
        
    teams = tba.fetch_event_teams(event_key)
    
    EMPTY_OPR = {'opr': {'mu': 0, 'sigma': 0}, 'dpr': {'mu': 0, 'sigma': 0}, 'tpr': {'mu': 0, 'sigma': 0}}   

    result = [
        {
            'team': t.key,
            'nickname': t.nickname,
            'number': t.team_number,
            'stats': opr.opr_lookup[t.key] if t.key in opr.opr_lookup else EMPTY_OPR
        }
        for t in teams
    ]

    return jsonify(result)


@app.route('/model/<model_key>/bracket/<model_method>', methods=['POST'])
def run_bracket(model_key, model_method):
    '''
    POST method to run a playoff bracket
    model_key: string, the key for the model to use
    model_method: one of opr, tpr, dpr
    post body: json object containing the set of alliances, of the format:
    {'A1': [team1, team2, team3], 'A2': [...], ..., 'A8': [...]}
    returns: a json object with the predicted spread 
        and standard deviation for each match in the bracket
    '''
    alliances = request.get_json()
    opr = get_model(model_key)
    logging.debug('Running bracket for model %s', model_key)
    # sanity check the alliances for presence in the model
    for a in alliances:
        for t in alliances[a]:
            if t not in opr.opr_lookup:
                # send a bad request result (400) if a team is not found
                logging.error('Team %s not found in model %s', t, model_key)
                return jsonify({'error': f'Team {t} not found in model {model_key}'})
    reverse_lookup = {str(v):k for k,v in alliances.items()}

    bracket = {
        1: ['A1', 'A8'],
        2: ['A4', 'A5'],
        3: ['A2', 'A7'],
        4: ['A3', 'A6'],
        5: ['L1', 'L2'],
        6: ['L3', 'L4'],
        7: ['W1', 'W2'],
        8: ['W3', 'W4'],
        9: ['L7', 'W6'],
        10: ['W5', 'L8'],
        11: ['W10', 'W9'],
        12: ['W7', 'W8'],
        13: ['L12', 'W11'],
        14: ['W12', 'W13'],
        15: ['W14', 'L14'],
        16: ['W15', 'L15']
    }

    density = {i:Counter() for i in range(1,len(bracket)+1)}
            
    def runMatch(matchNumber):
        red_id,blue_id = bracket[matchNumber]
        
        red = alliances[red_id]
        blue =alliances[blue_id]
        density[matchNumber][reverse_lookup[str(red)]]+=1
        density[matchNumber][reverse_lookup[str(blue)]]+=1
        #density[matchNumber][red_id]+=1
        #density[matchNumber][blue_id]+=1
        
        # mu and sigma are the expected advantage for red
        mu,sigma = opr.predict(red,blue, method=model_method)
        r = np.random.normal(mu, sigma)
        
        if r>0:        
            winner = red
            loser = blue
        else:
            winner = blue
            loser = red
        alliances[f'W{matchNumber}'] = winner
        alliances[f'L{matchNumber}'] = loser

      
    def pMatch(matchNumber):
        red_id,blue_id = bracket[matchNumber]
        
        red = alliances[red_id]
        blue =alliances[blue_id]
        density[matchNumber][reverse_lookup[str(red)]]+=1
        density[matchNumber][reverse_lookup[str(blue)]]+=1
        #density[matchNumber][red_id]+=1
        #density[matchNumber][blue_id]+=1
        
        # mu and sigma are the expected advantage for red
        return opr.predict(red,blue)

    

    def pRed(matchNumber):
        mu,sigma = pMatch(matchNumber)
        return 1.0-stats.norm.cdf(0, loc=mu, scale=sigma)
        
        
    def runBracket():
        for i in range(1,17):
            runMatch(i)        
        wins = Counter()
        for i in range(14,17):
            w = alliances[f'W{i}']
            wins[str(w)]+=1
        return sorted(wins, reverse=True, key=lambda x: wins[x])[0], (alliances['A6'] in [alliances['W11'],alliances['W13']])

    overall = Counter()
    inFinalCtr = 0
    for b in tqdm(range(1000)):
        (w, inFinal) = runBracket()
        overall[reverse_lookup[str(w)]] += 1
        inFinalCtr += 1 if inFinal else 0
            
    for k in sorted(overall, key=lambda x: overall[x], reverse=True):
        print(k, overall[k])

    print(f'inFinal: {inFinalCtr}')

    for k in sorted(density):
        print(k, density[k])
    return jsonify({'overall':overall, 'density':density})

if __name__ == '__main__':
    app.run(debug=False)