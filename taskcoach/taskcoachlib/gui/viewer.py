import patterns, command, widgets, uicommand, menu, color, render
import wx
from i18n import _
import wx.grid as grid
import domain.task as task
import domain.category as category
import domain.effort as effort
import domain.date as date


class Viewer(wx.Panel):
    ''' A Viewer shows the contents of a model (a list of tasks or a list of 
        efforts) by means of a widget (e.g. a ListCtrl or a TreeListCtrl).'''
        
    def __init__(self, parent, list, uiCommands, settings=None, *args, **kwargs):
        # FIXME: Are settings still optional?
        super(Viewer, self).__init__(parent, -1) # FIXME: Pass *args, **kwargs
        self.parent = parent # FIXME: Make instance variables private
        self.settings = settings
        self.uiCommands = uiCommands
        self.list = self.createSorter(self.createFilter(list))
        self.widget = self.createWidget()
        self.initLayout()
        patterns.Publisher().registerObserver(self.onAddItem, 
            eventType=self.list.addItemEventType())
        patterns.Publisher().registerObserver(self.onRemoveItem, 
            eventType=self.list.removeItemEventType())
        patterns.Publisher().registerObserver(self.onSorted, 
            eventType=self.list.sortEventType())
        
    def selectEventType(self):
        return '%s (%s).select'%(self.__class__, id(self))

    def initLayout(self):
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self.widget, 1, wx.EXPAND)
        self.SetSizerAndFit(self._sizer)
    
    def __getattr__(self, attr):
        return getattr(self.widget, attr)
        
    def createWidget(self, *args):
        raise NotImplementedError
    
    def getWidget(self):
        return self.widget
 
    def createSorter(self, collection):
        return collection
        
    def createFilter(self, collection):
        return collection

    def onAddItem(self, event):
        self.refresh()

    def onRemoveItem(self, event):
        self.refresh()

    def onSorted(self, event):
        self.refresh()

    def onSelect(self, *args):
        patterns.Publisher().notifyObservers(patterns.Event(self, 
            self.selectEventType(), self.curselection()))
    
    def refresh(self):
        self.widget.refresh(len(self.list))
        
    def curselection(self):
        return [self.list[index] for index in self.widget.curselection()]
        
    def size(self):
        return self.widget.GetItemCount()
    
    def model(self):
        return self.list
    
    def widgetCreationKeywordArguments(self):
        return {}
    
    """
    def onActivateViewer(self):
        ''' Called by ViewerContainer when a viewer becomes active, i.e. the
            foremost tab. '''
        print '%s.onActivateViewer'%self.__class__
        self.refresh()
        patterns.Publisher().registerObserver(self.onAddItem, 
            eventType=self.list.addItemEventType())
        patterns.Publisher().registerObserver(self.onRemoveItem, 
            eventType=self.list.removeItemEventType())
        patterns.Publisher().registerObserver(self.onSorted, 
            eventType=self.list.sortEventType())
        
    def onDeactivateViewer(self):
        ''' Called by ViewerContainer when a viewer is no longer the active
            viewer, i.e. no longer the foremost tab. '''
        print '%s.onDeactivateViewer'%self.__class__
        patterns.Publisher().removeObserver(self.onAddItem, 
            eventType=self.list.addItemEventType())
        patterns.Publisher().removeObserver(self.onRemoveItem, 
            eventType=self.list.removeItemEventType())
        patterns.Publisher().removeObserver(self.onSorted, 
            eventType=self.list.sortEventType())
    """     
        
class ListViewer(Viewer):
    def getItemImage(self, index):
        item = self.list[index]
        normalImageIndex, expandedImageIndex = self.getImageIndices(item) 
        if item.children():
            return expandedImageIndex
        else:
            return normalImageIndex

    def isTreeViewer(self):
        return False
        

