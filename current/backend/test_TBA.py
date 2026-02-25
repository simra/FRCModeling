"""
Tests for the incremental TBA match-caching logic in current/backend/TBA.py.

These tests use unittest.mock to avoid real HTTP calls and verify that:
  1. Per-event Last-Modified headers are stored and reused.
  2. A 304 Not Modified response for an event preserves cached data.
  3. The events-list 304 falls back to the cached events list.
  4. reset=True ignores all cached timestamps.
  5. The merge logic never loses previously cached events.
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Make sure the current/backend package is importable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from swagger_client.rest import ApiException
from TBA import TBA


def _make_api_exception(status):
    return ApiException(status=status, reason='test')


def _make_event(key, district_abbrev=None):
    event = MagicMock()
    event.key = key
    if district_abbrev:
        event.district = MagicMock()
        event.district.abbreviation = district_abbrev
    else:
        event.district = None
    return event


class _BaseTBATest(unittest.TestCase):
    """
    Base class that patches v3client, os.path.exists, pickle.load/dump and
    os.replace so that no real file I/O or network calls are made.
    """

    def setUp(self):
        # --- API client patches ---
        self.config_patcher = patch('TBA.v3client.Configuration')
        self.event_api_patcher = patch('TBA.v3client.EventApi')
        self.api_client_patcher = patch('TBA.v3client.ApiClient')
        self.mock_config_cls = self.config_patcher.start()
        self.mock_event_api_cls = self.event_api_patcher.start()
        self.mock_api_client_cls = self.api_client_patcher.start()

        self.mock_api = MagicMock()
        self.mock_event_api_cls.return_value = self.mock_api
        self.fake_last_response = MagicMock()
        self.fake_last_response.getheaders.return_value = {
            'Last-Modified': 'Thu, 01 Jan 2026 00:00:00 GMT'
        }
        self.fake_last_response.getheader.return_value = 'Thu, 01 Jan 2026 00:00:00 GMT'
        self.mock_api.api_client.last_response = self.fake_last_response

        # --- File I/O patches ---
        # Start with an existing, empty cache so __init__ doesn't trigger a fetch.
        self._initial_cache = {
            'events': [], 'matches': {}, 'event_teams': {},
            'event_last_modified': {}
        }
        self.exists_patcher = patch('TBA.os.path.exists', return_value=True)
        self.stat_patcher = patch('TBA.os.stat')
        self.replace_patcher = patch('TBA.os.replace')
        self.makedirs_patcher = patch('TBA.os.makedirs')
        self.open_patcher = patch('builtins.open', unittest.mock.mock_open())
        self.pickle_load_patcher = patch('TBA.pickle.load',
                                         side_effect=self._pickle_load_side_effect)
        self.pickle_dump_patcher = patch('TBA.pickle.dump')

        self.mock_exists = self.exists_patcher.start()
        self.mock_stat = self.stat_patcher.start()
        self.mock_replace = self.replace_patcher.start()
        self.mock_makedirs = self.makedirs_patcher.start()
        self.mock_open = self.open_patcher.start()
        self.mock_pickle_load = self.pickle_load_patcher.start()
        self.mock_pickle_dump = self.pickle_dump_patcher.start()

        mock_stat_result = MagicMock()
        mock_stat_result.st_mtime = 1234567890.0
        self.mock_stat.return_value = mock_stat_result

        with patch.dict(os.environ, {'DATA_FOLDER': '/tmp/tba_test', 'TBA_API_KEY': 'test'}):
            self.tba = TBA(year=2026, district='all')

    def _pickle_load_side_effect(self, f):
        return dict(self._initial_cache)  # return a fresh copy each time

    def tearDown(self):
        self.config_patcher.stop()
        self.event_api_patcher.stop()
        self.api_client_patcher.stop()
        self.exists_patcher.stop()
        self.stat_patcher.stop()
        self.replace_patcher.stop()
        self.makedirs_patcher.stop()
        self.open_patcher.stop()
        self.pickle_load_patcher.stop()
        self.pickle_dump_patcher.stop()


class TestIncrementalFetch(_BaseTBATest):
    # ------------------------------------------------------------------
    # Test 1: per-event Last-Modified is stored after a fresh fetch
    # ------------------------------------------------------------------
    def test_per_event_last_modified_stored(self):
        event_a = _make_event('2026waaaa')
        self.mock_api.get_events_by_year.return_value = [event_a]
        self.mock_api.get_event_matches.return_value = []
        self.mock_api.get_event_teams.return_value = []
        self.fake_last_response.getheader.return_value = 'Fri, 02 Jan 2026 12:00:00 GMT'

        result = self.tba.fetch_all_matches()

        self.assertIn('2026waaaa', result['event_last_modified'])
        self.assertEqual(result['event_last_modified']['2026waaaa'],
                         'Fri, 02 Jan 2026 12:00:00 GMT')

    # ------------------------------------------------------------------
    # Test 2: 304 for an event's matches preserves the cached matches
    # ------------------------------------------------------------------
    def test_event_304_preserves_cached_matches(self):
        event_a = _make_event('2026waaaa')
        cached_match = MagicMock()
        self._initial_cache = {
            'events': [event_a],
            'matches': {'2026waaaa': [cached_match]},
            'event_teams': {'2026waaaa': []},
            'event_last_modified': {'2026waaaa': 'Mon, 01 Jan 2026 00:00:00 GMT'},
            'headers': {'Last-Modified': 'Mon, 01 Jan 2026 00:00:00 GMT'},
        }

        self.mock_api.get_events_by_year.return_value = [event_a]
        self.mock_api.get_event_matches.side_effect = _make_api_exception(304)
        self.mock_api.get_event_teams.side_effect = _make_api_exception(304)

        result = self.tba.fetch_all_matches()

        self.assertIn('2026waaaa', result['matches'])
        self.assertEqual(result['matches']['2026waaaa'], [cached_match])

    # ------------------------------------------------------------------
    # Test 3: events-list 304 falls back to cached events
    # ------------------------------------------------------------------
    def test_events_list_304_uses_cached_events(self):
        event_a = _make_event('2026waaaa')
        self._initial_cache = {
            'events': [event_a],
            'matches': {},
            'event_teams': {},
            'event_last_modified': {},
            'headers': {'Last-Modified': 'Mon, 01 Jan 2026 00:00:00 GMT'},
        }

        self.mock_api.get_events_by_year.side_effect = _make_api_exception(304)
        self.mock_api.get_event_matches.return_value = []
        self.mock_api.get_event_teams.return_value = []

        result = self.tba.fetch_all_matches()

        self.assertIn(event_a, result['events'])

    # ------------------------------------------------------------------
    # Test 4: reset=True sends empty if_modified_since for every event
    # ------------------------------------------------------------------
    def test_reset_ignores_cached_timestamps(self):
        event_a = _make_event('2026waaaa')
        self._initial_cache = {
            'events': [event_a],
            'matches': {'2026waaaa': []},
            'event_teams': {},
            'event_last_modified': {'2026waaaa': 'Mon, 01 Jan 2026 00:00:00 GMT'},
            'headers': {'Last-Modified': 'Mon, 01 Jan 2026 00:00:00 GMT'},
        }

        self.mock_api.get_events_by_year.return_value = [event_a]
        self.mock_api.get_event_matches.return_value = []
        self.mock_api.get_event_teams.return_value = []

        self.tba.fetch_all_matches(reset=True)

        call_kwargs = self.mock_api.get_event_matches.call_args
        self.assertEqual(call_kwargs.kwargs.get('if_modified_since', ''), '')

    # ------------------------------------------------------------------
    # Test 5: previously cached matches for other events are preserved
    # ------------------------------------------------------------------
    def test_previously_cached_matches_preserved_for_other_events(self):
        event_old = _make_event('2026waold')
        event_new = _make_event('2026wanew')
        old_match = MagicMock()
        self._initial_cache = {
            'events': [event_old],
            'matches': {'2026waold': [old_match]},
            'event_teams': {},
            'event_last_modified': {},
            'headers': {},
        }

        self.mock_api.get_events_by_year.return_value = [event_new]
        self.mock_api.get_event_matches.return_value = []
        self.mock_api.get_event_teams.return_value = []

        result = self.tba.fetch_all_matches()

        # Old cached matches must be preserved.
        self.assertIn('2026waold', result['matches'])
        self.assertEqual(result['matches']['2026waold'], [old_match])
        # New event must also be present.
        self.assertIn('2026wanew', result['matches'])

    # ------------------------------------------------------------------
    # Test 6: per-event if_modified_since is passed to the API
    # ------------------------------------------------------------------
    def test_per_event_if_modified_since_used(self):
        event_a = _make_event('2026waaaa')
        stored_ts = 'Tue, 10 Jan 2026 08:00:00 GMT'
        self._initial_cache = {
            'events': [event_a],
            'matches': {'2026waaaa': []},
            'event_teams': {},
            'event_last_modified': {'2026waaaa': stored_ts},
            'headers': {},
        }

        self.mock_api.get_events_by_year.return_value = [event_a]
        self.mock_api.get_event_matches.return_value = []
        self.mock_api.get_event_teams.return_value = []

        self.tba.fetch_all_matches()

        call_kwargs = self.mock_api.get_event_matches.call_args
        self.assertEqual(call_kwargs.kwargs.get('if_modified_since'), stored_ts)


if __name__ == '__main__':
    unittest.main()
