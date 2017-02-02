#!/usr/bin/env python2.7

"""tests of the aspectus.lambda_handler function"""

import unittest

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import aspectus

import icalendar

def mock_gen_ical(place, lookaheaddays, start):
    """mock aspectus.generate_icalendar function returning an empty ical"""
    # pylint:disable=unused-argument
    cal = icalendar.Calendar()
    return cal

class TestLambdaHndler(unittest.TestCase): \
        # pylint:disable=too-many-public-methods
        # they're all inherited!

    """container for test cases"""

    def setUp(self):
        """install the mock function"""
        self.real_generate_icalendar_ = aspectus.generate_icalendar
        aspectus.generate_icalendar = mock_gen_ical

    def test_good(self):
        """test that we get a reasonable response"""
        resp = aspectus.lambda_handler(
            {
                'httpMethod': 'GET',
                'queryStringParameters': {
                    'place': 'Avon, North Carolina',
                    'lookaheaddays': '1',
                    'startdatetime': '2017/01/01 00:00:00Z-0500'
                }
            },
            None)
        self.assertIn('statusCode', resp)
        self.assertEqual(resp['statusCode'], '200')

    def tearDown(self):
        """uninstall the mock function"""
        aspectus.generate_icalendar = self.real_generate_icalendar_
