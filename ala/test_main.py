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

    def test_e2e_parsing_and_creating_ml_df():
        # Setup
        ALparser = ApacheLogParser('../../data/test/bad-user-agents-test.list', '../../data/test/bad-referer-test.list')
        file_reader.read_logs_file(ALparser, 'test/input1')

        # Get ML formatted logs
        ml_df = ALparser.getMLFormattedLogs()

        ## ASSERTIONS

        # Session IDs
        expected_ids = np.array(['83.149.9.216:1', '46.105.14.53:1', '218.30.103.62:1', '218.30.103.62:1'])
        numpy.testing.assert_array_equal(expected_ids, ml_df['session_id'].to_numpy())

        # Hosts
        expected_hosts = np.array(['83.149.9.216', '46.105.14.53', '218.30.103.62', '218.30.103.62'])
        numpy.testing.assert_array_equal(expected_hosts, ml_df['host'].to_numpy())

        # Lognames
        expected_lognames = np.array(['-', '-', '-', '-'])
        numpy.testing.assert_array_equal(expected_lognames, ml_df['logname'].to_numpy())

        # Users
        expected_user = np.array(['-', '-', '-', '-'])
        numpy.testing.assert_array_equal(expected_user, ml_df['user'].to_numpy())

        # Http methods
        expected_http_methods = np.array(['GET', 'GET', 'GET', 'GET'])
        numpy.testing.assert_array_equal(expected_http_methods, ml_df['http_method'].to_numpy())

        # Activities
        expected_activities = np.array(['/favicon.ico', '/admin/blog/tags/puppet?flav=rss20', '/robots.txt', '/robots.txt'])
        numpy.testing.assert_array_equal(expected_activities, ml_df['activity'].to_numpy())

        # Activity file extension
        expected_activity_file_ext = np.array(['ico', '-', 'txt', 'txt'])
        numpy.testing.assert_array_equal(expected_activity_file_ext, ml_df['activity_file_ext'].to_numpy())

        # Http versions
        expected_http_versions = np.array(['HTTP/1.1', 'HTTP/1.1', 'HTTP/1.1', 'HTTP/1.1'])
        numpy.testing.assert_array_equal(expected_http_versions, ml_df['http_version'].to_numpy())

        # Statuses
        expected_statuses = np.array([200, 404, 200, 200])
        numpy.testing.assert_array_equal(expected_statuses, ml_df['status'].to_numpy())

        # Bytes of response
        expected_bytes = np.array([3638, 14872, 0, 0])
        numpy.testing.assert_array_equal(expected_bytes, ml_df['bytes_of_response'].to_numpy())

        # Referers
        expected_referers = np.array([
            "http://000free.us",
            "http://semicomplete.com/presentations/logstash-monitorama-2013/",
            "http://semicomplete.com/presentations/logstash-monitorama-2013/",
            "http://semicomplete.com/presentations/logstash-monitorama-2013/"
        ])
        numpy.testing.assert_array_equal(expected_referers, ml_df['referer'].to_numpy())

        # User agent
        expected_user_agents = np.array([
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36',
            'UniversalFeedParser/4.2-pre-314-svn +http://feedparser.org/',
            'Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)',
            'Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)'
        ])
        numpy.testing.assert_array_equal(expected_user_agents, ml_df['user_agent'].to_numpy())

        # Suspicious referer
        expected_statuses = np.array([1, 0, 0, 0])
        numpy.testing.assert_array_equal(expected_statuses, ml_df['suspicious_referer'].to_numpy())

        # Suspicious agent
        expected_statuses = np.array([0, 0, 1, 1])
        numpy.testing.assert_array_equal(expected_statuses, ml_df['suspicious_agent'].to_numpy())

        # Reserved words
        expected_statuses = np.array([0, 1, 0, 0])
        numpy.testing.assert_array_equal(expected_statuses, ml_df['reserved_words'].to_numpy())

        # Error statuses
        expected_statuses = np.array([0, 1, 0, 0])
        numpy.testing.assert_array_equal(expected_statuses, ml_df['err_status'].to_numpy())

        # '%' sign count
        expected_statuses = np.array([0, 0, 0, 0])
        numpy.testing.assert_array_equal(expected_statuses, ml_df['prec_sign_count'].to_numpy())

        # Session request count
        expected_statuses = np.array([1, 1, 2, 2])
        numpy.testing.assert_array_equal(expected_statuses, ml_df['session_request_count'].to_numpy())

        # Session request count per second
        expected_statuses = np.array([0, 0, 0.057143, 0.057143])
        numpy.testing.assert_array_almost_equal(expected_statuses, ml_df['session_request_count_per_second'].to_numpy())

        # Session same count
        expected_statuses = np.array([1, 1, 2, 2])
        numpy.testing.assert_array_equal(expected_statuses, ml_df['session_same_count'].to_numpy())

    def test_e2e_parsing_and_creating_visualization_data():
        # Setup
        ALparser = ApacheLogParser('../../data/test/bad-user-agents-test.list', '../../data/test/bad-referer-test.list')
        file_reader.read_logs_file(ALparser, 'test/input1')

        # Get Visualization formatted logs
        vs_logs = ALparser.getVisualizationFormattedLogs()

        ## ASSERTIONS

        activity0 = {'caseId': '0_session1', 'Activity': 'End', 'index': 0}
        activity1_1 = {'caseId': '1_session1', 'Activity': '/admin/blog/tags/puppet', 'index': 0}
        activity1_2 = {'caseId': '1_session1', 'Activity': 'End', 'index': 1}
        activity2_1 = {'caseId': '2_session1', 'Activity': '/robots.txt', 'index': 0}
        activity2_2 = {'caseId': '2_session1', 'Activity': '/robots.txt', 'index': 1}
        activity2_3 = {'caseId': '2_session1', 'Activity': 'End', 'index': 2}

        # Logs
        expected_logs = np.array([activity0, activity1_1, activity1_2, activity2_1, activity2_2, activity2_3])
        numpy.testing.assert_array_equal(expected_logs, np.array(vs_logs))

    



if __name__ == '__main__':
    fail_count = 0
    tests = [Test.test_e2e_parsing_and_creating_ml_df,
            Test.test_e2e_parsing_and_creating_visualization_data]
    for case in tests:
        try:
            case()
        except AssertionError as e:
            print(e)
            fail_count += 1
        except Exception as any_e:
            fail_count += 1
            raise any_e

    if not fail_count:
        print(f"=====\nAll {len(tests)} tests successful\n=====")
    else:
        print(f"=====\n{len(tests)-fail_count}/{len(tests)} tests successful\n=====")