class TreeViewer(Viewer):
    def expandAll(self):
        self.widget.expandAllItems()

    def collapseAll(self):
        self.widget.collapseAllItems()
        
    def expandSelected(self):
        self.widget.expandSelectedItems()
        
    def collapseSelected(self):
        self.widget.collapseSelectedItems()
        
    def isSelectionExpandable(self):
        return self.widget.isSelectionExpandable()
    
    def isSelectionCollapsable(self):
        return self.widget.isSelectionCollapsable()
        
    def draggedItems(self):
        return [self.list[index] for index in self.widget.draggedItems()]

    def isTreeViewer(self):
        return True
        

class UpdatePerSecondViewer(Viewer, date.ClockObserver):
    def __init__(self, *args, **kwargs):
        self.__trackedItems = set()
        super(UpdatePerSecondViewer, self).__init__(*args, **kwargs)
        patterns.Publisher().registerObserver(self.onStartTracking,
            eventType=self.trackStartEventType())
        patterns.Publisher().registerObserver(self.onStopTracking,
            eventType=self.trackStopEventType())
                
    def trackStartEventType(self):
        raise NotImplementedError
    
    def trackStopEventType(self):
        raise NotImplementedError

    def onAddItem(self, event):
        super(UpdatePerSecondViewer, self).onAddItem(event)
        self.addTrackedItems(self.trackedItems(event.values()))

    def onRemoveItem(self, event):
        super(UpdatePerSecondViewer, self).onRemoveItem(event)
        self.removeTrackedItems(self.trackedItems(event.values()))

    def onStartTracking(self, event):
        item = event.source()
        if item in self.list:
            self.addTrackedItems([item])

    def onStopTracking(self, event):
        item = event.source()
        if item in self.list:
            self.removeTrackedItems([item])

    def onEverySecond(self, event):
        trackedItemsToRemove = []
        for item in self.__trackedItems:
            # Prepare for a ValueError, because we might receive a clock
            # notification before we receive a 'remove item' notification for
            # an item that has been removed from the observed collection.
            try:
                self.widget.refreshItem(self.list.index(item))
            except ValueError:
                trackedItemsToRemove.append(item)
        self.removeTrackedItems(trackedItemsToRemove)
            
    def addTrackedItems(self, items):
        if items:
            self.__trackedItems.update(items)
            self.startClockIfNecessary()

    def removeTrackedItems(self, items):
        if items:
            self.__trackedItems.difference_update(items)
            self.stopClockIfNecessary()

    def startClockIfNecessary(self):
        if self.__trackedItems and not self.isClockStarted():
            self.startClock()

    def stopClockIfNecessary(self):
        if not self.__trackedItems and self.isClockStarted():
            self.stopClock()

    @staticmethod
    def trackedItems(items):
        return [item for item in items if item.isBeingTracked(recursive=True)]

        
class ViewerWithColumns(Viewer):
    def __init__(self, *args, **kwargs):
        super(ViewerWithColumns, self).__init__(*args, **kwargs)
        self.initColumns()

    def initColumns(self):
        for column in self.columns():
            self.initColumn(column)

    def initColumn(self, column):
        visibilitySetting = column.visibilitySetting()
        if visibilitySetting:
            patterns.Publisher().registerObserver(self.onShowColumn, 
                eventType='%s.%s'%visibilitySetting)
            show = self.settings.getboolean(*column.visibilitySetting())
            self.widget.showColumn(column, show=show)
        else:
            show = True
        if show:
            self.__startObserving(column.eventTypes())
    
    def onShowColumn(self, event):
        visibilitySetting = tuple(event.type().split('.'))
        for column in self.columns():
            if column.visibilitySetting() == visibilitySetting:
                show = event.value() == 'True'
                self.widget.showColumn(column, show)
                if show:
                    self.__startObserving(column.eventTypes())
                else:
                    self.__stopObserving(column.eventTypes())
                break
                
    def onAttributeChanged(self, event):
        item = event.source()
        if item in self.list:
            self.widget.refreshItem(self.list.index(item))
        
    def columns(self):
        return self._columns
    
    def isVisibleColumn(self, column):
        visibilitySetting = column.visibilitySetting()
        return visibilitySetting == None or \
            self.settings.getboolean(*visibilitySetting)
    
    def visibleColumns(self):
        return [column for column in self._columns if \
                self.isVisibleColumn(column)]
    
    def hideColumn(self, visibleColumnIndex):
        column = self.visibleColumns()[visibleColumnIndex]
        section, setting = column.visibilitySetting()
        self.settings.set(section, setting, 'False')
        self.__stopObserving(column.eventTypes())
            
    def isHideableColumn(self, visibleColumnIndex):
        column = self.visibleColumns()[visibleColumnIndex]
        return column.visibilitySetting() != None
        
    def getItemText(self, index, column):
        item = self.list[index]
        return column.render(item)

    def __startObserving(self, eventTypes):
        for eventType in eventTypes:
            patterns.Publisher().registerObserver(self.onAttributeChanged, 
                eventType=eventType)                    
        
    def __stopObserving(self, eventTypes):
        for eventType in eventTypes:
            patterns.Publisher().removeObserver(self.onAttributeChanged, 
                eventType=eventType)                                        


