#!/usr/bin/env python2.7

""" sun stations """

from geopy.geocoders import Nominatim
from ephem import Observer, Sun #pylint: disable=no-name-in-module
from datetime import datetime, timedelta
from math import degrees, radians
from pytz import utc
from icalendar import Calendar, Event

def find_altitude(targets, body, observer, step, max_lookahead):
    """ returns the next point in time at which the ephem Body :param body will
    be at one of the altitudes found in the list :param targets, using the
    ephem Observer :param observer and stepping its date forward by
    datetime.timedelta :param step in each iteration. Returns None if a target
    is not found after having looked ahead datetime.timedelta :param
    max_lookahead. :param targets should be a list of floats representing
    altitudes in degrees. :param step should be about an hour or less. :param
    observer should be already initialized with a date and location. """

    #print 'find_altitude', targets, body, observer, step, max_lookahead

    # determine how close the altitude needs to be to a target in order for
    # us to recurse with a finer step.
    # generalized assumption: in a 12 hour day, sun goes from 0 degrees to
    # 90 and back down to 0, so it moves from 0 to 90 in 6 hours.
    degrees_per_second = 90/timedelta(hours=6).total_seconds()
    # target should be within "degrees per step" in order to recurse.
    recursion_tolerance = degrees_per_second * step.total_seconds()

    beginning_datetime = observer.date.datetime()

    body.compute(observer)
    prev_altitude = degrees(float(repr(body.alt)))

    while observer.date.datetime() < \
          observer.date.datetime() + max_lookahead:

        observer.date = observer.date.datetime() + step
        body.compute(observer)

        altitude = degrees(float(repr(body.alt)))

        for target in targets:
            past_target = \
                True if altitude > target and altitude-prev_altitude > 0 else (
                True if altitude < target and altitude-prev_altitude < 0 else \
                    False)

            # determine how close to the target we need to be in order to say
            # we found it
            target_tolerance = target * 0.00001

            if abs(target - altitude) < target_tolerance:
                return {'target': altitude, 'date': observer.date.datetime()}
            elif not past_target and abs(target-altitude) < recursion_tolerance:
                return find_altitude([target], body, observer, \
                        timedelta(seconds=step.total_seconds()/10), \
                        max_lookahead - (observer.date.datetime() \
                                         - beginning_datetime))

        prev_altitude = altitude

def lambda_handler(event, context): #pylint: disable=unused-argument
    """ handle event from AWS lambda """

    place = event['queryStringParameters']['place']
    lookaheaddays = event['queryStringParameters']['lookaheaddays']

    location = Nominatim().geocode(place)

    observer = Observer()
    observer.lat = radians(location.latitude)
    observer.lon = radians(location.longitude)
    observer.date = datetime.utcnow()

    sun = Sun()

    cal = Calendar()
    cal.add('prodid',
            '-//gene@aumson.org//'
            'https://github.com/feuGeneA/socalgen//EN')
            # embed revision number into URL above
    cal.add('version', '2.0') # iCalendar spec version, not prodid version

    while observer.date.datetime() < \
            datetime.utcnow() + timedelta(days=int(lookaheaddays)):

        find = find_altitude([30], sun, observer, timedelta(minutes=2), \
                timedelta(hours=24))

        event = Event()
        event.add('summary', 'Sun-earth Trine, at '+place)
        event.add('dtstart', find['date'].replace(tzinfo=utc))
        event.add('dtend', \
                find['date'].replace(tzinfo=utc)+timedelta(seconds=1))

        cal.add_component(event)

    return {
        'statusCode': '200',
        'body': cal.to_ical(),
        'headers': {
            'Content-Type': 'text/calendar',
            'Content-Disposition': \
                    'attachment; filename="sun-earth trines at '+place+'.ics"'
        },
    }

if __name__ == "__main__":
    print \
        lambda_handler(
            {
                'httpMethod': 'GET',
                'queryStringParameters': {
                    'place': 'avon, nc',
                    'lookaheaddays': '1'
                }
            },
            None)['body']
