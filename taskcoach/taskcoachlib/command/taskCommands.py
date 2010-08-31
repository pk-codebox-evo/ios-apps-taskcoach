# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

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
from taskcoachlib.domain import task, effort, date
import base


class SaveTaskStateMixin(base.SaveStateMixin, base.CompositeMixin):
    pass


class EffortCommand(base.BaseCommand): # pylint: disable-msg=W0223
    def stopTracking(self):
        self.stoppedEfforts = [] # pylint: disable-msg=W0201
        for taskToStop in self.tasksToStopTracking():
            self.stoppedEfforts.extend(taskToStop.activeEfforts())
            taskToStop.stopTracking()

    def startTracking(self):
        for stoppedEffort in self.stoppedEfforts:
            stoppedEffort.setStop(date.DateTime.max)
    
    def tasksToStopTracking(self):
        return self.list
                
    def do_command(self):
        self.stopTracking()
    
    def undo_command(self):
        self.startTracking()
        
    def redo_command(self):
        self.stopTracking()


class DragAndDropTaskCommand(base.DragAndDropCommand):
    plural_name = _('Drag and drop tasks')


class DeleteTaskCommand(base.DeleteCommand, EffortCommand):
    plural_name = _('Delete tasks')
    singular_name = _('Delete task "%s"')

    def tasksToStopTracking(self):
        return self.items

    def do_command(self):
        super(DeleteTaskCommand, self).do_command()
        self.stopTracking()
        self.removePrerequisites()
        
    def undo_command(self):
        super(DeleteTaskCommand, self).undo_command()
        self.startTracking()
        self.restorePrerequisites()
        
    def redo_command(self):
        super(DeleteTaskCommand, self).redo_command()
        self.stopTracking()
        self.removePrerequisites()
        
    @patterns.eventSource
    def removePrerequisites(self, event=None):
        self.__relationsToRestore = dict() # pylint: disable-msg=W0201
        for item in self.items:
            prerequisites, dependencies = item.prerequisites(), item.dependencies()
            self.__relationsToRestore[item] = prerequisites, dependencies
            item.removeTaskAsDependencyOf(prerequisites, event=event)
            item.removeTaskAsPrerequisiteOf(dependencies, event=event) 
                            
    @patterns.eventSource
    def restorePrerequisites(self, event=None):
        for item, (prerequisites, dependencies) in self.__relationsToRestore.items():
            item.addTaskAsDependencyOf(prerequisites, event=event)
            item.addTaskAsPrerequisiteOf(dependencies, event=event)


class NewTaskCommand(base.NewItemCommand):
    singular_name = _('New task')
    
    def __init__(self, *args, **kwargs):
        subject = kwargs.pop('subject', _('New task'))
        startDateTime = kwargs.pop('startDateTime', date.Now())
        super(NewTaskCommand, self).__init__(*args, **kwargs)
        self.items = [task.Task(subject=subject, 
                                startDateTime=startDateTime, **kwargs)]

    def do_command(self):
        super(NewTaskCommand, self).do_command()
        self.addDependenciesAndPrerequisites()
        
    def undo_command(self):
        super(NewTaskCommand, self).undo_command()
        self.removeDependenciesAndPrerequisites()
        
    def redo_command(self):
        super(NewTaskCommand, self).redo_command()
        self.addDependenciesAndPrerequisites()
        
    @patterns.eventSource
    def addDependenciesAndPrerequisites(self, event=None):
        for eachTask in self.items:
            for prerequisite in eachTask.prerequisites():
                prerequisite.addDependencies([eachTask], event=event)
            for dependency in eachTask.dependencies():
                dependency.addPrerequisites([eachTask], event=event)

    @patterns.eventSource
    def removeDependenciesAndPrerequisites(self, event=None):
        for eachTask in self.items:
            for prerequisite in eachTask.prerequisites():
                prerequisite.removeDependencies([eachTask], event=event)                                
            for dependency in eachTask.dependencies():
                dependency.removePrerequisites([eachTask], event=event)
                
                