class TaskViewer(UpdatePerSecondViewer):
    def __init__(self, *args, **kwargs):
        super(TaskViewer, self).__init__(*args, **kwargs)
        self.__registerForColorChanges()
    
    def isShowingTasks(self): 
        return True

    def isShowingEffort(self): 
        return False
    
    def trackStartEventType(self):
        return 'task.track.start'
    
    def trackStopEventType(self):
        return 'task.track.stop'
   
    def statusMessages(self):
        status1 = _('Tasks: %d selected, %d visible, %d total')%\
            (len(self.curselection()), len(self.list), 
             self.list.originalLength())         
        status2 = _('Status: %d over due, %d inactive, %d completed')% \
            (self.list.nrOverdue(), self.list.nrInactive(),
             self.list.nrCompleted())
        return status1, status2
 
    def createTaskPopupMenu(self):
        return menu.TaskPopupMenu(self.parent, self.uiCommands, 
            self.isTreeViewer())

    def getItemAttr(self, index):
        task = self.list[index]
        return wx.ListItemAttr(color.taskColor(task, self.settings))

    def __registerForColorChanges(self):
        colorSettings = ['color.%s'%setting for setting in 'activetasks',\
            'inactivetasks', 'completedtasks', 'duetodaytasks', 'overduetasks']
        for colorSetting in colorSettings:
            patterns.Publisher().registerObserver(self.onColorChange, 
                eventType=colorSetting)
        
    def onColorChange(self, *args, **kwargs):
        self.refresh()

    def createImageList(self):
        imageList = wx.ImageList(16, 16)
        self.imageIndex = {}
        for index, image in enumerate(['task', 'task_inactive', 
            'task_completed', 'task_duetoday', 'task_overdue', 'tasks', 
            'tasks_open', 'tasks_inactive', 'tasks_inactive_open', 
            'tasks_completed', 'tasks_completed_open', 'tasks_duetoday', 
            'tasks_duetoday_open', 'tasks_overdue', 'tasks_overdue_open', 
            'start', 'ascending', 'descending']):
            imageList.Add(wx.ArtProvider_GetBitmap(image, wx.ART_MENU, (16,16)))
            self.imageIndex[image] = index
        return imageList

    def getImageIndices(self, task):
        bitmap = 'task'
        if task.children():
            bitmap += 's'
        if task.completed():
            bitmap += '_completed'
        elif task.overdue():
            bitmap += '_overdue'
        elif task.dueToday():
            bitmap += '_duetoday'
        elif task.inactive():
            bitmap += '_inactive'
        if task.children():
            bitmap_selected = bitmap + '_open'
        else:
            bitmap_selected = bitmap
        if task.isBeingTracked():
            bitmap = bitmap_selected = 'start'
        return self.imageIndex[bitmap], self.imageIndex[bitmap_selected]
        
    def onDropFiles(self, index, filenames):
        ''' This method is called by the widget when one or more files
            are dropped on a task. '''
        addAttachment = command.AddAttachmentToTaskCommand(self.list,
            [self.list[index]], attachments=filenames)
        addAttachment.do()

    def widgetCreationKeywordArguments(self):
        kwargs = super(TaskViewer, self).widgetCreationKeywordArguments()
        kwargs['onDropFiles'] = self.onDropFiles
        return kwargs
               
            
