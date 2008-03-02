# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

''' render.py - functions to render various objects, like date, time, etc. '''

from i18n import _


def date(date):
    ''' render a date (of type date.Date) '''
    return str(date)
    
def priority(priority):
    ''' Render an (integer) priority '''
    return str(priority)
   
def daysLeft(timeLeft, completedTask):
    ''' Render time left (of type date.TimeDelta) in days. '''
    if completedTask:
        return ''
    from domain import date
    if timeLeft == date.TimeDelta.max:
        return _('Infinite') # u'∞' 
    else:
        return str(timeLeft.days)

def timeSpent(timeSpent):
    ''' render time spent (of type date.TimeDelta) as
    "<hours>:<minutes>:<seconds>" '''
    import domain.date as date
    if timeSpent < date.TimeDelta():
        sign = '-'
    else:
        sign = ''
    return sign + '%d:%02d:%02d'%timeSpent.hoursMinutesSeconds()

def recurrence(recurrenceValue):
    return {'': '', 'weekly': _('Weekly'), 
            'daily': _('Daily')}.get(recurrenceValue, recurrenceValue)

def budget(aBudget):
    ''' render budget (of type date.TimeDelta) as
    "<hours>:<minutes>:<seconds>". '''
    return timeSpent(aBudget)
        
def dateTime(dateTime):
    if dateTime:
        return dateTime.strftime('%Y-%m-%d %H:%M')
    else:
        return ''
    
def dateTimePeriod(start, stop):
    if stop is None:
        return '%s - %s'%(dateTime(start), _('now'))
    elif start.date() == stop.date():
        return '%s %s - %s'%(date(start.date()), time(start), time(stop))
    else:
        return '%s - %s'%(dateTime(start), dateTime(stop))
            
def time(dateTime):
    return dateTime.strftime('%H:%M')
    
def month(dateTime):
    return dateTime.strftime('%Y %B')
    
def weekNumber(dateTime):
    # Would have liked to use dateTime.strftime('%Y-%U'), but the week number is one off
    # in 2004
    return '%d-%d'%(dateTime.year, dateTime.weeknumber())
    
def amount(aFloat):
    return '%.2f'%aFloat

