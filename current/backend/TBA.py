from __future__ import print_function
import pickle
import os
import logging
import swagger_client as v3client
from swagger_client.rest import ApiException

logging.basicConfig(level=logging.INFO)

class TBA:
    def __init__(self, year=2026, district='all'):
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

        self.api_instance = v3client.EventApi(v3client.ApiClient(configuration))

        if not os.path.exists(self.matches_file):
            self.fetch_all_matches()

        with open(self.matches_file, 'rb') as f:
            self.matches = pickle.load(f)
            self.matches['last_modified'] = os.stat(self.matches_file).st_mtime

    def fetch_all_matches(self, eventsToPull="", reset=False):
        """
        Fetch all matches for the configured year, filtered to eventsToPull (or all
        events if empty).  Only events whose data has changed since the last fetch are
        re-downloaded; everything else is served from the local cache.

        Incremental behaviour is implemented via per-event HTTP If-Modified-Since
        headers.  The Last-Modified value returned by TBA for each event is stored
        in result['event_last_modified'][event_key] and reused on the next call so
        that TBA can return 304 Not Modified for unchanged events.

        Set reset=True to ignore all cached timestamps and force a full re-fetch.
        """
        api_instance = self.api_instance
        result = {}
        events_filter = None
        if eventsToPull != "":
            events_filter = eventsToPull.split(',')

        outfile = self.matches_file

        # Load the existing cache so we can do incremental updates.
        if os.path.exists(outfile):
            with open(outfile, 'rb') as inresult:
                try:
                    result = pickle.load(inresult)
                except Exception as e:
                    logging.error('Failed to load prior matches: %s', e)
                    result = {}

        # Ensure the sub-dicts we rely on always exist in result.
        result.setdefault('matches', {})
        result.setdefault('event_teams', {})
        result.setdefault('event_last_modified', {})

        # --- Fetch the list of events ---
        # Use the globally stored Last-Modified for the events-list endpoint.
        events_if_modified = ''
        if not reset and 'headers' in result and 'Last-Modified' in result['headers']:
            events_if_modified = result['headers']['Last-Modified']

        events = result.get('events', [])
        try:
            fetched_events = api_instance.get_events_by_year(
                self.year, if_modified_since=events_if_modified)
            if self.district != 'all':
                fetched_events = [
                    e for e in fetched_events
                    if e.district and e.district.abbreviation == self.district
                ]
            if events_filter is not None:
                fetched_events = [e for e in fetched_events if e.key in events_filter]

            # Update the events list and the global Last-Modified header.
            events = fetched_events
            result['events'] = events
            result['headers'] = api_instance.api_client.last_response.getheaders()
            logging.info('Fetched %d events for %d', len(events), self.year)
        except ApiException as exc:
            if exc.status == 304:
                logging.info('Events list not modified since last fetch; using cache')
            else:
                logging.error('Error fetching events for year %d: %s', self.year, exc)

        # --- Fetch matches and teams for each event incrementally ---
        for event in events:
            # Re-use the per-event Last-Modified so TBA can skip unchanged events.
            event_if_modified = '' if reset else result['event_last_modified'].get(event.key, '')

            # Matches
            try:
                matches = api_instance.get_event_matches(
                    event.key, if_modified_since=event_if_modified)
                result['matches'][event.key] = matches
                last_mod = api_instance.api_client.last_response.getheader('Last-Modified', '')
                if last_mod:
                    result['event_last_modified'][event.key] = last_mod
                logging.info('Fetched %d matches for event %s', len(matches), event.key)
            except ApiException as exc:
                if exc.status == 304:
                    logging.info('Matches for event %s not modified; using cache', event.key)
                else:
                    logging.error('Error fetching matches for event %s: %s', event.key, exc)

            # Teams
            try:
                teams = api_instance.get_event_teams(
                    event.key, if_modified_since=event_if_modified)
                result['event_teams'][event.key] = teams
            except ApiException as exc:
                if exc.status == 304:
                    logging.info('Teams for event %s not modified; using cache', event.key)
                else:
                    logging.error('Error fetching teams for event %s: %s', event.key, exc)

        # Persist the updated cache.
        if 'events' in result:
            if os.path.exists(outfile):
                os.replace(outfile, outfile + '.bak')
            with open(outfile, 'wb') as outmatches:
                pickle.dump(result, outmatches)

        result['last_modified'] = os.stat(outfile).st_mtime
        self.matches = result
        return result

    def fetch_events(self, team_key='frc492', if_modified_since=''):
        events = self.api_instance.get_team_events_by_year(
            team_key, self.year, if_modified_since=if_modified_since)
        for e in events:
            print(f'{e.event_code}\t{e.name}\t{e.start_date}')
        return events

    def fetch_event_rankings(self, event_key):
        rankings = self.api_instance.get_event_rankings(event_key)
        return rankings

    def fetch_event_teams(self, event_key):
        return self.api_instance.get_event_teams(event_key)

    def fetch_matches(self, team_key='frc492', if_modified_since=''):
        """
        Fetches all matches for all events associated with a single team.
        """
        result = []
        try:
            events = self.api_instance.get_team_events_by_year(
                team_key, self.year, if_modified_since=if_modified_since)
            for e in events:
                print('Fetching: ' + e.short_name)
                matches = self.api_instance.get_event_matches(e.key)
                result += matches
        except ApiException as e:
            print("Exception when calling EventApi->get_team_events: %s\n" % e)
        return result

    @staticmethod
    def count_matches(events):
        return sum([len(events[e]) for e in events])

    def fetch_teams(self):
        """
        Fetch the list of all teams for the configured year.
        """
        list_api = v3client.ListApi(v3client.ApiClient(self.configuration))
        pg = 0
        result = []
        while True:
            logging.info('Fetching teams page %d', pg)
            teams = list_api.get_teams_by_year(self.year, pg)
            if len(teams) == 0:
                break
            result += teams
            pg += 1

        with open(f'{self.DATA_FOLDER}/teams_{self.year}.pkl', 'wb') as outTeams:
            pickle.dump(result, outTeams)
