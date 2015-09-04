#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Zoe madtrans
# https://github.com/rmed/zoe-madtrans
#
# Copyright (c) 2015 Rafael Medina García <rafamedgar@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
sys.path.append('./lib')

import gettext
import requests
import zoe
from os import environ as env
from os.path import join as path
from zoe.deco import *

gettext.install('madtrans')

LOCALEDIR = path(env['ZOE_HOME'], 'locale')
ZOE_LOCALE = env['ZOE_LOCALE'] or 'en'

BASE_URL = 'https://openbus.emtmadrid.es:9443/emt-proxy-server/last/'
# Not all of these are used!
API = {
    'bus_calendar'           : 'bus/GetCalendar.php',
    'bus_groups'             : 'bus/GetGroups.php',
    'bus_list_lines'         : 'bus/GetListLines.php',
    'bus_nodes_lines'        : 'bus/GetNodesLines.php',
    'bus_route_lines'        : 'bus/GetRouteLines.php',
    'bus_route_lines_route'  : 'bus/GetRouteLinesRoute.php',
    'bus_times_lines'        : 'bus/GetTimeslines.php',
    'bus_timetable_lines'    : 'bus/GetTimeTableLines.php',

    'geo_arrive_stop'        : 'geo/GetArriveStop.php',
    'geo_groups'             : 'geo/GetGroups.php',
    'geo_info_line'          : 'geo/GetInfoLine.php',
    'geo_info_line_extended' : 'geo/GetInfoLineExtend.php',
    'geo_stops_from_stop'    : 'geo/GetStopsFromStop.php',
    'geo_stops_line'         : 'geo/GetStopsLine.php',
    'geo_street'             : 'geo/GetStreet.php',
}

with open(path(env['ZOE_HOME'], 'etc', 'archivist.conf'), 'r') as f:
    EMT_ID = f.readline().strip()
    EMT_PWD = f.readline().strip()