class NewSubTaskCommand(base.NewSubItemCommand, SaveTaskStateMixin):
    plural_name = _('New subtasks')
    singular_name = _('New subtask of "%s"')

    def __init__(self, *args, **kwargs):
        super(NewSubTaskCommand, self).__init__(*args, **kwargs)
        subject = kwargs.pop('subject', _('New subtask'))
        self.items = [parent.newChild(subject=subject, **kwargs) for parent in self.items]
        self.saveStates(self.getTasksToSave())
    
    def getTasksToSave(self):
        # FIXME: can be simplified to: return self.getAncestors(self.items) ?
        parents = [item.parent() for item in self.items if item.parent()]
        return parents + self.getAncestors(parents)

    def undo_command(self):
        super(NewSubTaskCommand, self).undo_command()
        self.undoStates()

    def redo_command(self):
        super(NewSubTaskCommand, self).redo_command()
        self.redoStates()


class EditTaskCommand(base.EditCommand):
    plural_name = _('Edit tasks')
    singular_name = _('Edit task "%s"')
    
    def __init__(self, *args, **kwargs):
        super(EditTaskCommand, self).__init__(*args, **kwargs)
        self.oldCategories = [item.categories() for item in self.items]
        self.oldPrerequisites = [item.prerequisites() for item in self.items]
        
    def do_command(self):
        super(EditTaskCommand, self).do_command()
        # pylint: disable-msg=W0201
        self.newCategories = [item.categories() for item in self.items] 
        self.updateCategories(self.oldCategories, self.newCategories)
        self.newPrerequisites = [item.prerequisites() for item in self.items]
        self.updatePrerequisites(self.oldPrerequisites, self.newPrerequisites)
        
    def undo_command(self):
        super(EditTaskCommand, self).undo_command()
        self.updateCategories(self.newCategories, self.oldCategories)
        self.updatePrerequisites(self.newPrerequisites, self.oldPrerequisites)
        
    def redo_command(self):
        super(EditTaskCommand, self).redo_command()
        self.updateCategories(self.oldCategories, self.newCategories)
        self.updatePrerequisites(self.oldPrerequisites, self.newPrerequisites)
        
    def getItemsToSave(self):
        return set([relative for item in self.items for relative in item.family()])
        
    @patterns.eventSource
    def updateCategories(self, oldCategories, newCategories, event=None):
        for item, categories in zip(self.items, oldCategories):
            for category in categories:
                category.removeCategorizable(item, event=event)
        for item, categories in zip(self.items, newCategories):
            for category in categories:
                category.addCategorizable(item, event=event)

    @patterns.eventSource
    def updatePrerequisites(self, oldPrerequisites, newPrerequisites, event=None):
        for item, prerequisites in zip(self.items, oldPrerequisites):
            for prerequisite in prerequisites:
                prerequisite.removeDependencies([item], event=event)
        for item, prerequisites in zip(self.items, newPrerequisites):
            for prerequisite in prerequisites:
                prerequisite.addDependencies([item], event=event)
                
                
class MarkCompletedCommand(EditTaskCommand, EffortCommand):
    plural_name = _('Mark tasks completed')
    singular_name = _('Mark "%s" completed')

    @patterns.eventSource
    def do_command(self, event=None):
        super(MarkCompletedCommand, self).do_command()
        for item in self.items:
            if item.completed():
                item.setCompletionDateTime(date.DateTime(), event=event)
            else:
                item.setCompletionDateTime(event=event)

    def tasksToStopTracking(self):
        return self.items


class StartEffortCommand(EffortCommand):
    plural_name = _('Start tracking')
    singular_name = _('Start tracking "%s"')

    def __init__(self, *args, **kwargs):
        super(StartEffortCommand, self).__init__(*args, **kwargs)
        start = date.DateTime.now()
        self.efforts = [effort.Effort(item, start) for item in self.items]
        
    def do_command(self):
        super(StartEffortCommand, self).do_command()
        self.addEfforts()
        
    def undo_command(self):
        self.removeEfforts()
        super(StartEffortCommand, self).undo_command()
        
    def redo_command(self):
        super(StartEffortCommand, self).redo_command()
        self.addEfforts()

    @patterns.eventSource
    def addEfforts(self, event=None):
        for item, newEffort in zip(self.items, self.efforts):
            item.addEffort(newEffort, event=event)

    @patterns.eventSource
    def removeEfforts(self, event=None):
        for item, newEffort in zip(self.items, self.efforts):
            item.removeEffort(newEffort, event=event)
            
        
