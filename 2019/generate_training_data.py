from __future__ import print_function
import time
import swagger_client as v3client
from swagger_client.rest import ApiException
from pprint import pprint
import pickle
import os

# Configure API key authorization: apiKey
configuration = v3client.Configuration()
configuration.api_key['X-TBA-Auth-Key'] = 'H5BU1gIXB57bFxNXNGQswd4E59Gs4rLuSooiPWYuu0c0zh8tBVuLQrwBJepUgXUQ'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# net.thefletcher.tbaapi.v3client.configuration.api_key_prefix['X-TBA-Auth-Key'] = 'Bearer'
# create an instance of the API class
#api_instance = v3client.TBAApi()

api_instance = v3client.EventApi(v3client.ApiClient(configuration))
team_key = 'frc492' # str | TBA Team Key, eg `frc254`
if_modified_since = 'if_modified_since_example' # str | Value of the `Last-Modified` header in the most recently cached response by the client. (optional)

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

filename = 'matches.pkl'
if not os.path.exists(filename):
    m=fetch_matches()
    with open(filename, 'wb') as f:
        pickle.dump(m, f)

matches = []
with open(filename, 'rb') as f:
    matches = pickle.load(f)

#print(len(matches))

for m in matches:
    red = ' '.join(m.alliances.red.team_keys)
    blue = ' '.join(m.alliances.blue.team_keys)
    label = str(int(m.winning_alliance == 'red'))
    print('\t'.join([label,red,blue]))
#if_modified_since = 'if_modified_since_example' # str | Value of the `Last-Modified` header in the most recently cached response by the client. (optional)

#try:
#    api_response = api_instance.get_status(if_modified_since=if_modified_since)
#    pprint(api_response)
#except ApiException as e:
#    print("Exception when calling TBAApi->get_status: %s\n" % e)
