#!/usr/bin/env python2.7

"""test various usages of the aspectus.find_altitude function"""

import unittest

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import aspectus

from datetime import timedelta
from dateutil.parser import parse
from dateutil.tz import gettz
from ephem import Observer, Sun, degrees # pylint:disable=no-name-in-module

class TestFindAltitude(unittest.TestCase): \
        # pylint:disable=too-many-public-methods
        # they're all inherited!

    """container of test cases"""

    def test_one(self):
        """test case of a known-good aspect event"""
        body = Sun()

        observer = Observer()
        observer.date = \
                parse('2017/01/01 00:00:00Z-0500').astimezone(gettz('UTC')) # pylint:disable=maybe-no-member
        observer.lat = degrees('37.7625')
        observer.lon = degrees('-78.1002')

        body.compute(observer)
        altitude, moment = aspectus.find_altitude(body, observer, [30, -30], \
                timedelta(hours=1), observer.date.datetime()+timedelta(days=2))
        self.assertEqual(altitude, -30)
        self.assertEqual(moment, parse('2017/01/01 00:39:50.111983'))

    def test_not_found(self):
        """ test case of no expected events within given time frame"""
        body = Sun()

        observer = Observer()
        observer.date = \
                parse('2017/01/01 00:00:00Z-0500').astimezone(gettz('UTC')) # pylint:disable=maybe-no-member
        observer.lat = degrees('37.7625')
        observer.lon = degrees('-78.1002')

        body.compute(observer)
        self.assertRaises(aspectus.AltitudeNotFound, aspectus.find_altitude,
                body, observer, [30, -30], timedelta(hours=1),
                observer.date.datetime()+timedelta(minutes=38))

if __name__ == "__main__":
    unittest.main()
