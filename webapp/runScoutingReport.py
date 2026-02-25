from OPR import OPR
from fetchMatches import fetch_event_teams
import pickle
import os
import argparse
import json
import logging
import time

parser = argparse.ArgumentParser(description='Generate a scouting report for an event')
parser.add_argument('event_key', type=str, default='2024wasam', help='Event key to generate a scouting report for')
parser.add_argument('--debug', help='Enable debug logging', action='store_true')
parser.add_argument('--force', help='Force recompute of the model', action='store_true')
args = parser.parse_args()
year = int(args.event_key[:4])

logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
logging.debug(f"Debug logging enabled")

logging.info(f"Generating scouting report for {args.event_key}, year {year}")

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
    
    logging.debug(f'{len(all_matches["matches"])} events')

    data = [m for k in all_matches['matches'] for m in all_matches['matches'][k]]
    data = [m for m in data if m.winning_alliance!='' and m.score_breakdown is not None]
    logging.debug(f'Found {len(data)} matches')

    def in_scope(m):
        return ((event == 'all' and m.event_key in selected_district) \
            or (m.event_key == event)) \
                and (match_type == 'all' or m.comp_level == match_type)

    selected_matches = list(filter(in_scope, data))
    logging.debug([m.alliances.red.score for m in selected_matches])
    logging.debug([m.alliances.blue.score for m in selected_matches])
    logging.debug(f'Using {len(selected_matches)} matches')
    teams = set()
    for m in selected_matches:
        for t in m.alliances.red.team_keys:
            teams.add(t)
        for t in m.alliances.blue.team_keys:
            teams.add(t)

    teams = list(sorted(teams))
    
    opr = OPR(selected_matches, teams)
    logging.debug(json.dumps(opr.opr_lookup, indent=2))
    opr.data_timestamp = all_matches['last_modified']
    
    return opr

def scrub(s):
    return s.replace(',', '_').replace(' ', '_')

def runScoutingReport(event_key):
    opr = create_model('pnw', 'all', 'all')
    event_teams = fetch_event_teams(event_key)
    timestamp = time.strftime('%Y%m%d%H%M%S')
    out_fn = f"scouting_report_{event_key}_{timestamp}.csv"
    with open(out_fn, 'w') as f:
        f.write(f"Scouting Report for {event_key} @ {timestamp}\n")
        header = "team_number,nickname,opr_mu,opr_sigma,dpr_mu,dpr_sigma,tpr_mu,tpr_sigma\n"
        f.write(header)
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
            f.write(','.join(map(str, row))+'\n')
    logging.info(f"Scouting report written to {out_fn}")

runScoutingReport(args.event_key)