class TaskViewerWithColumns(TaskViewer, ViewerWithColumns):
    def __init__(self, *args, **kwargs):
        super(TaskViewerWithColumns, self).__init__(*args, **kwargs)
        patterns.Publisher().registerObserver(self.onSortKeyChanged, 
            eventType='view.sortby')
        patterns.Publisher().registerObserver(self.onSortOrderChanged, 
            eventType='view.sortascending')
            
    def _createColumns(self):
        return [widgets.Column(_('Subject'), 'task.subject', 'task.completionDate',
                'task.dueDate', 'task.startDate',
                'task.track.start', 'task.track.stop', sortKey='subject', 
                sortCallback=self.uiCommands['viewsortbysubject'], 
                renderCallback=self.renderSubject)] + \
            [widgets.Column(columnHeader, eventType,
             visibilitySetting=('view', setting.lower()), sortKey=setting, 
             sortCallback=self.uiCommands['viewsortby' + setting.lower()],
             renderCallback=renderCallback, alignment=wx.LIST_FORMAT_RIGHT) \
             for columnHeader, eventType, setting, renderCallback in \
            (_('Start date'), 'task.startDate', 'startDate', lambda task: render.date(task.startDate())),
            (_('Due date'), 'task.dueDate', 'dueDate', lambda task: render.date(task.dueDate())),
            (_('Days left'), 'task.timeLeft', 'timeLeft', lambda task: render.daysLeft(task.timeLeft())),
            (_('Completion date'), 'task.completionDate', 'completionDate', lambda task: render.date(task.completionDate())),
            (_('Budget'), 'task.budget', 'budget', lambda task: render.budget(task.budget())),
            (_('Total budget'), 'task.totalBudget', 'totalbudget', lambda task: render.budget(task.budget(recursive=True))),
            (_('Time spent'), 'task.timeSpent', 'timeSpent', lambda task: render.timeSpent(task.timeSpent())),
            (_('Total time spent'), 'task.totalTimeSpent', 'totaltimeSpent', lambda task: render.timeSpent(task.timeSpent(recursive=True))),
            (_('Budget left'), 'task.budgetLeft', 'budgetLeft', lambda task: render.budget(task.budgetLeft())),
            (_('Total budget left'), 'task.totalBudgetLeft', 'totalbudgetLeft', lambda task: render.budget(task.budgetLeft(recursive=True))),
            (_('Priority'), 'task.priority', 'priority', lambda task: render.priority(task.priority())),
            (_('Overall priority'), 'task.totalPriority', 'totalpriority', lambda task: render.priority(task.priority(recursive=True))),
            (_('Hourly fee'), 'task.hourlyFee', 'hourlyFee', lambda task: render.amount(task.hourlyFee())),
            (_('Fixed fee'), 'task.fixedFee', 'fixedFee', lambda task: render.amount(task.fixedFee())),
            (_('Total fixed fee'), 'task.totalFixedFee', 'totalfixedfee', lambda task: render.amount(task.fixedFee(recursive=True))),
            (_('Revenue'), 'task.revenue', 'revenue', lambda task: render.amount(task.revenue())),
            (_('Total revenue'), 'task.totalRevenue', 'totalrevenue', lambda task: render.amount(task.revenue(recursive=True))),
            (_('Last modification time'), 'task.lastModificationTime', 'lastModificationTime', lambda task: render.dateTime(task.lastModificationTime())),
            (_('Overall last modification time'),
            'task.totalLastModificationTime', 'totallastModificationTime', lambda task: render.dateTime(task.lastModificationTime(recursive=True)))]

    def initColumn(self, column):
        super(TaskViewerWithColumns, self).initColumn(column)
        if self.settings.get('view', 'sortby') == column.sortKey():
            self.widget.showSortColumn(column)
            self.showSortOrder(self.settings.getboolean('view',
                'sortascending'))
        
    def onSortKeyChanged(self, event):
        sortKey = event.value()
        for column in self.columns():
            if column.sortKey() == sortKey:
                self.widget.showSortColumn(column)
                break
        
    def onSortOrderChanged(self, event):
        self.showSortOrder(event.value() == 'True')

    def showSortOrder(self, ascending):
        if ascending:
            sortOrder = 'ascending'
        else:
            sortOrder = 'descending'
        self.widget.showSortOrder(self.imageIndex[sortOrder])
    
    def getItemText(self, index, column=None):
        task = self.list[index]
        if not column:
            column = self.columns()[0]
        return column.render(task)
                
    def createColumnPopupMenu(self):
        return menu.TaskViewerColumnPopupMenu(self.parent, self.uiCommands)
    

