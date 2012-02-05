'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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

from taskcoachlib import patterns
from taskcoachlib.domain import base
import task


class ViewFilter(base.Filter):
    def __init__(self, *args, **kwargs):
        self.__statusesToHide = set()
        for status in task.Task.possibleStatuses():
            if kwargs.pop('hide%sTasks'%status.capitalize(), False):
                self.__statusesToHide.add(status)
        self.__hideCompositeTasks = kwargs.pop('hideCompositeTasks', False)
        self.registerObservers()
        super(ViewFilter, self).__init__(*args, **kwargs)
        
    def registerObservers(self):
        registerObserver = patterns.Publisher().registerObserver
        for eventType in ('task.actualStartDateTime', 'task.plannedStartDateTime',
                          'task.dueDateTime', 'task.completionDateTime', 
                          'task.prerequisites',
                          task.Task.appearanceChangedEventType(), # Proxy for status changes
                          task.Task.addChildEventType(),
                          task.Task.removeChildEventType(),
                          'clock.day'):
            registerObserver(self.onTaskStatusChange, eventType=eventType)

    def onTaskStatusChange(self, event): # pylint: disable-msg=W0613
        self.reset()
        
    def hideTaskStatus(self, status, hide=True):
        if hide:
            self.__statusesToHide.add(status)
        else:
            self.__statusesToHide.discard(status)
        self.reset()
                       
    def hideCompositeTasks(self, hide=True):
        self.__hideCompositeTasks = hide
        self.reset()
        
    def filter(self, tasks):
        return [task for task in tasks if self.filterTask(task)] # pylint: disable-msg=W0621
    
    def filterTask(self, task): # pylint: disable-msg=W0621
        result = True
        if task.status() in self.__statusesToHide:
            result = False
        elif self.__hideCompositeTasks and not self.treeMode() and task.children():
            result = False # Hide composite task
        return result
