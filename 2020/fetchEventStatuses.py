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

if __name__ == "__main__":

    result = {}
    for e in args.events.split(','):        
        rankings = api_instance.get_event_rankings(e)
        rankout = [(x.team_key, x.rank) for x in rankings.rankings]
        result[e]=dict(rankout)
        
    with open('rankings_2020.pkl', 'wb') as outRankings:
        pickle.dump(result, outRankings)
print(result)