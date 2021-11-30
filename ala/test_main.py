from unittest import TestCase

import numpy.testing
from fastapi import FastAPI
import os
import sys

currentdir = os.path.dirname(__file__)
sys.path.insert(0, currentdir)

from reader import file_reader
from ALparser.ALParser import ApacheLogParser
import numpy as np

app = FastAPI()


class Test(TestCase):

    def test_e2e_parsing_and_creating_ml_df(self):
        # Setup
        ALparser = ApacheLogParser('../../data/test/bad-user-agents-test.list', '../../data/test/bad-referer-test.list')
        file_reader.read_logs_file(ALparser, 'test/input1')

        # Get ML formatted logs
        ml_df = ALparser.getMLFormattedLogs()

        ## ASSERTIONS

        # Statuses
        expected_statuses = np.array([200, 200, 200, 200])
        numpy.testing.assert_array_equal(expected_statuses, ml_df['status'].to_numpy())

        # Activity file extension
        expected_activity_file_ext = np.array(['ico', '-', 'txt', 'txt'])
        numpy.testing.assert_array_equal(expected_activity_file_ext, ml_df['activity_file_ext'].to_numpy())

        # User agent
        expected_user_agents = np.array([
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36',
            'UniversalFeedParser/4.2-pre-314-svn +http://feedparser.org/',
            'Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)',
            'Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)'
        ])
        numpy.testing.assert_array_equal(expected_user_agents, ml_df['user_agent'].to_numpy())

        # Suspicious agent
        expected_statuses = np.array([0, 0, 1, 1])
        numpy.testing.assert_array_equal(expected_statuses, ml_df['suspicious_agent'].to_numpy())

        # Session same count
        expected_statuses = np.array([1, 1, 2, 2])
        numpy.testing.assert_array_equal(expected_statuses, ml_df['session_same_count'].to_numpy())
