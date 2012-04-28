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
from taskcoachlib.i18n import _
from taskcoachlib.domain import effort, date
import base


class NewEffortCommand(base.BaseCommand):
    plural_name = _('New efforts')
    singular_name = _('New effort of "%s"')
    
    def __init__(self, *args, **kwargs):
        super(NewEffortCommand, self).__init__(*args, **kwargs)
        self.items = self.efforts = [effort.Effort(task) for task in self.items]
        self.__oldActualStartDateTimes = {}

    def name_subject(self, effort):  # pylint: disable-msg=W0621
        return effort.task().subject()
        
    @patterns.eventSource
    def do_command(self, event=None):
        for effort in self.efforts:  # pylint: disable-msg=W0621
            task = effort.task()
            if task not in self.__oldActualStartDateTimes and effort.getStart() < task.actualStartDateTime():
                self.__oldActualStartDateTimes[task] = task.actualStartDateTime()
                task.setActualStartDateTime(effort.getStart())
            task.addEffort(effort, event=event)
            
    @patterns.eventSource
    def undo_command(self, event=None):
        for effort in self.efforts:  # pylint: disable-msg=W0621
            task = effort.task()
            task.removeEffort(effort, event=event)
            if task in self.__oldActualStartDateTimes:
                task.setActualStartDateTime(self.__oldActualStartDateTimes[task])
                del self.__oldActualStartDateTimes[task]
            
    redo_command = do_command
    

class DeleteEffortCommand(base.DeleteCommand):
    plural_name = _('Delete efforts')
    singular_name = _('Delete effort "%s"')
    
    
class EditTaskCommand(base.BaseCommand):
    plural_name = _('Change task of effort')
    singular_name = _('Change task of "%s" effort')
    
    def __init__(self, *args, **kwargs):
        self.__task = kwargs.pop('newValue')
        super(EditTaskCommand, self).__init__(*args, **kwargs)
        self.__oldTasks = [item.task() for item in self.items]
        
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setTask(self.__task, event=event)
            
    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldTask in zip(self.items, self.__oldTasks):
            item.setTask(oldTask, event=event)

    def redo_command(self):
        self.do_command()


class EditEffortStartDateTimeCommand(base.BaseCommand):
    plural_name = _('Change effort start date and time')
    singular_name = _('Change effort start date and time of "%s"')
    
    def __init__(self, *args, **kwargs):
        self.__datetime = kwargs.pop('newValue')
        super(EditEffortStartDateTimeCommand, self).__init__(*args, **kwargs)
        self.__oldDateTimes = [item.getStart() for item in self.items]
        self.__oldActualStartDateTimes = {}
        
    def canDo(self):
        maxDateTime = date.DateTime()
        return super(EditEffortStartDateTimeCommand, self).canDo() and \
            all(self.__datetime < (item.getStop() or maxDateTime) for item in self.items)
        
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setStart(self.__datetime, event=event)
            task = item.task()
            if task not in self.__oldActualStartDateTimes and self.__datetime < task.actualStartDateTime():
                self.__oldActualStartDateTimes[task] = task.actualStartDateTime()
                task.setActualStartDateTime(self.__datetime)
            
    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldDateTime in zip(self.items, self.__oldDateTimes):
            item.setStart(oldDateTime, event=event)
            task = item.task()
            if task in self.__oldActualStartDateTimes:
                task.setActualStartDateTime(self.__oldActualStartDateTimes[task])
                del self.__oldActualStartDateTimes[task]
                
    def redo_command(self):
        self.do_command()


class EditEffortStopDateTimeCommand(base.BaseCommand):
    plural_name = _('Change effort stop date and time')
    singular_name = _('Change effort stop date and time of "%s"')
    
    def __init__(self, *args, **kwargs):
        self.__datetime = kwargs.pop('newValue')
        super(EditEffortStopDateTimeCommand, self).__init__(*args, **kwargs)
        self.__oldDateTimes = [item.getStop() for item in self.items]

    def canDo(self):
        return super(EditEffortStopDateTimeCommand, self).canDo() and \
            all(self.__datetime > item.getStart() for item in self.items)
                
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setStop(self.__datetime, event=event)
            
    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldDateTime in zip(self.items, self.__oldDateTimes):
            item.setStop(oldDateTime, event=event)

    def redo_command(self):
        self.do_command()