class TaskListViewer(TaskViewerWithColumns, ListViewer):
    def createWidget(self):
        self._columns = self._createColumns()
        widget = widgets.ListCtrl(self, self.columns(),
            self.getItemText, self.getItemImage, self.getItemAttr, 
            self.onSelect, self.uiCommands['edit'], 
            self.createTaskPopupMenu(),
            self.createColumnPopupMenu(),
            **self.widgetCreationKeywordArguments())
        widget.AssignImageList(self.createImageList(), wx.IMAGE_LIST_SMALL)
        return widget
        
    def createFilter(self, taskList):
        return task.filter.CategoryFilter(task.filter.CompositeFilter( \
            task.filter.ViewFilter(task.filter.SearchFilter(taskList, 
            settings=self.settings), settings=self.settings), 
            settings=self.settings), settings=self.settings)
        
    def createSorter(self, taskList):
        return task.sorter.Sorter(taskList, settings=self.settings, 
            treeMode=False)
    
    def setViewCompositeTasks(self, viewCompositeTasks):
        self.list.setViewCompositeTasks(viewCompositeTasks)

    def renderSubject(self, task):
        return render.subject(task, recursively=True)


class TaskTreeViewer(TaskViewer, TreeViewer):
    def createWidget(self):
        widget = widgets.TreeCtrl(self, self.getItemText, self.getItemImage, 
            self.getItemAttr, self.getItemId, self.getRootIndices, 
            self.getChildIndices, self.onSelect, self.uiCommands['edit'], 
            self.uiCommands['draganddroptask'], self.createTaskPopupMenu(),
            **self.widgetCreationKeywordArguments())
        widget.AssignImageList(self.createImageList())
        return widget
    
    def createFilter(self, taskList):
        # FIXME: pull up
        return task.filter.CategoryFilter(task.filter.ViewFilter(task.filter.SearchFilter(taskList, 
            settings=self.settings, treeMode=True), settings=self.settings, 
            treeMode=True), settings=self.settings, treeMode=True)
        
    def createSorter(self, taskList):
        # FIMXE: pull up
        return task.sorter.Sorter(taskList, settings=self.settings, 
            treeMode=True)
    
    def getItemText(self, index):
        task = self.list[index]
        return task.subject()
    
    def getItemImage(self, index):
        task = self.list[index]
        return self.getImageIndices(task) 
        
    def getItemChildIndex(self, index):
        task = self.list[index]
        if task.parent():
            parentIndex = self.list.index(task.parent())
            childrenBeforeThisTask = [child for child in \
                self.list[parentIndex+1:index] \
                if task.parent() == child.parent()]
            return len(childrenBeforeThisTask)
        else:
            return len([child for child in self.list[:index] \
                        if child.parent() is None])
                   
    def getItemId(self, index):
        task = self.list[index]
        return task.id()

    def getRootIndices(self):
        return [self.list.index(task) for task in self.list.rootItems()]
        
    def getChildIndices(self, index):
        task = self.list[index]
        childIndices = [self.list.index(child) for child in task.children() \
                        if child in self.list]
        childIndices.sort()
        return childIndices

    def renderSubject(self, task):
        return render.subject(task, recursively=False)


