from __future__ import print_function
import pickle
import os
import logging
import swagger_client as v3client
from swagger_client.rest import ApiException

logging.basicConfig(level=logging.INFO)

class TBA:
    def __init__(self, year=2024, district = 'all'):
        self.matches = None
        self.year = year
        self.district = district
        self.DATA_FOLDER = os.environ.get('DATA_FOLDER', './data')
        if not os.path.exists(self.DATA_FOLDER):
            os.makedirs(self.DATA_FOLDER)
        self.matches_file = f'{self.DATA_FOLDER}/matches_{self.district}_{self.year}.pkl'
        
        # Configure API key authorization: apiKey
        configuration = v3client.Configuration()
        configuration.api_key['X-TBA-Auth-Key'] = os.environ.get('TBA_API_KEY')
        self.configuration = configuration
        
        # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
        # net.thefletcher.tbaapi.v3client.configuration.api_key_prefix['X-TBA-Auth-Key'] = 'Bearer'
        # create an instance of the API class
        #api_instance = v3client.TBAApi()

        self.api_instance = v3client.EventApi(v3client.ApiClient(configuration))
        #team_key = 'frc492' # str | TBA Team Key, eg `frc254`
        #if_modified_since = 'if_modified_since_example' # str | Value of the `Last-Modified` header in the most recently cached response by the client. (optional)
        
        if not os.path.exists(self.matches_file):
            self.fetch_all_matches()

        with open(self.matches_file, 'rb') as f:
            self.matches = pickle.load(f)
            self.matches['last_modified'] = os.stat(self.matches_file).st_mtime


    def fetch_all_matches(self, eventsToPull="", reset=False, if_modified_since='',):
        """
        Fetch all matches associated with a requested year, 
        filtered to eventsToPull, or all events if it's empty.
        Set reset=True to force re-fetching everything.
        """
        api_instance = self.api_instance
        result = {}
        events_filter = None
        if eventsToPull!="":
            events_filter=eventsToPull.split(',')

        outfile = self.matches_file
        if os.path.exists(outfile):
            with open(outfile, 'rb') as inresult:
                try:
                    result=pickle.load(inresult)
                    if 'headers' in result and 'Last-Modified' in result['headers'] and not reset:
                        if_modified_since = result['headers']['Last-Modified']
                except Exception as e:
                    logging.error('Failed to load prior matches. %s', e)
                    result = {}
        try:
            events = api_instance.get_events_by_year(self.year, if_modified_since=if_modified_since)
            if self.district != 'all':
                events = [e for e in events if e.district and e.district.abbreviation==self.district]
            if events_filter is not None:
                events = [e for e in events if e.key in events_filter]

            # TODO: this overrides result with a new dict, should be merged
            result = {
                'headers': api_instance.api_client.last_response.getheaders(),
                'events': events
            }
            if 'matches' not in result:
                result['matches'] = {}
                result['event_teams'] = {}
            for e in events:
                logging.info('Fetching event %s', e)
                matches = api_instance.get_event_matches(e.key, if_modified_since=if_modified_since)
                result['matches'][e.key]=matches
                # print(matches)
                teams = api_instance.get_event_teams(e.key, if_modified_since=if_modified_since)
                result['event_teams'][e.key]=teams
            
        except ApiException as e:
            logging.error("Exception when calling EventApi->get_team_events: %s\n", e)
        
        if 'events' in result:
            if os.path.exists(outfile):
                # make a backup copy, overwrite if it already exists            
                os.replace(outfile, outfile+'.bak')
            with open(outfile,'wb') as outmatches:
                pickle.dump(result,outmatches)

        result['last_modified'] = os.stat(outfile).st_mtime
        self.matches = result
        return result

    def fetch_events(self, team_key='frc492', if_modified_since=''):
        events = self.api_instance.get_team_events_by_year(team_key, self.year, if_modified_since=if_modified_since)
        for e in events:
            print(f'{e.event_code}\t{e.name}\t{e.start_date}')
        return events

    def fetch_event_rankings(self, event_key):
        rankings = self.api_instance.get_event_rankings(event_key)
        return rankings

    def fetch_event_teams(self, event_key):
        return self.api_instance.get_event_teams(event_key)


    def fetch_matches(self, team_key = 'frc492', if_modified_since=''):
        """
        Fetches all matches all events associated with a single team
        """
        result = []
        try:
            events = self.api_instance.get_team_events_by_year(team_key, self.year, if_modified_since=if_modified_since)
            for e in events:
                print('Fetching: '+e.short_name)
                matches = self.api_instance.get_event_matches(e.key)
                result += matches
                #for m in matches:
                    #print(m.match_number)

        except ApiException as e:
            print("Exception when calling EventApi->get_team_events: %s\n" % e)
        
        return result

    @staticmethod
    def count_matches(events):
        return sum([len(events[e]) for e in events])

    def fetch_teams(self):
        """
        Fetch the list of all teams for a requested year.
        """
        list_api = v3client.ListApi(v3client.ApiClient(self.configuration))
        pg = 0
        result = []
        while True:
            logging.info('page ' % pg)
            teams = list_api.get_teams_by_year(self.year, pg)
            if len(teams)==0:
                break
            result+=teams
            pg+=1
            
        with open(f'{self.DATA_FOLDER}/teams_{self.year}.pkl','wb') as outTeams:
            pickle.dump(result,outTeams)
    