@Agent(name='madtrans')
class Madtrans:

    @Message(tags=['bus-calendar'])
    def bus_calendar(self, parser):
        """ Get EMT calendar for all days and line schedules for a
            range of dates.

            API requires:
                SelectDateBegin - dd/mm/yyyy start date
                SelectDateEnd   - dd/mm/yyyy end date
        """
        sender = parser.get('sender')
        src = parser.get('src')
        self.set_locale(sender)

        params = {}
        params['SelectDateBegin'] = parser.get('sdate').replace('-', '/')
        params['SelectDateEnd'] = parser.get('edate').replace('-', '/')

        response = self.make_request('bus_calendar', params)

        if response['resultCode'] != 0:
            return self.feedback(
                _('ERROR: %s') % response['resultDescription'],
                sender, src)

        # Message will contain day and the type of day
        # (Laborable, Festive, Saturday) for applicable timetables
        msg = ''
        for d in response['resultValues']:
            msg += '- %s %s: %s\n' % (
                self.day_week(d['dayOfWeek']),
                d['date'][:10],
                self.day_type(d['dayType']))

        return self.feedback(msg, sender, src)

    @Message(tags=['bus-list-lines'])
    def bus_list_lines(self, parser):
        """ Get information on all lines with description.

            API requires:
                SelectDate - dd/mm/yyyy
                Lines      - | separated line numbers (if empty, returns all)
        """
        sender = parser.get('sender')
        src = parser.get('src')
        self.set_locale(sender)

        params = {}
        params['selectDate'] = parser.get('date').replace('-', '/')
        params['Lines'] = parser.get('lines').replace(' ', '|')
        response = self.make_request('bus_list_lines', params)

        if response['resultCode'] != 0:
            return self.feedback(
                _('ERROR: %s') % response['resultDescription'],
                sender, src)

        msg = ''
        for l in response['resultValues']:
            msg += '- '
            msg += _('Line')
            msg += ' %s: %s - %s\n' % (l['label'], l['nameA'], l['nameB'])

        return self.feedback(msg, sender, src)

    @Message(tags=['bus-nodes-lines'])
    def bus_nodes_lines(self, parser):
        """ Get information on stops.

            API requires:
                Nodes - | separated stop number (if empty, returns all)
        """
        sender = parser.get('sender')
        src = parser.get('src')
        self.set_locale(sender)

        params = {}
        params['Nodes'] = parser.get('stops').replace(' ', '|')
        response = self.make_request('bus_nodes_list', params)

        msg = ''
        for s in response['resultValues']:
            msg += '- %d: %s (%s)\n' % (s['node'], s['name'], s['lines'])

        return self.feedback(msg, sender, src)

    @Message(tags=['bus-route-lines'])
    def bus_route_lines(self, parser):
        """ Get stops for a given line.

            We only work with a single line each time.

            API requires:
                SelectDate  - dd/mm/yyyy
                Lines       - line numbers
        """
        sender = parser.get('sender')
        src = parser.get('src')
        self.set_locale(sender)

        params = {}
        params['SelectDate'] = parser.get('date').replace('-', '/')
        params['Lines'] = parser.get('line')
        response = self.make_request('bus_route_list', params)

        msg = ''
        for l in response['resultValues']:
            msg += '- %s (%d)\n' % (l['name'], l['node'])
            msg += _('Distance from origin: %d\n') % l['distance']
            msg += _('Distance from previous stop: %d\n\n') % l['distancePreviousStop']

        return self.feedback(msg, sender, src)

    @Message(tags=['bus-times-lines'])
    def bus_times_lines(self, parser):
        """ Get current schedules for requested lines.

            We only work with a single line each time.

            API requires:
                SelectDate  - dd/mm/yyyy
                lines       - | separated lines
        """
        sender = parser.get('sender')
        src = parser.get('src')
        self.set_locale(sender)

        params = {}
        params['SelectDate'] = parser.get('date').replace('-', '/')
        params['line'] = parser.get('line')
        response = self.make_request('bus_route_list', params)

        msg = ''
        for l in response['resultValues']:
            msg += '- '
            msg += _('Line')
            msg += ' %s (%s)\n' % (l['line'], self.day_type(l['typeDay']))
            msg += _('From: %s\n') % l['dateFirst']
            msg += _('To: %s\n') % l['dateEnd']
            msg += _('First (A): %s\n') % l['timeFirstA']
            msg += _('Last (A): %s\n') % l['timeEndA']
            msg += _('First (B): %s\n') % l['timeFirstB']
            msg += _('Last (B): %s\n') % l['timeEndB']
            msg += '\n'

        return self.feedback(msg, sender, src)

    @Message(tags=['geo-arrive-stop'])
    def geo_arrive_stop(self, parser):
        """ Get bus arrive info at specified stop.

            API requires:
                idStop      - stop number
                cultureInfo - locale for result
        """
        sender = parser.get('sender')
        src = parser.get('src')
        lang = self.set_locale(sender)

        params = {}
        params['idStop'] = parser.get('stop')
        params['cultureInfo'] = lang
        response = self.make_request('geo_arrive_stop', params)

        msg = ''
        for a in response['arrives']:
            mins, secs = divmod(a['busTimeLeft'], 60)
            msg += '- '
            msg += '%s: %s\n' % (a['lineId'], a['destination'])
            msg += _('Time left')
            msg += ': %d:%d\n' % (mins, secs)
            msg += _('Bus distance: %d m\n\n') % a['busDistance']

        return self.feedback(msg, sender, src)

    @Message(tags=['geo-info-line-extended'])
    def geo_info_line_extended(self, parser):
        """ Get information on a given line.

            API requires:
                fecha       - dd/mm/yyyy
                line        - line number
                cultureInfo - locale for result
        """
        sender = parser.get('sender')
        src = parser.get('src')
        lang = self.set_locale(sender)

        params = {}
        params['fecha'] = parser.get('date').replace('-', '/')
        params['line'] = parser.get('line')
        params['cultureInfo'] = lang
        response = self.make_request('geo_info_line_extended', params)
        line = response['Line']

        msg = _('Line')
        msg += ' %s: %s - %s\n' % (line['label'], line['headerA'],
            line['headerB'])
        msg += _('Incidents: %d\n') % line['incidents']

        for d in line['dayType']:
            msg += '- %s\n' % d['dayTypeId']
            msg += _('Direction 1: %s\n') % d['direction1']['frequencyDescription']
            msg += _('Direction 2: %s\n\n') % d['direction2']['frequencyDescription']

        return self.feedback(msg, sender, src)

    @Message(tags=['gep-stops-from-stop'])
    def geo_stops_from_stop(self, parser):
        """ Get stops from a given radius of the specified stop and
            information such as lines arriving to those stops.

            API requires:
                idStop      - id of the stop to search
                Radius      - radius in meters
                cultureInfo - locale for result
        """
        sender = parser.get('sender')
        src = parser.get('src')
        lang = self.set_locale(sender)

        params = {}
        params['idStop'] = parser.get('stop')
        params['Radius'] = parser.get('radius')
        params['cultureInfo'] = lang
        response = self.make_request('geo_stops_from_stop', params)

        msg = ''
        for s in response['stops']:
            msg += '- %s (%s): %s\n' % (s['name'], s['stopId'],
                s['postalAddress'])
            msg += _('Lines: ')

            if type(s['line']) == list:
                for l in s['line']:
                    msg += '%s ' % l['label']

            else:
                msg += s['line']['label']

        return self.feedback(msg, sender, src)

    def day_week(self, day):
        """ Parse the dayOfWeek from a response and return human
            readable format.
        """
        if day == 'L':
            return _('Monday')
        elif day == 'M':
            return _('Tuesday')
        elif day == 'X':
            return _('Wednesday')
        elif day == 'J':
            return _('Thursday')
        elif day == 'V':
            return _('Friday')
        elif day == 'S':
            return _('Saturday')
        elif day == 'D':
            return _('Sunday')

    def day_type(self, day):
        """ Parse the dayType from the response and return human
            readable format.
        """
        if day == 'LA':
            return _('Labour day')

        elif day == 'V':
            return _('Friday')

        elif day == 'SA':
            return _('Saturday')

        elif day == 'FE':
            return _('Festive')

    def feedback(self, msg, user, dst=None):
        """ Send a message to a given user.

            msg     - message text or attachment
            user    - user to send the feedback to
            dst     - destination of the message: 'jabber' or 'tg'
        """
        if not user:
            return

        to_send = {
            'dst'     : 'relay',
            'to'      : user,
            'relayto' : dst,
            'msg'     : msg
        }

        return zoe.MessageBuilder(to_send)

    def make_request(self, path, params):
        """ Make a request to the given path and return the response
            obtained from the EMT services.

            path   - endpoint of the API
            params - dict with parameters for the request
        """
        api = BASE_URL + API['path']

        params['idClient'] = EMT_ID
        params['passKey'] = EMT_PWD

        # SSL verification fails...
        return requests.post(api, data=params, verify=False).json()

    def set_locale(self, user):
        """ Set the locale for messages based on the locale of the sender.

            If no locale is povided, Zoe's default locale is used or
            English (en) is used by default.

            Returns 'EN' or 'ES' for API calls that have localization.
        """
        if not user:
            locale = ZOE_LOCALE

        else:
            conf = zoe.Users().subject(user)
            locale = conf.get('locale', ZOE_LOCALE)

        lang = gettext.translation('madtrans', localedir=LOCALEDIR,
            languages=[locale,])

        lang.install()

        if locale == 'es':
            return 'ES'

        return 'EN'
