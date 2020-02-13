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

def fetch_all_matches(year, reset=False):
    if_modified_since = ''
    result = {}
    outfile = 'matches_{}.pkl'.format(year)
    if os.path.exists(outfile):
        with open(outfile, 'r', encoding='utf-8') as inresult:
            result=json.load(inresult)
            if 'Last-Modified' in result and not reset:
                if_modified_since = result['Last-Modified']

    try:
        events = api_instance.get_events_by_year(2020, if_modified_since=if_modified_since)
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
        with open(outfile,'w', encoding='utf-8') as outmatches:
            pickle.dump(result,outmatches)

    return result

team_key = 'frc492'
def fetch_matches():
    result = []
    try:
        events = api_instance.get_team_events_by_year(team_key, 2019, if_modified_since=if_modified_since)
        for e in events:
            print('Fetching: '+e.short_name)
            matches = api_instance.get_event_matches(e.key)
            result += matches
            #for m in matches:
                #print(m.match_number)

    except ApiException as e:
        print("Exception when calling EventApi->get_team_events: %s\n" % e)
    
    return result


matches = fetch_all_matches(2020)
print(' {} events fetched'.format(len(matches['Events'])))