class TaskTreeListViewer(TaskViewerWithColumns, TaskTreeViewer):
    def createWidget(self):
        self._columns = self._createColumns()
        widget = widgets.TreeListCtrl(self, self.columns(), self.getItemText,
            self.getItemImage, self.getItemAttr, self.getItemId, 
            self.getRootIndices, self.getChildIndices, self.onSelect, 
            self.uiCommands['edit'], self.uiCommands['draganddroptask'],
            self.createTaskPopupMenu(), self.createColumnPopupMenu(),
            **self.widgetCreationKeywordArguments())
        widget.AssignImageList(self.createImageList())
        return widget    


class CategoryViewer(TreeViewer):
    def createWidget(self):
        widget = widgets.TreeCtrl(self, self.getItemText, self.getItemImage,
            self.getItemAttr, self.getItemId, self.getRootIndices, 
            self.getChildIndices, self.onSelect, None, None)
        return widget

    def getItemText(self, index):    # FIXME: pull up to TreeViewer
        category = self.list[index]
        return category.subject()
    
    def getItemImage(self, index):
        return -1, -1
    
    def getItemAttr(self, index):
        return wx.ListItemAttr()
    
    def getItemId(self, index):
        category = self.list[index]
        return id(category)
    
    def getRootIndices(self):
        return [self.list.index(category) for category in self.list.rootItems()]
    
    def getChildIndices(self, index):    # FIXME: pull up to TreeViewer
        category = self.list[index]
        childIndices = [self.list.index(child) for child in category.children() \
                        if child in self.list]
        childIndices.sort()
        return childIndices
    
    def createSorter(self, categoryContainer):
        return category.CategorySorter(categoryContainer)
    
    def isShowingTasks(self):
        return False
    

class EffortViewer(UpdatePerSecondViewer):
    def isShowingTasks(self):
        return False
        
    def isShowingEffort(self):
        return True

    def trackStartEventType(self):
        return 'effort.track.start'
    
    def trackStopEventType(self):
        return 'effort.track.stop'

    def createSorter(self, effortList):
        return effort.EffortSorter(effortList)
    
    def statusMessages(self):
        status1 = _('Effort: %d selected, %d visible, %d total')%\
            (len(self.curselection()), len(self.list), 
             self.list.originalLength())         
        status2 = _('Status: %d tracking')% self.list.nrBeingTracked()
        return status1, status2
 
    