class StopEffortCommand(EffortCommand):
    plural_name = _('Stop tracking')
    singular_name = _('Stop tracking "%s"')
                  
    def canDo(self):
        return True # No selected items needed.


class ExtremePriorityCommand(base.BaseCommand): # pylint: disable-msg=W0223
    delta = 'Subclass responsibility'
    
    def __init__(self, *args, **kwargs):
        super(ExtremePriorityCommand, self).__init__(*args, **kwargs)
        self.oldPriorities = [item.priority() for item in self.items]
        self.oldExtremePriority = self.getOldExtremePriority()
        
    def getOldExtremePriority(self):
        raise NotImplementedError # pragma: no cover

    @patterns.eventSource
    def setNewExtremePriority(self, event=None):
        newExtremePriority = self.oldExtremePriority + self.delta 
        for item in self.items:
            item.setPriority(newExtremePriority, event=event)

    @patterns.eventSource
    def restorePriorities(self, event=None):
        for item, oldPriority in zip(self.items, self.oldPriorities):
            item.setPriority(oldPriority, event=event)

    def do_command(self):
        super(ExtremePriorityCommand, self).do_command()
        self.setNewExtremePriority()
        
    def undo_command(self):
        self.restorePriorities()
        super(ExtremePriorityCommand, self).undo_command()
        
    def redo_command(self):
        super(ExtremePriorityCommand, self).redo_command()
        self.setNewExtremePriority()


class MaxPriorityCommand(ExtremePriorityCommand):
    plural_name = _('Maximize priority')
    singular_name = _('Maximize priority of "%s"')
    
    delta = +1
    
    def getOldExtremePriority(self):
        return self.list.maxPriority()
    

class MinPriorityCommand(ExtremePriorityCommand):
    plural_name = _('Minimize priority')
    singular_name = _('Minimize priority of "%s"')
    
    delta = -1
                    
    def getOldExtremePriority(self):
        return self.list.minPriority()
    

class ChangePriorityCommand(base.BaseCommand): # pylint: disable-msg=W0223
    delta = 'Subclass responsibility'
    
    @patterns.eventSource
    def changePriorities(self, delta, event=None):
        for item in self.items:
            item.setPriority(item.priority() + delta, event=event)

    def do_command(self):
        super(ChangePriorityCommand, self).do_command()
        self.changePriorities(self.delta)

    def undo_command(self):
        self.changePriorities(-self.delta)
        super(ChangePriorityCommand, self).undo_command()

    def redo_command(self):
        super(ChangePriorityCommand, self).redo_command()
        self.changePriorities(self.delta)


class IncPriorityCommand(ChangePriorityCommand):
    plural_name = _('Increase priority')
    singular_name = _('Increase priority of "%s"')
    
    delta = +1


class DecPriorityCommand(ChangePriorityCommand):
    plural_name = _('Decrease priority')
    singular_name = _('Decrease priority of "%s"')

    delta = -1
    

class EditPriorityCommand(base.BaseCommand):
    def __init__(self, *args, **kwargs):
        self.__newPriority = kwargs.pop('priority')
        super(EditPriorityCommand, self).__init__(*args, **kwargs)
        self.__oldPriorities = [item.priority() for item in self.items]

    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setPriority(self.__newPriority, event=event)

    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldPriority in zip(self.items, self.__oldPriorities):
            item.setPriority(oldPriority, event=event)

    def redo_command(self):
        self.do_command()
    
    
class AddTaskNoteCommand(base.AddNoteCommand):
    plural_name = _('Add note to tasks')
