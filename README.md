aspectus
===
*Chart upcoming astrological aspects*

Import events into your Google Calendar (or other favorite iCalendar application) for recurring angles between celestial bodies.

### Development status
aspectus currently supports only trine and sextant aspects, and only between the Earth and Sun.

The sun-earth trine and sextant aspects are are derived from the altitude of the Sun.  A solar altitude of 30 degrees implies the 120 degree trine aspect, comrpised of the 30 degrees between lines from observer to sun and from observer to horizon, plus the 90 degrees between the lines from observer to horizon and from to observer to center of Earth.  A solar altitude of -30 degrees implies the 60 degree sextant aspect, comprised of the -30 degrees between lines from observer to horizon and from observer to the sun (below the horizon), and the -90 degrees between the lines from observer to horizon and observer to the center of the earth.

### Backlog of potential improvements
* As a user, I want all of the events for a particular aspect, and at a specific location, to be one recurring event, rather than separate independent calendar entries, so that I might delete all of them in one fell swoop from my calendar application.

* As a user, I want to specify a number of minutes ahead of the alignment at which I will be notified by my calendar application, so that I don't get stuck with the application's default (30 minutes for Google Calendar), or, worse yet, so that I don't have no alarm at all. (Add VALARM components to the events.)

* As a user, I want to pass calendar-generation options via the command line, so that I can generate a calendar by running the python script directly, rather than relying on an online instance of the service.

* As a user, I want to chart aspects with other bodies instead of the Sun.  (Should be very easy to implement.)

* As a user, rather than the alignment events being a single moment in time, I want them to have a duration, using an astrological "orb" based on the size of the body in angular distance, so that I understand how long the alignment is having an effect.  (Use pyehem.body.size, which is diameter in arcseconds.)

* As a user, I want to chart other aspects besides trines and sextants.  (Should be not *too* much work to implement.)

* As a user I want to chart aspects between two celestial bodes outside of earth.  (Would be great to have, but would be much work to implement, as it would not be well supported by the current altitude-based algorithms.)

* As a user, I want the performance improvements suggested by http://codereview.stackexchange.com/a/153972/85827.  (Primarily, use ephem.newton() instead of recursion.  Also consider sort/bisect instead of list comprehensions, and consider minimizing data type conversions.  After, consider "start, stop, step" idiom to eliminate observer and body initialization preconditions.)

### Backlog of technical debt and seeds of rot
* As a maintainer, I need Travis CI to continuously run the unit tests, upon by every commit to GitHub, with status as a badge in REAME.md, so that the fundamental functionality of the code is always known to be in a usable state.

* As a maintainer, I need a Selenium deployment test, in order to test the generated form.html.  Then, I need that deployment test integrated into the local deploy and test pipeline, so that I don't have to remember to run it; specifically, I want a Selenium execution target in the Makefile, which depends on the form.html target, and then I want the all: target to go away in favor of delivery_test: first being first target in the file.

* As a maintainer, I need my AWS credentials securely conveyed to Travis CI, so that every commit can also enable continuous deployment in addition to continuous unit testing.
Likely define encrypted variables in .travis.yml.  See:
    * https://docs.travis-ci.com/user/environment-variables/#Defining-encrypted-variables-in-.travis.yml

    * http://docs.aws.amazon.com/cli/latest/topic/config-vars.html)
Then, I need the Selenium deployment test to be run automatically by Travis CI upon every github commit, in order to achieve continuous deployment testing.  (Use Sauce Labs as in https://docs.travis-ci.com/user/gui-and-headless-browsers/.)

* As a maintainer, I need the aspectus.find_altitude method to conform to the "start, stop, step" argument convention, so that the code is easier to comprehend.  (Consider having stop be a timedelta, so that a default parameter value can be specified in the interface.

* As a tester of the web service, I need any Python exceptions to be conveyed as part of the body of an HTTP 500 response, so that if something goes wrong I have some indication of what the problem was.
