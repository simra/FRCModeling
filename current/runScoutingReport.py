from OPR import OPR
from fetchMatches import fetch_event_teams
import pickle
import os
import argparse

parser = argparse.ArgumentParser(description='Generate a scouting report for an event')
parser.add_argument('event_key', type=str, default='2024wasam', help='Event key to generate a scouting report for')
args = parser.parse_args()
year = int(args.event_key[:4])

def create_model(district, event, match_type, force_recompute=False):
    '''
    district: string, the district to filter by. eg 'pnw', 'all' for all districts
    event: string, the event to filter by. eg. '2024wasno', 'all' for all events
    match_type: string, the match type to filter by. eg. 'qm', 'all' for all match types
    force_recompute: bool, if True, recompute the model even if it already exists
    '''
    
    model_key=f'{district}_{event}_{match_type}'
    model_fn = f'model_{model_key}.pkl'
    
    filename = f'matches_{year}.pkl'        
    with open(filename, 'rb') as f:
        all_matches = pickle.load(f)
        # stat the matches file to get its last modified time and set it on all_matches
        all_matches['last_modified'] = os.stat(filename).st_mtime

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
    
    opr = OPR(selected_matches, teams)
    opr.data_timestamp = all_matches['last_modified']
    
    return opr

def scrub(s):
    return s.replace(',', '_').replace(' ', '_')

def runScoutingReport(event_key):
    opr = create_model('pnw', 'all', 'all')
    event_teams = fetch_event_teams(event_key)
    print(f"Scouting Report for {event_key}")
    header = "team_number,nickname,opr_mu,opr_sigma,dpr_mu,dpr_sigma,tpr_mu,tpr_sigma"
    print(header)
    results = []
    for t in event_teams:
        if t.key in opr.opr_lookup:
            o = opr.opr_lookup[t.key]
            output = (t.team_number, scrub(t.nickname), o['opr']['mu'], o['opr']['sigma'], o['dpr']['mu'], o['dpr']['sigma'], o['tpr']['mu'], o['tpr']['sigma'])
        else:
            output = (t.team_number, scrub(t.nickname), 0, 0, 0, 0, 0, 0)
        results.append(output)
    results = sorted(results, key=lambda x: x[-2], reverse=True)
    for row in results:    
        print(','.join(map(str, row)))

runScoutingReport(args.event_key)