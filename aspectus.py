#!/usr/bin/env python2.7

# aspectus: aspect+prospectus. iCalendars with astrological aspect events.
# Copyright (C) 2017 Frederick Eugene Aumson
# gene@aumson.org -- 12 Dogwood Ln; Flint Hill, VA 22627-1836
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""aspectus: aspect+prospectus. Generates iCalendar .ics files to populate your
calendar application with events for astrological aspects (angles) between two
celestial bodies.  Currently supports only the trine and sextant aspects, and
only between the sun and the earth. Could easily be extended to support other
bodies besides the sun, and perhaps with not much more work extended to support
aspects between two bodies outside of Earth.
"""

from icalendar import Calendar, Event
from ephem import Observer, Sun, Body # pylint:disable=no-name-in-module
from dateutil.tz import gettz
from geopy.geocoders import Nominatim
from datetime import timedelta, datetime
from math import degrees, radians
from logging import info, debug, getLogger, DEBUG

class AltitudeNotFound(Exception):
    """Raised by find_altitude when no altitude can be found"""
    pass

def find_altitude(body, observer, altitudes, step, stop):
    """Searches forward through time for the next moment at which :param body
    can be observed by :param observer to be at one of the given :param
    altitudes (a list of float degrees), starting from the datetime contained
    in :param observer, incrementing by :param step in each iteration, and
    raising AltitudeNotFound if :param stop is reached.  Returns a pair whose
    first value is the altitude found and whose second value is the (datetime)
    moment at which that altitude occurs.  :param observer should be already
    initialized with a datetime and location.  body.compute(observer) should
    already have been called.
    """
    # many thanks to http://codereview.stackexchange.com/a/153972/85827
    debug('find_altitude(%s, %s, %s, %s, %s)', body, observer, altitudes, step,
            stop)

    assert isinstance(body, Body)
    assert isinstance(observer, Observer)
    assert isinstance(step, timedelta)
    assert isinstance(stop, datetime)
    assert [altitude is float and 0 <= altitude and altitude <= 360 \
            for altitude in altitudes]

    current_alt = degrees(body.alt)

    while True:
        # capture each altitude's relation to curr_alt before step forward
        before = [altitude < current_alt for altitude in altitudes]

        # step observer date forward
        observer.date = observer.date.datetime() + step
        if observer.date.datetime() > stop:
            info('reached latest date')
            raise AltitudeNotFound
        observer.epoch = observer.date
        body.compute(observer)
        current_alt = degrees(body.alt)
        debug('%s %s', current_alt, observer)

        # if any altitude is "close enough", return it
        for altitude in altitudes:
            if abs(altitude - current_alt) < abs(altitude * 0.00001):
                # step forward to prevent double-catching this altitude
                observer.date = observer.date.datetime() + \
                        timedelta(seconds=step.total_seconds()*10)
                observer.epoch = observer.date
                body.compute(observer)
                info('found %s at %s', current_alt, observer)
                return (altitude, observer.date.datetime())

        # capture each altitude's relation to cur_alt after step forward
        after = [altitude < current_alt for altitude in altitudes]

        # an altitude whose relation changed was passed by the step forward.
        # if there is such an altitude, step the observer date backwards, to
        # "un-pass" the altitude, and then recurse, with a finer-grained step.
        changes = [delta[0] != delta[1] for delta in zip(before, after)]
        for index, changed in enumerate(changes):
            if changed:
                observer.date = observer.date.datetime() - step
                observer.epoch = observer.date
                body.compute(observer)
                return find_altitude(body, observer, [altitudes[index]],
                        timedelta(seconds=step.total_seconds()/10), stop)

def generate_icalendar(place, lookaheaddays, start):
    """generate icalendar containing events for all sun alignments at the place
    described by string :param place, looking by int()-compatible string :param
    lookaheaddays number of days, optionally starting from the optional
    dateutil.parser-compatible string :param start, which is extrapolated to a
    datetime at midnight UTC.
    """
    debug('generate_icalendar(%s, %s, %s)', place, lookaheaddays, start)

    location = Nominatim().geocode(place)

    observer = Observer()
    observer.lat = radians(location.latitude)
    observer.lon = radians(location.longitude)
    if start is not None and len(start) != 0:
        debug('start is "%s", type is "%s"', start, type(start))
        from dateutil.parser import parse
        observer.date = parse(start)
    observer.epoch = observer.date

    startdate = observer.date.datetime()

    sun = Sun()
    sun.compute(observer)

    cal = Calendar()
    cal.add('prodid',
            '-//gene@aumson.org//'
            'https://github.com/feuGeneA/aspectus//EN')
            # embed revision number into URL above
    cal.add('version', '2.0') # iCalendar spec version, not prodid version
    cal_has_events = False

    while observer.date.datetime() < \
            startdate + timedelta(days=int(lookaheaddays)):
        try:
            altitude, moment = find_altitude(sun, observer, [30, -30],
                    timedelta(hours=1),
                    startdate + timedelta(days=int(lookaheaddays)))
        except AltitudeNotFound:
            break
        event = Event()
        if altitude == 30:
            event.add('summary', 'Sun-earth Trine, at '+place)
        elif altitude == -30:
            event.add('summary', 'Sun-earth Sextant, at '+place)
        event.add('dtstart', moment.replace(tzinfo=gettz('UTC')))
        event.add('dtend', \
                moment.replace(tzinfo=gettz('UTC')) +timedelta(seconds=1))

        cal.add_component(event)
        cal_has_events = True

    if cal_has_events:
        return cal
    else:
        return None

def lambda_handler(event, context): # pylint:disable=unused-argument
    """handle event from AWS lambda"""
    getLogger().setLevel(DEBUG)
    debug('lambda_handler(%s, %s)', event, context)
    assert 'queryStringParameters' in event
    assert 'place' in event['queryStringParameters']
    assert 'lookaheaddays' in event['queryStringParameters']

    cal = generate_icalendar( \
            event['queryStringParameters']['place'],
            event['queryStringParameters']['lookaheaddays'],
            event['queryStringParameters']['startdate'] \
                if 'startdate' in event['queryStringParameters'] else None)

    if cal is None:
        return {'statusCode': '204'}
    else:
        return {
            'statusCode': '200',
            'body': cal.to_ical(),
            'headers': {
                'Content-Type': 'text/calendar',
                'Content-Disposition': \
                        'attachment; filename="Sun-earth aspects at '+\
                                event['queryStringParameters']['place']+'.ics"'
            },
        }

def main():
    """use command-line arguments as input and produce .ics file on stdout"""
    from sys import argv
    cal = generate_icalendar(argv[1], argv[2], None)
    print cal.to_ical()

if __name__ == "__main__":
    main()
