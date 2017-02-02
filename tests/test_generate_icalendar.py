#!/usr/bin/env python2.7

"""unit tests for the aspectus.generate_icalendar function"""

import unittest

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import aspectus

from datetime import timedelta
import icalendar

def mock_find_altitude(body, observer, targets, step, latest_date):
    """mock aspectus.find_altitude that seemingly returns a legitimate
    altitude/moment
    """
    # pylint:disable=unused-argument
    observer.date = observer.date.datetime()+timedelta(days=1)
    return (targets[0], observer.date.datetime())

def mock_find_altitude_none_found(body, observer, targets, step, latest_date):
    """mock aspectus.find_altitude that finds no suitable altitude"""
    # pylint:disable=unused-argument
    raise aspectus.AltitudeNotFound

class TestGenerateiCalendarInIsolation(unittest.TestCase): \
        # pylint:disable=too-many-public-methods
        # they're all inherited!

    """test cases using a mock find_altitude which returns a legitimate
    result
    """

    def setUp(self):
        """install the mock"""
        self.real_find_altitude_ = aspectus.find_altitude
        aspectus.find_altitude = mock_find_altitude

    def test_one_day_out(self):
        """test that we get a calendar object with some content lines"""
        cal = aspectus.generate_icalendar('avon nc', '1', None)
        self.assertIsInstance(cal, icalendar.Calendar)
        self.assertTrue(len(cal.content_lines()) > 0)

    def tearDown(self):
        """uninstall the mock"""
        aspectus.find_altitude = self.real_find_altitude_

class TestGenerateiCalendar(unittest.TestCase): \
        # pylint:disable=too-many-public-methods
        # they're all inherited!
    """test generate_icalendar without any mocks"""
    def test_one_day_out(self):
        """test that we get a calendar object with some content lines"""
        cal = aspectus.generate_icalendar('avon nc', '1', None)
        self.assertIsInstance(cal, icalendar.Calendar)
        self.assertTrue(len(cal.content_lines()) > 0)

class TestGenerateiCalendarNoEvents(unittest.TestCase): \
        # pylint:disable=too-many-public-methods
        # they're all inherited!

    """test cases using a mock find_altitude that doesn't find anything"""

    def setUp(self):
        """install the mock"""
        self.real_find_altitude_ = aspectus.find_altitude
        aspectus.find_altitude = mock_find_altitude_none_found

    def test_one_day_out(self):
        """test case of no aspect found"""
        self.assertIsNone(aspectus.generate_icalendar('avon nc', '1', None))

    def tearDown(self):
        """uninstall the mock"""
        aspectus.find_altitude = self.real_find_altitude_

if __name__ == "__main__":
    unittest.main()
