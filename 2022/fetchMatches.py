from __future__ import print_function
import sys
sys.path.append('../')
import time
import swagger_client as v3client
from swagger_client.rest import ApiException
from pprint import pprint
import pickle
import os
import json
import argparse

parser = argparse.ArgumentParser(description='Fetch match data from the blue alliance.')
parser.add_argument('--year', type=int, default=2022, help='Season to fetch')
parser.add_argument('--reset', help='Force re-fetch of the entire season', action='store_true')
parser.add_argument('--events', help='events to pull', default="")

args = parser.parse_args()

# Configure API key authorization: apiKey
configuration = v3client.Configuration()
configuration.api_key['X-TBA-Auth-Key'] = 'H5BU1gIXB57bFxNXNGQswd4E59Gs4rLuSooiPWYuu0c0zh8tBVuLQrwBJepUgXUQ'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# net.thefletcher.tbaapi.v3client.configuration.api_key_prefix['X-TBA-Auth-Key'] = 'Bearer'
# create an instance of the API class
#api_instance = v3client.TBAApi()

api_instance = v3client.EventApi(v3client.ApiClient(configuration))
#team_key = 'frc492' # str | TBA Team Key, eg `frc254`
#if_modified_since = 'if_modified_since_example' # str | Value of the `Last-Modified` header in the most recently cached response by the client. (optional)
if_modified_since = ''

def fetch_all_matches(year, eventsToPull="", reset=False):
    """
    Fetch all matches associated with a requested year, 
    filtered to eventsToPull, or all events if it's empty.
    Set reset=True to force re-fetching everything.
    """
    if_modified_since = ''
    result = {}
    eventsFilter = None
    if eventsToPull!="":
        eventsFilter=eventsToPull.split(',')

    outfile = 'matches_{}.pkl'.format(year)
    if os.path.exists(outfile):
        with open(outfile, 'rb') as inresult:
            try:
                result=pickle.load(inresult)
                if 'headers' in result and 'Last-Modified' in result['headers'] and not reset:
                    if_modified_since = result['headers']['Last-Modified']
            except:
                print('Failed to load prior matches')
                result = {}
    try:
        events = api_instance.get_events_by_year(year, if_modified_since=if_modified_since)
        if eventsFilter is not None:
            events = [e for e in events if e.key in eventsFilter]

        result = {
            'headers': api_instance.api_client.last_response.getheaders(), 
            'events': events 
            }
        if 'matches' not in result:
            result['matches']= {}
        for e in events:
            print('Fetching event {}'.format(e.key))
            matches = api_instance.get_event_matches(e.key, if_modified_since=if_modified_since)
            result['matches'][e.key]=matches
            print(matches)
        
    except ApiException as e:
        print("Exception when calling EventApi->get_team_events: %s\n" % e)
    
    if 'events' in result:
        with open(outfile,'wb') as outmatches:
            pickle.dump(result,outmatches)

    return result

def fetch_events(team_key='frc492'):
    events = api_instance.get_team_events_by_year(team_key, 2022, if_modified_since=if_modified_since)
    for e in events:
        print(f'{e.event_code}\t{e.name}\t{e.start_date}')


def fetch_event_rankings(event_key = '2022wasno'):
    rankings = api_instance.get_event_rankings(event_key)
    return rankings

def fetch_matches(team_key = 'frc492'):
    """
    Fetches all matches all events associated with a single team
    """
    result = []
    try:
        events = api_instance.get_team_events_by_year(team_key, 2022, if_modified_since=if_modified_since)
        for e in events:
            print('Fetching: '+e.short_name)
            matches = api_instance.get_event_matches(e.key)
            result += matches
            #for m in matches:
                #print(m.match_number)

    except ApiException as e:
        print("Exception when calling EventApi->get_team_events: %s\n" % e)
    
    return result

def count_matches(events): 
    return sum([len(events[e]) for e in events])

def fetch_teams(year):
    """
    Fetch the list of all teams for a requested year.
    """
    list_api = v3client.ListApi(v3client.ApiClient(configuration))
    pg = 0
    result = []
    while True:
        print('page {}'.format(pg))
        teams = list_api.get_teams_by_year(year, pg)
        if len(teams)==0:
            break
        result+=teams
        pg+=1
        
    with open('teams_{}.pkl'.format(year),'wb') as outTeams:
        pickle.dump(result,outTeams)

if __name__ == "__main__":
    # Current default behavior is to fetch all the matches for a single year.
    matches = fetch_all_matches(args.year, eventsToPull=args.events, reset=args.reset)
    print('{} events fetched'.format(len(matches['events'])))
    print('{} matches total'.format(count_matches(matches['matches'])))