class EffortListViewer(ListViewer, EffortViewer, ViewerWithColumns):
    def __init__(self, parent, list, *args, **kwargs):
        self.taskList = list
        super(EffortListViewer, self).__init__(parent, list, *args, **kwargs)
        
    def createWidget(self):
        # We need to create new uiCommands here, because the viewer might not
        # be the effort viewer in the mainwindow, but the effort viewer in the 
        # task edit window.
        uiCommands = {}
        uiCommands.update(self.uiCommands)
        uiCommands['editeffort'] = uicommand.EffortEdit(mainwindow=self.parent, 
            effortList=self.list, taskList=self.taskList, viewer=self, 
            uiCommands=self.uiCommands)
        uiCommands['deleteeffort'] = uicommand.EffortDelete( \
            effortList=self.list, viewer=self, taskList=self.taskList)
        uiCommands['cut'] = uicommand.EditCut(viewer=self)
        uiCommands['copy'] = uicommand.EditCopy(viewer=self)
        uiCommands['pasteintotask'] = uicommand.EditPasteIntoTask(viewer=self)
        uiCommands['hidecurrentcolumn'] = \
            uicommand.HideCurrentColumn(viewer=self)
        
        self._columns = self._createColumns()
        widget = widgets.ListCtrl(self, self.columns(),
            self.getItemText, self.getItemImage, self.getItemAttr,
            self.onSelect, uiCommands['editeffort'], 
            menu.EffortPopupMenu(self.parent, uiCommands), 
            menu.EffortViewerColumnPopupMenu(self.parent, uiCommands), 
            resizeableColumn=2, **self.widgetCreationKeywordArguments())
        widget.SetColumnWidth(0, 150)
        return widget
    
    def _createColumns(self):
        return [widgets.Column(columnHeader, eventType, 
                renderCallback=renderCallback) \
            for columnHeader, eventType, renderCallback in \
            (_('Period'), 'effort.duration', self.renderPeriod),
            (_('Task'), 'effort.task', lambda effort: render.subject(effort.task(), recursively=True))] + \
            [widgets.Column(columnHeader, eventType, 
             visibilitySetting=('view', setting), 
             renderCallback=renderCallback, alignment=wx.LIST_FORMAT_RIGHT) \
            for columnHeader, eventType, setting, renderCallback in \
            (_('Time spent'), 'effort.duration', 'efforttimespent', 
                lambda effort: render.timeSpent(effort.duration())),
            (_('Revenue'), 'effort.duration', 'effortrevenue', 
                lambda effort: render.amount(effort.revenue()))]

    def createFilter(self, taskList):
        return effort.EffortList(taskList)
            
    def getItemImage(self, index):
        return -1
    
    def getItemAttr(self, index):
        return wx.ListItemAttr()
                
    def renderPeriod(self, effort):
        index = self.list.index(effort)
        previousEffort = index > 0 and self.list[index-1] or None
        if previousEffort and effort.getStart() == previousEffort.getStart():
            return self.renderRepeatedPeriod(effort)
        else:
            return self.renderEntirePeriod(effort)

    def renderRepeatedPeriod(self, effort):
        return ''
        
    def renderEntirePeriod(self, effort):
        return render.dateTimePeriod(effort.getStart(), effort.getStop())
        

class CompositeEffortListViewer(EffortListViewer):
    def _createColumns(self):
        return super(CompositeEffortListViewer, self)._createColumns() + \
            [widgets.Column(columnHeader, eventType, 
             visibilitySetting=('view', setting), 
              renderCallback=renderCallback, alignment=wx.LIST_FORMAT_RIGHT) \
             for columnHeader, eventType, setting, renderCallback in \
                (_('Total time spent'), 'effort.totalDuration', 'totalefforttimespent', 
                 lambda effort: render.timeSpent(effort.duration(recursive=True))),
                (_('Total revenue'), 'effort.totalDuration', 'totaleffortrevenue', 
                 lambda effort: render.amount(effort.revenue(recursive=True)))]
        
    def curselection(self):
        compositeEfforts = super(CompositeEffortListViewer, self).curselection()
        return [effort for compositeEffort in compositeEfforts for effort in compositeEffort]

    def createFilter(self, taskList):
        return self.EffortPerPeriod(taskList)


class EffortPerDayViewer(CompositeEffortListViewer):
    EffortPerPeriod = effort.EffortPerDay
    
    def renderEntirePeriod(self, compositeEffort):
        return render.date(compositeEffort.getStart().date())

        
class EffortPerWeekViewer(CompositeEffortListViewer):
    EffortPerPeriod = effort.EffortPerWeek
        
    def renderEntirePeriod(self, compositeEffort):
        return render.weekNumber(compositeEffort.getStart())


class EffortPerMonthViewer(CompositeEffortListViewer):
    EffortPerPeriod = effort.EffortPerMonth
    
    def renderEntirePeriod(self, compositeEffort):
        return render.month(compositeEffort.getStart())

