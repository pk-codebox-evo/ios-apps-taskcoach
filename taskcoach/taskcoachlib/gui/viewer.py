import patterns, command, widgets, uicommand, menu, color, render, dialog, mailer
import wx
from i18n import _
from domain import base, task, category, effort, date, note, attachment


class SearchableViewer(object):
    ''' A viewer that is searchable. This is a mixin class. '''

    def isSearchable(self):
        return True
    
    def createFilter(self, model):
        model = super(SearchableViewer, self).createFilter(model)
        return base.SearchFilter(model, **self.searchOptions())

    def searchOptions(self):
        searchString, matchCase, includeSubItems = self.getSearchFilter()
        return dict(searchString=searchString, matchCase=matchCase, 
                    includeSubItems=includeSubItems, 
                    treeMode=self.isTreeViewer())
    
    def setSearchFilter(self, searchString, matchCase=False, 
                        includeSubItems=False):
        section = self.settingsSection()
        self.settings.set(section, 'searchfilterstring', searchString)
        self.settings.set(section, 'searchfiltermatchcase', str(matchCase))
        self.settings.set(section, 'searchfilterincludesubitems', str(includeSubItems))
        self.model().setSearchFilter(searchString, matchCase, includeSubItems)
        
    def getSearchFilter(self):
        section = self.settingsSection()
        searchString = self.settings.get(section, 'searchfilterstring')
        matchCase = self.settings.getboolean(section, 'searchfiltermatchcase')
        includeSubItems = self.settings.getboolean(section, 'searchfilterincludesubitems')
        return searchString, matchCase, includeSubItems
    

class FilterableViewer(object):
    ''' A viewer that is filterable. This is a mixin class. '''

    def isFilterable(self):
        return True
    
    '''
    def createFilter(self, model):
        model = super(FilterableViewer, self).createFilter(model)
        return self.FilterClass(model, **self.filterOptions())
    '''    
        
class FilterableViewerForTasks(FilterableViewer):
    def createFilter(self, taskList):
        taskList = super(FilterableViewerForTasks, self).createFilter(taskList)
        return task.filter.CategoryFilter( \
            task.filter.ViewFilter(taskList, treeMode=self.isTreeViewer(), 
                                   **self.viewFilterOptions()), 
            categories=self.categories, treeMode=self.isTreeViewer())
    
    def viewFilterOptions(self):
        options = dict(dueDateFilter=self.getFilteredByDueDate(),
                       hideActiveTasks=self.isHidingActiveTasks(),
                       hideCompletedTasks=self.isHidingCompletedTasks(),
                       hideInactiveTasks=self.isHidingInactiveTasks(),
                       hideOverdueTasks=self.isHidingOverdueTasks(),
                       hideOverBudgetTasks=self.isHidingOverbudgetTasks())
        if not self.isTreeViewer():
            options['hideCompositeTasks'] = self.isHidingCompositeTasks()
        return options
    
    def isFilteredByDueDate(self, dueDateString):
        return dueDateString == self.settings.get(self.settingsSection(), 
                                                  'tasksdue')
    
    def setFilteredByDueDate(self, dueDateString):
        self.settings.set(self.settingsSection(), 'tasksdue', dueDateString)
        self.model().setFilteredByDueDate(dueDateString)
        
    def getFilteredByDueDate(self):
        return self.settings.get(self.settingsSection(), 'tasksdue')
    
    def hideActiveTasks(self, hide=True):
        self.__setBooleanSetting('hideactivetasks', hide)
        self.model().hideActiveTasks(hide)
        
    def isHidingActiveTasks(self):
        return self.__getBooleanSetting('hideactivetasks')

    def hideInactiveTasks(self, hide=True):
        self.__setBooleanSetting('hideinactivetasks', hide)
        self.model().hideInactiveTasks(hide)
        
    def isHidingInactiveTasks(self):
        return self.__getBooleanSetting('hideinactivetasks')
    
    def hideCompletedTasks(self, hide=True):
        self.__setBooleanSetting('hidecompletedtasks', hide)
        self.model().hideCompletedTasks(hide)
        
    def isHidingCompletedTasks(self):
        return self.__getBooleanSetting('hidecompletedtasks')
    
    def hideOverdueTasks(self, hide=True):
        self.__setBooleanSetting('hideoverduetasks', hide)
        self.model().hideOverdueTasks(hide)
        
    def isHidingOverdueTasks(self):
        return self.__getBooleanSetting('hideoverduetasks')
    
    def hideOverbudgetTasks(self, hide=True):
        self.__setBooleanSetting('hideoverbudgettasks', hide)
        self.model().hideOverbudgetTasks(hide)
    
    def isHidingOverbudgetTasks(self):
        return self.__getBooleanSetting('hideoverbudgettasks')
    
    def hideCompositeTasks(self, hide=True):
        self.__setBooleanSetting('hidecompositetasks', hide)
        self.model().hideCompositeTasks(hide)
        
    def isHidingCompositeTasks(self):
        return self.__getBooleanSetting('hidecompositetasks')
    
    def resetFilter(self):
        self.hideActiveTasks(False)
        self.hideInactiveTasks(False)
        self.hideCompletedTasks(False)
        self.hideOverdueTasks(False)
        self.hideOverbudgetTasks(False)
        self.hideCompositeTasks(False)
        self.setFilteredByDueDate('Unlimited')
        
    def getFilterUICommands(self):
        return ['resetfilter', None, 
                (_('Show only tasks &due before end of'), 'viewdueunlimited', 
                 'viewduetoday', 'viewduetomorrow', 'viewdueworkweek', 
                 'viewdueweek', 'viewduemonth', 'viewdueyear'),
                (_('&Hide tasks that are'), 'hideactivetasks', 'hideinactivetasks',
                 'hidecompletedtasks', None, 'hideoverduetasks', 
                 'hideoverbudgettasks')]

    def __getBooleanSetting(self, setting):
        return self.settings.getboolean(self.settingsSection(), setting)
    
    def __setBooleanSetting(self, setting, booleanValue):
        self.settings.setboolean(self.settingsSection(), setting, booleanValue)
        
                
class SortableViewer(object):
    ''' A viewer that is sortable. This is a mixin class. '''

    def isSortable(self):
        return True

    def createSorter(self, model):
        return self.SorterClass(model, **self.sorterOptions())
    
    def sorterOptions(self):
        return dict(sortBy=self.sortKey(),
                    sortAscending=self.isSortOrderAscending(),
                    sortCaseSensitive=self.isSortCaseSensitive())
        
    def sortBy(self, sortKey):
        if self.isSortedBy(sortKey):
            self.setSortOrderAscending(not self.isSortOrderAscending())
        else:
            self.settings.set(self.settingsSection(), 'sortby', sortKey)
            self.model().sortBy(sortKey)
        
    def isSortedBy(self, sortKey):
        return sortKey == self.sortKey()

    def sortKey(self):
        return self.settings.get(self.settingsSection(), 'sortby')
    
    def isSortOrderAscending(self):
        return self.settings.getboolean(self.settingsSection(), 
            'sortascending')
    
    def setSortOrderAscending(self, ascending=True):
        self.settings.set(self.settingsSection(), 'sortascending', 
            str(ascending))
        self.model().sortAscending(ascending)
        
    def isSortCaseSensitive(self):
        return self.settings.getboolean(self.settingsSection(), 
            'sortcasesensitive')
        
    def setSortCaseSensitive(self, caseSensitive=True):
        self.settings.set(self.settingsSection(), 'sortcasesensitive', 
            str(caseSensitive))
        self.model().sortCaseSensitive(caseSensitive)

        
class SortableViewerForTasks(SortableViewer):
    SorterClass = task.sorter.Sorter
    
    def isSortByTaskStatusFirst(self):
        return self.settings.getboolean(self.settingsSection(),
            'sortbystatusfirst')
        
    def setSortByTaskStatusFirst(self, sortByTaskStatusFirst):
        self.settings.set(self.settingsSection(), 'sortbystatusfirst',
            str(sortByTaskStatusFirst))
        self.model().sortByTaskStatusFirst(sortByTaskStatusFirst)

    def sorterOptions(self):
        options = super(SortableViewerForTasks, self).sorterOptions()
        options.update(treeMode=self.isTreeViewer(), 
            sortByTaskStatusFirst=self.isSortByTaskStatusFirst())
        return options

    def getSortUICommands(self):
        return ['viewsortorder', 
            'viewsortcasesensitive', 'viewsortbystatusfirst', None, 
            'viewsortbysubject', 'viewsortbydescription',
            'viewsortbycategories', 'viewsortbystartdate',
            'viewsortbyduedate', 'viewsortbytimeleft', 
            'viewsortbycompletiondate', 'viewsortbybudget', 
            'viewsortbytotalbudget', 'viewsortbytimespent',
            'viewsortbytotaltimespent', 'viewsortbybudgetleft',
            'viewsortbytotalbudgetleft', 'viewsortbypriority',
            'viewsortbytotalpriority', 'viewsortbyhourlyfee',
            'viewsortbyfixedfee', 'viewsortbyreminder', 
            'viewsortbylastmodificationtime', 
            'viewsortbytotallastmodificationtime']


class SortableViewerForEffort(SortableViewer):
    def sorterOptions(self):
        return dict()
    

class SortableViewerForCategories(SortableViewer):
    def getSortUICommands(self):
        return ['viewsortorder', 'viewsortcasesensitive']


class SortableViewerForNotes(SortableViewer):
    def getSortUICommands(self):
        return ['viewsortorder', 'viewsortcasesensitive', None, 
                'viewsortbysubject', 'viewsortbydescription']
        
    
class Viewer(wx.Panel):
    __metaclass__ = patterns.NumberedInstances
    
    ''' A Viewer shows the contents of a model (a list of tasks or a list of 
        efforts) by means of a widget (e.g. a ListCtrl or a TreeListCtrl).'''
        
    def __init__(self, parent, list, uiCommands, settings, *args, **kwargs):
        super(Viewer, self).__init__(parent, -1) # FIXME: Pass *args, **kwargs
        self.parent = parent # FIXME: Make instance variables private
        self.settings = settings
        self.__settingsSection = kwargs.pop('settingsSection')
        self.__instanceNumber = kwargs.pop('instanceNumber')
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
        self.refresh()
        
    def detach(self):
        ''' Should be called by viewercontainer before closing the viewer '''
        patterns.Publisher().removeInstance(self)

    def selectEventType(self):
        return '%s (%s).select'%(self.__class__, id(self))
    
    def title(self):
        return self.settings.get(self.settingsSection(), 'title') or self.defaultTitle
    
    def setTitle(self, title):
        self.settings.set(self.settingsSection(), 'title', title)
        self.parent.SetPageText(self.parent.GetPageIndex(self), title)

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
        return [self.getItemWithIndex(index) for index in self.widget.curselection()]
        
    def size(self):
        return self.widget.GetItemCount()
    
    def model(self):
        return self.list
    
    def widgetCreationKeywordArguments(self):
        return {}

    def isShowingTasks(self): 
        return False

    def isShowingEffort(self): 
        return False
    
    def isShowingCategories(self):
        return False
    
    def isShowingNotes(self):
        return False
    
    def visibleColumns(self):
        return [widgets.Column('subject', _('Subject'))]
    
    def itemEditor(self, *args, **kwargs):
        raise NotImplementedError
    
    def getColor(self, item):
        return wx.BLACK
    
    def settingsSection(self):
        section = self.__settingsSection
        if self.__instanceNumber > 0:
            previousSectionNumber = self.__instanceNumber - 1
            while previousSectionNumber > 0:
                previousSection = section + str(previousSectionNumber)
                if self.settings.has_section(previousSection):
                    break
                previousSectionNumber -= 1
            else:
                previousSection = section
            section += str(self.__instanceNumber)
            if not self.settings.has_section(section):
                self.settings.add_section(section, copyFromSection=previousSection)
        return section
    
    def isSortable(self):
        return False

    def getSortUICommands(self):
        return []
    
    def isSearchable(self):
        return False
        
    def hasHideableColumns(self):
        return False
    
    def getColumnUICommands(self):
        return []

    def isFilterable(self):
        return False
    
    def getFilterUICommands(self):
        return []
        
        
class ListViewer(Viewer):
    def isTreeViewer(self):
        return False

    def visibleItems(self):
        ''' Iterate over the items in the model. '''
        for item in self.model():
            yield item
    
    def getItemWithIndex(self, index):
        return self.model()[index]
            
    def getIndexOfItem(self, item):
        return self.model().index(item)
    

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
        
    def isTreeViewer(self):
        return True
        
    def visibleItems(self):
        ''' Iterate over the items in the model. '''            
        def yieldAllChildren(parent):
            for item in self.model():
                if item.parent() and item.parent() == parent:
                    yield item
                    for child in yieldAllChildren(item):
                        yield child
        for item in self.model().rootItems():
            yield item
            for child in yieldAllChildren(item):
                yield child

    def getItemWithIndex(self, index):
        ''' Return the item in the model with the specified index. index
            is a tuple of indices that specifies the path to the item. E.g.,
            (0,2,1) is (read the tuple from right to left) the second child 
            of the third child of the first root item. '''
        # This is performance critical code
        model = self.model()
        children = model.rootItems()
        for i in index[:-1]:
            item = children[i]
            childIndices = [model.index(child) for child in item.children() \
                            if child in model]
            childIndices.sort()
            children = [model[childIndex] for childIndex in childIndices]
        return children[index[-1]]

    def getIndexOfItem(self, item):
        parent = item.parent()
        if parent:
            children = [child for child in self.model() if child.parent() == parent]
            return self.getIndexOfItem(parent) + (children.index(item),)
        else:
            return (self.model().rootItems().index(item),)
        
    def getChildrenCount(self, index):
        if index == ():
            return len(self.model().rootItems())
        else:
            item = self.getItemWithIndex(index)
            return len([child for child in item.children() if child in self.model()])
    
    
class UpdatePerSecondViewer(Viewer, date.ClockObserver):
    def __init__(self, *args, **kwargs):
        self.__trackedItems = set()
        super(UpdatePerSecondViewer, self).__init__(*args, **kwargs)
        patterns.Publisher().registerObserver(self.onStartTracking,
            eventType=self.trackStartEventType())
        patterns.Publisher().registerObserver(self.onStopTracking,
            eventType=self.trackStopEventType())
        self.addTrackedItems(self.trackedItems(self.list))
                        
    def trackStartEventType(self):
        raise NotImplementedError
    
    def trackStopEventType(self):
        raise NotImplementedError

    def onAddItem(self, event):
        self.addTrackedItems(self.trackedItems(event.values()))
        super(UpdatePerSecondViewer, self).onAddItem(event)

    def onRemoveItem(self, event):
        self.removeTrackedItems(self.trackedItems(event.values()))
        super(UpdatePerSecondViewer, self).onRemoveItem(event)

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
                self.widget.RefreshItem(self.getIndexOfItem(item))
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
        self.__initDone = False
        self.__visibleColumns = []
        super(ViewerWithColumns, self).__init__(*args, **kwargs)
        self.initColumns()
        self.__initDone = True
        self.refresh()
        
    def hasHideableColumns(self):
        return True
    
    def getColumnUICommands(self):
        raise NotImplementedError
    
    def refresh(self, *args, **kwargs):
        if self.__initDone:
            super(ViewerWithColumns, self).refresh(*args, **kwargs)
                    
    def initColumns(self):
        for column in self.columns():
            self.initColumn(column)

    def initColumn(self, column):
        if column.name() in self.settings.getlist(self.settingsSection(), 
                                                  'columnsalwaysvisible'):
            show = True
        else:
            show = column.name() in self.settings.getlist(self.settingsSection(), 'columns')
            self.widget.showColumn(column, show=show)
        if show:
            self.__visibleColumns.append(column)
            self.__startObserving(column.eventTypes())
    
    def showColumnByName(self, columnName, show=True):
        for column in self.hideableColumns():
            if columnName == column.name():
                self.showColumn(column, show)
                break

    def showColumn(self, column, show=True):
        if show:
            self.__visibleColumns.append(column)
            self.__startObserving(column.eventTypes())
        else:
            self.__visibleColumns.remove(column)
            self.__stopObserving(column.eventTypes())
        self.settings.set(self.settingsSection(), 'columns', 
            str([column.name() for column in self.__visibleColumns]))
        self.widget.showColumn(column, show)
        self.widget.RefreshItems()

    def hideColumn(self, visibleColumnIndex):
        column = self.visibleColumns()[visibleColumnIndex]
        self.showColumn(column, show=False)
                
    def onAttributeChanged(self, event):
        item = event.source()
        if item in self.list:
            self.widget.RefreshItem(self.getIndexOfItem(item))
        
    def columns(self):
        return self._columns
    
    def isVisibleColumnByName(self, columnName):
        return columnName in [column.name() for column in self.__visibleColumns]
        
    def isVisibleColumn(self, column):
        return column in self.__visibleColumns
    
    def visibleColumns(self):
        return self.__visibleColumns
        
    def hideableColumns(self):
        return [column for column in self._columns if column.name() not in \
                self.settings.getlist(self.settingsSection(), 'columnsalwaysvisible')]
                
    def isHideableColumn(self, visibleColumnIndex):
        column = self.visibleColumns()[visibleColumnIndex]
        return column.name() not in self.settings.getlist(self.settingsSection(), 
                                                          'columnsalwaysvisible')
        
    def getItemText(self, index, column=0):
        item = self.getItemWithIndex(index)
        column = self.visibleColumns()[column]
        return column.render(item)

    def getItemDescription(self, index, column=0):
        item = self.getItemWithIndex(index)
        column = self.visibleColumns()[column]
        return column.renderDescription(item)

    def getItemImage(self, index, which, column=0):
        item = self.getItemWithIndex(index)
        column = self.visibleColumns()[column]
        return column.imageIndex(item, which) 
            
    def __startObserving(self, eventTypes):
        for eventType in eventTypes:
            patterns.Publisher().registerObserver(self.onAttributeChanged, 
                eventType=eventType)                    
        
    def __stopObserving(self, eventTypes):
        for eventType in eventTypes:
            patterns.Publisher().removeObserver(self.onAttributeChanged, 
                eventType=eventType)


class SortableViewerWithColumns(SortableViewer, ViewerWithColumns):
    def initColumn(self, column):
        super(SortableViewerWithColumns, self).initColumn(column)
        if self.isSortedBy(column.name()):
            self.widget.showSortColumn(column)
            self._showSortOrder()

    def _showSortOrder(self):
        if self.isSortOrderAscending():
            sortOrder = 'ascending' 
        else: 
            sortOrder = 'descending'
        self.widget.showSortOrder(self.imageIndex[sortOrder])

    def setSortOrderAscending(self, *args, **kwargs):
        super(SortableViewerWithColumns, self).setSortOrderAscending(*args, **kwargs)
        self._showSortOrder()
        
    def sortBy(self, *args, **kwargs):
        super(SortableViewerWithColumns, self).sortBy(*args, **kwargs)
        for column in self.columns():
            if self.isSortedBy(column.name()):
                self.widget.showSortColumn(column)
                break
            

class TaskViewer(FilterableViewerForTasks, SortableViewerForTasks, 
                 SearchableViewer, UpdatePerSecondViewer):
    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories')
        super(TaskViewer, self).__init__(*args, **kwargs)
        self.__registerForColorChanges()
            
    def isShowingTasks(self): 
        return True
    
    def getColumnUICommands(self):
        return [(_('&Dates'), 'viewalldatecolumns', None, 'viewstartDate', 
                 'viewdueDate', 'viewcompletionDate', 'viewtimeLeft'),
                (_('&Budget'), 'viewallbudgetcolumns', None, 'viewbudget', 
                 'viewtotalBudget', 'viewtimeSpent', 'viewtotalTimeSpent', 
                 'viewbudgetLeft', 'viewtotalBudgetLeft'),
                (_('&Financial'), 'viewallfinancialcolumns', None, 
                 'viewhourlyFee', 'viewfixedFee', 'viewtotalFixedFee', 
                'viewrevenue', 'viewtotalRevenue'),
                'viewdescription', 'viewattachments', 'viewcategories', 
                'viewpriority', 'viewtotalPriority', 'viewreminder', 
                'viewlastModificationTime', 'viewtotalLastModificationTime']
 
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

    def getColor(self, task):
        return color.taskColor(task, self.settings)
    
    def getItemAttr(self, index):
        task = self.getItemWithIndex(index)
        return wx.ListItemAttr(self.getColor(task))

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
            'start', 'ascending', 'descending', 'attachment']):
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

    def onDropURL(self, index, url):
        attachments = [attachment.URIAttachment(url)]
        if index is None:
            newTaskDialog = self.newItemDialog(bitmap='new',
                                               attachments=attachments)
            newTaskDialog.Show()
        else:
            addAttachment = command.AddAttachmentToTaskCommand(self.list,
                [self.getItemWithIndex(index)], attachments=attachments)
            addAttachment.do()

    def onDropFiles(self, index, filenames):
        ''' This method is called by the widget when one or more files
            are dropped on a task. '''
        attachments = [attachment.FileAttachment(name) for name in filenames]
        if index is None:
            newTaskDialog = self.newItemDialog(bitmap='new',
                                               attachments=attachments)
            newTaskDialog.Show()
        else:
            addAttachment = command.AddAttachmentToTaskCommand(self.list,
                [self.getItemWithIndex(index)], attachments=attachments)
            addAttachment.do()

    def onDropMail(self, index, mail):
        attachments = [attachment.MailAttachment(mail)]
        if index is None:
            subject, content = mailer.readMail(mail)
            newTaskDialog = self.newItemDialog(bitmap='new',
                                               subject=subject,
                                               description=content,
                                               attachments=attachments)
            newTaskDialog.Show()
        else:
            addAttachment = command.AddAttachmentToTaskCommand(self.list,
                [self.getItemWithIndex(index)], attachments=attachments)
            addAttachment.do()

    def widgetCreationKeywordArguments(self):
        kwargs = super(TaskViewer, self).widgetCreationKeywordArguments()
        kwargs['onDropURL'] = self.onDropURL
        kwargs['onDropFiles'] = self.onDropFiles
        kwargs['onDropMail'] = self.onDropMail
        return kwargs
    
    # The methods below have two names. This is because there are two types
    # of domain object related UICommands. The generic variant works on
    # whatever type of domain object is shown in the current viewer. The
    # specific variant works on one specific type of domain object.
    # When a generic UICommand is invoked, e.g. uicommand.EditDomainObject, 
    # it will use 'itemEditor' to get a domain object editor for the current 
    # viewer. But when a specific UICommand is invoked, e.g. uicommand.EditTask, 
    # a TaskEditor needs to be returned, independently of which viewer is 
    # current. So, uicommand.NewTask will call taskEditor() to force a 
    # task editor. 
    
    def newItemDialog(self, *args, **kwargs):
        bitmap = kwargs.pop('bitmap')
        return dialog.editor.TaskEditor(wx.GetTopLevelParent(self), 
            command.NewTaskCommand(self.list, *args, **kwargs), self.list, self.uiCommands, 
            self.settings, self.categories, bitmap=bitmap)
    
    def editItemDialog(self, *args, **kwargs):
        return dialog.editor.TaskEditor(wx.GetTopLevelParent(self),
            command.EditTaskCommand(self.list, self.curselection()),
            self.list, self.uiCommands, self.settings, self.categories,
            bitmap=kwargs['bitmap'])
    
    editTaskDialog = editItemDialog
    
    def deleteItemCommand(self):
        return command.DeleteTaskCommand(self.list, self.curselection(),
            categories=self.categories)
        
    deleteTaskCommand = deleteItemCommand
    
    def newSubItemDialog(self, *args, **kwargs):
        return dialog.editor.TaskEditor(wx.GetTopLevelParent(self), 
            command.NewSubTaskCommand(self.list, self.curselection()), 
            self.list, self.uiCommands, self.settings, self.categories,
            bitmap=kwargs['bitmap'])
        
    newSubTaskDialog = newSubItemDialog
           
            
class TaskViewerWithColumns(TaskViewer, SortableViewerWithColumns):
    def _createColumns(self):
        return [widgets.Column('subject', _('Subject'), 'task.subject', 
                'task.completionDate', 'task.dueDate', 'task.startDate',
                'task.track.start', 'task.track.stop', 
                sortCallback=self.uiCommands['viewsortbysubject'], 
                imageIndexCallback=self.subjectImageIndex,
                renderCallback=self.renderSubject,
                renderDescriptionCallback=lambda task: task.description())] + \
            [widgets.Column('description', _('Description'), 'task.description', 
                sortCallback=self.uiCommands['viewsortbydescription'],
                renderCallback=lambda task: task.description(),
                renderDescriptionCallback=lambda task: task.description())] + \
            [widgets.Column('attachments', '', 'task.attachment.add', 
                'task.attachment.remove', width=28,
                alignment=wx.LIST_FORMAT_LEFT,
                imageIndexCallback=self.attachmentImageIndex,
                headerImageIndex=self.imageIndex['attachment'],
                renderCallback=lambda task: '',
                renderDescriptionCallback=lambda task: task.description())] + \
            [widgets.Column('categories', _('Categories'), 'task.category.add', 
                'task.category.remove', 
                sortCallback=self.uiCommands['viewsortbycategories'],
                renderDescriptionCallback=lambda task: task.description(),
                renderCallback=self.renderCategory)] + \
            [widgets.Column(name, columnHeader, 'task.'+name, 
             sortCallback=self.uiCommands['viewsortby' + name.lower()],
             renderCallback=renderCallback,
             renderDescriptionCallback=lambda task: task.description(),
             alignment=wx.LIST_FORMAT_RIGHT) \
             for name, columnHeader, renderCallback in \
            ('startDate', _('Start date'), lambda task: render.date(task.startDate())),
            ('dueDate', _('Due date'), lambda task: render.date(task.dueDate())),
            ('timeLeft', _('Days left'), lambda task: render.daysLeft(task.timeLeft())),
            ('completionDate', _('Completion date'), lambda task: render.date(task.completionDate())),
            ('budget', _('Budget'), lambda task: render.budget(task.budget())),
            ('totalBudget', _('Total budget'), lambda task: render.budget(task.budget(recursive=True))),
            ('timeSpent', _('Time spent'), lambda task: render.timeSpent(task.timeSpent())),
            ('totalTimeSpent', _('Total time spent'), lambda task: render.timeSpent(task.timeSpent(recursive=True))),
            ('budgetLeft', _('Budget left'), lambda task: render.budget(task.budgetLeft())),
            ('totalBudgetLeft', _('Total budget left'), lambda task: render.budget(task.budgetLeft(recursive=True))),
            ('priority', _('Priority'), lambda task: render.priority(task.priority())),
            ('totalPriority', _('Overall priority'), lambda task: render.priority(task.priority(recursive=True))),
            ('hourlyFee', _('Hourly fee'), lambda task: render.amount(task.hourlyFee())),
            ('fixedFee', _('Fixed fee'), lambda task: render.amount(task.fixedFee())),
            ('totalFixedFee', _('Total fixed fee'), lambda task: render.amount(task.fixedFee(recursive=True))),
            ('revenue', _('Revenue'), lambda task: render.amount(task.revenue())),
            ('totalRevenue', _('Total revenue'), lambda task: render.amount(task.revenue(recursive=True))),
            ('reminder', _('Reminder'), lambda task: render.dateTime(task.reminder())),
            ('lastModificationTime', _('Last modification time'), lambda task: render.dateTime(task.lastModificationTime())),
            ('totalLastModificationTime', _('Overall last modification time'),
            lambda task: render.dateTime(task.lastModificationTime(recursive=True)))]
            
    def subjectImageIndex(self, task, which):
        normalImageIndex, expandedImageIndex = self.getImageIndices(task) 
        if which in [wx.TreeItemIcon_Expanded, wx.TreeItemIcon_SelectedExpanded]:
            return expandedImageIndex 
        else:
            return normalImageIndex
                    
    def attachmentImageIndex(self, task, which):
        if task.attachments():
            return self.imageIndex['attachment'] 
        else:
            return -1
                
    def createColumnPopupMenu(self):
        return menu.ColumnPopupMenu(self, self.uiCommands)

    def renderCategory(self, task):
        return ', '.join(sorted([category.subject() for category in task.categories()]))


class TaskListViewer(TaskViewerWithColumns, ListViewer):
    defaultTitle = _('Task list')
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'tasklistviewer')
        super(TaskListViewer, self).__init__(*args, **kwargs)
    
    def createWidget(self):
        imageList = self.createImageList() # Has side-effects
        self._columns = self._createColumns()
        widget = widgets.ListCtrl(self, self.columns(),
            self.getItemText, self.getItemDescription, self.getItemImage,
            self.getItemAttr, self.onSelect, self.uiCommands['edittask'], 
            self.createTaskPopupMenu(),
            self.createColumnPopupMenu(),
            **self.widgetCreationKeywordArguments())
        widget.AssignImageList(imageList, wx.IMAGE_LIST_SMALL)
        return widget
                
    def renderSubject(self, task):
        return render.subject(task, recursively=True)

    def getFilterUICommands(self):
        uiCommands = super(TaskListViewer, self).getFilterUICommands()
        uiCommands.extend([None, 'hidecompositetasks'])
        return uiCommands


class TaskTreeViewer(TaskViewer, TreeViewer):
    defaultTitle = _('Task tree') 
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'tasktreeviewer')
        super(TaskTreeViewer, self).__init__(*args, **kwargs)       

    def createWidget(self):
        imageList = self.createImageList() # Has side-effects
        widget = widgets.TreeCtrl(self, self.getItemText, self.getItemDescription,
            self.getItemImage, self.getItemAttr,
            self.getChildrenCount, self.onSelect, self.uiCommands['edittask'], 
            self.uiCommands['draganddroptask'], self.createTaskPopupMenu(),
            **self.widgetCreationKeywordArguments())
        widget.AssignImageList(imageList)
        return widget
    
    def getItemText(self, index):
        task = self.getItemWithIndex(index)
        return task.subject()

    def getItemDescription(self, index):
        task = self.getItemWithIndex(index)
        return task.description()

    def getItemImage(self, index, which):
        task = self.getItemWithIndex(index)
        normalImageIndex, expandedImageIndex = self.getImageIndices(task)
        if which in [wx.TreeItemIcon_Expanded, wx.TreeItemIcon_SelectedExpanded]:
            return expandedImageIndex 
        else:
            return normalImageIndex
                           
    def renderSubject(self, task):
        return render.subject(task, recursively=False)

    def setSearchFilter(self, searchString, *args, **kwargs):
        super(TaskTreeViewer, self).setSearchFilter(searchString, *args, **kwargs)
        if searchString:
            self.expandAll()


class TaskTreeListViewer(TaskViewerWithColumns, TaskTreeViewer):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'tasktreelistviewer')
        super(TaskTreeListViewer, self).__init__(*args, **kwargs)

    def createWidget(self):
        imageList = self.createImageList() # Has side-effects
        self._columns = self._createColumns()
        widget = widgets.TreeListCtrl(self, self.columns(), self.getItemText,
            self.getItemDescription, self.getItemImage, self.getItemAttr,
            self.getChildrenCount, self.onSelect, 
            self.uiCommands['edittask'], self.uiCommands['draganddroptask'],
            self.createTaskPopupMenu(), self.createColumnPopupMenu(),
            **self.widgetCreationKeywordArguments())
        widget.AssignImageList(imageList)
        return widget    

    def getItemText(self, *args, **kwargs):
        return TaskViewerWithColumns.getItemText(self, *args, **kwargs)

    def getItemDescription(self, *args, **kwargs):
        return TaskViewerWithColumns.getItemDescription(self, *args, **kwargs)

    def getItemImage(self, *args, **kwargs):
        return TaskViewerWithColumns.getItemImage(self, *args, **kwargs)

    
class CategoryViewer(SortableViewerForCategories, SearchableViewer, TreeViewer):
    SorterClass = category.CategorySorter
    defaultTitle = _('Categories')
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'categoryviewer')
        super(CategoryViewer, self).__init__(*args, **kwargs)
        for eventType in category.Category.subjectChangedEventType(), \
                         category.Category.filterChangedEventType():
            patterns.Publisher().registerObserver(self.onCategoryChanged, 
                eventType)
    
    def createWidget(self):
        widget = widgets.CheckTreeCtrl(self, self.getItemText, self.getItemDescription,
            self.getItemImage, self.getItemAttr, self.getChildrenCount,
            self.getIsItemChecked, self.onSelect, self.onCheck,
            self.uiCommands['editcategory'], 
            self.uiCommands['draganddropcategory'], 
            self.createCategoryPopupMenu())
        return widget

    def createCategoryPopupMenu(self):
        return menu.CategoryPopupMenu(self.parent, self.uiCommands)

    def createFilter(self, categories):
        return base.SearchFilter(categories, treeMode=True)
    
    def onCategoryChanged(self, event):
        category = event.source()
        if category in self.list:
            self.widget.RefreshItem(self.getIndexOfItem(category))

    def onCheck(self, event):
        category = self.getItemWithIndex(self.widget.GetIndexOfItem(event.GetItem()))
        category.setFiltered(event.GetItem().IsChecked())
        self.onSelect(event) # Notify status bar
            
    def getItemText(self, index):    # FIXME: pull up to TreeViewer
        category = self.getItemWithIndex(index)
        return category.subject()

    def getItemDescription(self, index):
        return None

    def getItemImage(self, index, which):
        return -1
    
    def getItemAttr(self, index):
        return wx.ListItemAttr()
    
    def getIsItemChecked(self, index):
        return self.getItemWithIndex(index).isFiltered()

    def isShowingCategories(self):
        return True

    def statusMessages(self):
        status1 = _('Categories: %d selected, %d total')%\
            (len(self.curselection()), len(self.list))
        status2 = _('Status: %d filtered')%len([category for category in self.list if category.isFiltered()])
        return status1, status2

    def newItemDialog(self, *args, **kwargs):
        return dialog.editor.CategoryEditor(wx.GetTopLevelParent(self), 
            command.NewCategoryCommand(self.list),
            self.list, self.uiCommands, bitmap=kwargs['bitmap'])
    
    # See TaskViewer for why the methods below have two names.
    
    def editItemDialog(self, *args, **kwargs):
        return dialog.editor.CategoryEditor(wx.GetTopLevelParent(self),
            command.EditCategoryCommand(self.list, self.curselection()),
            self.list, self.uiCommands, bitmap=kwargs['bitmap'])
    
    editCategoryDialog = editItemDialog
    
    def deleteItemCommand(self):
        return command.DeleteCommand(self.list, self.curselection())
    
    deleteCategoryCommand = deleteItemCommand
    
    def newSubItemDialog(self, *args, **kwargs):
        return dialog.editor.CategoryEditor(wx.GetTopLevelParent(self), 
            command.NewSubCategoryCommand(self.list, self.curselection()),
            self.list, self.uiCommands, bitmap=kwargs['bitmap'])
        
    newSubCategoryDialog = newSubItemDialog


class NoteViewer(SearchableViewer, SortableViewerWithColumns, 
                 SortableViewerForNotes, TreeViewer):
    SorterClass = note.NoteSorter
    defaultTitle = _('Notes')
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'noteviewer')
        super(NoteViewer, self).__init__(*args, **kwargs)
        for eventType in [note.Note.subjectChangedEventType()]:
            patterns.Publisher().registerObserver(self.onNoteChanged, 
                eventType)

    def createWidget(self):
        imageList = self.createImageList() # Has side-effects
        self._columns = self._createColumns()
        widget = widgets.TreeListCtrl(self, self.columns(), self.getItemText, 
            self.getItemDescription, self.getItemImage, self.getItemAttr, 
            self.getChildrenCount, self.onSelect,
            self.uiCommands['editnote'], 
            self.uiCommands['draganddropnote'], 
            self.createNotePopupMenu(), self.createColumnPopupMenu())
        widget.AssignImageList(imageList)
        return widget
    
    def createFilter(self, notes):
        return base.SearchFilter(notes, treeMode=True)
    
    def createImageList(self):
        imageList = wx.ImageList(16, 16)
        self.imageIndex = {}
        for index, image in enumerate(['ascending', 'descending']):
            imageList.Add(wx.ArtProvider_GetBitmap(image, wx.ART_MENU, (16,16)))
            self.imageIndex[image] = index
        return imageList

    def getColumnUICommands(self):
        return ['viewdescription']

    def createNotePopupMenu(self):
        return menu.NotePopupMenu(self.parent, self.uiCommands)

    def createColumnPopupMenu(self):
        return menu.ColumnPopupMenu(self, self.uiCommands)

    def _createColumns(self):
        return [widgets.Column(name, columnHeader, 'note.'+name, 
                renderCallback=renderCallback, 
                sortCallback=self.uiCommands['viewsortby' + name.lower()]) \
            for name, columnHeader, renderCallback in \
            ('subject', _('Subject'), lambda note: render.subject(note, recursively=False)),
            ('description', _('Description'), lambda note: note.description())]
                     
    def onNoteChanged(self, event):
        note = event.source()
        if note in self.list:
            self.widget.RefreshItem(self.getIndexOfItem(note))
            
    def getItemText(self, index, column=0):
        item = self.getItemWithIndex(index)
        column = self.visibleColumns()[column]
        return column.render(item)

    def getItemDescription(self, index, column=0):
        note = self.getItemWithIndex(index)
        return note.description()

    def getItemImage(self, index, which, column=0):
        return -1
    
    def getItemAttr(self, index):
        return wx.ListItemAttr()
        
    def isShowingNotes(self):
        return True

    def statusMessages(self):
        status1 = _('Notes: %d selected, %d total')%\
            (len(self.curselection()), len(self.list))
        status2 = _('Status: n/a')
        return status1, status2

    def newItemDialog(self, *args, **kwargs):
        return dialog.editor.NoteEditor(wx.GetTopLevelParent(self), 
            command.NewNoteCommand(self.list),
            self.list, self.uiCommands, bitmap=kwargs['bitmap'])
    
    # See TaskViewer for why the methods below have two names.
    
    def editItemDialog(self, *args, **kwargs):
        return dialog.editor.NoteEditor(wx.GetTopLevelParent(self),
            command.EditNoteCommand(self.list, self.curselection()),
            self.list, self.uiCommands, bitmap=kwargs['bitmap'])
    
    editNoteDialog = editItemDialog
    
    def deleteItemCommand(self):
        return command.DeleteCommand(self.list, self.curselection())
    
    deleteNoteCommand = deleteItemCommand
    
    def newSubItemDialog(self, *args, **kwargs):
        return dialog.editor.NoteEditor(wx.GetTopLevelParent(self), 
            command.NewSubNoteCommand(self.list, self.curselection()),
            self.list, self.uiCommands, bitmap=kwargs['bitmap'])
        
    newSubNoteDialog = newSubItemDialog
    
    
class EffortViewer(SortableViewerForEffort, SearchableViewer, 
                   UpdatePerSecondViewer):
    SorterClass = effort.EffortSorter
    
    def isSortable(self):
        return False # FIXME: make effort viewers sortable too?
    
    def isShowingEffort(self):
        return True
    
    def trackStartEventType(self):
        return 'effort.track.start'
    
    def trackStopEventType(self):
        return 'effort.track.stop'

    def statusMessages(self):
        status1 = _('Effort: %d selected, %d visible, %d total')%\
            (len(self.curselection()), len(self.list), 
             self.list.originalLength())         
        status2 = _('Status: %d tracking')% self.list.nrBeingTracked()
        return status1, status2
 
    # See TaskViewer for why the methods below have two names.
    
    def newItemDialog(self, *args, **kwargs):
        selectedTasks = kwargs.get('selectedTasks', [])
        if not selectedTasks:
            subjectDecoratedTaskList = [(render.subject(task, 
                recursively=True), task) for task in self.taskList]
            subjectDecoratedTaskList.sort() # Sort by subject
            selectedTasks = [subjectDecoratedTaskList[0][1]]
        return dialog.editor.EffortEditor(wx.GetTopLevelParent(self), 
            command.NewEffortCommand(self.list, selectedTasks),
            self.uiCommands, self.list, self.taskList, bitmap=kwargs['bitmap'])
        
    newEffortDialog = newItemDialog
    
    def editItemDialog(self, *args, **kwargs):
        return dialog.editor.EffortEditor(wx.GetTopLevelParent(self),
            command.EditEffortCommand(self.list, self.curselection()), 
            self.uiCommands, self.list, self.taskList)
    
    editEffortDialog = editItemDialog
    
    def deleteItemCommand(self):
        return command.DeleteCommand(self.list, self.curselection())
    
    deleteEffortCommand = deleteItemCommand
    

class EffortListViewer(ListViewer, EffortViewer, ViewerWithColumns): 
    defaultTitle = _('Effort details')  
    
    def __init__(self, parent, list, *args, **kwargs):
        self.taskList = list
        kwargs.setdefault('settingsSection', 'effortlistviewer')
        super(EffortListViewer, self).__init__(parent, list, *args, **kwargs)
        
    def createWidget(self):
        # We need to create new uiCommands here, because the viewer might not
        # be the effort viewer in the mainwindow, but the effort viewer in the 
        # task edit window.
        uiCommands = {}
        uiCommands.update(self.uiCommands)
        uiCommands.update(uicommand.EditorUICommands(self, self.list))        
        self._columns = self._createColumns()
        widget = widgets.ListCtrl(self, self.columns(),
            self.getItemText, self.getItemDescription, self.getItemImage,
            self.getItemAttr, self.onSelect, uiCommands['editeffort'], 
            menu.EffortPopupMenu(self.parent, uiCommands), 
            menu.ColumnPopupMenu(self, uiCommands), 
            resizeableColumn=1, **self.widgetCreationKeywordArguments())
        widget.SetColumnWidth(0, 150)
        return widget
    
    def _createColumns(self):
        return [widgets.Column(name, columnHeader, eventType, 
                renderCallback=renderCallback) \
            for name, columnHeader, eventType, renderCallback in \
            ('period', _('Period'), 'effort.duration', self.renderPeriod),
            ('task', _('Task'), 'effort.task', lambda effort: render.subject(effort.task(), recursively=True)),
            ('description', _('Description'), 'effort.description', lambda effort: effort.getDescription())] + \
            [widgets.Column(name, columnHeader, eventType, 
             renderCallback=renderCallback, alignment=wx.LIST_FORMAT_RIGHT) \
            for name, columnHeader, eventType, renderCallback in \
            ('timeSpent', _('Time spent'), 'effort.duration', 
                lambda effort: render.timeSpent(effort.duration())),
            ('revenue', _('Revenue'), 'effort.duration', 
                lambda effort: render.amount(effort.revenue()))]

    def createFilter(self, taskList):
        return effort.EffortList(base.SearchFilter(taskList))

    def getColumnUICommands(self):
        return ['viewdescription', 'viewtimeSpent', 'viewrevenue']
                
    def getItemImage(self, index, which, column=0):
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
            [widgets.Column(name, columnHeader, eventType, 
              renderCallback=renderCallback, alignment=wx.LIST_FORMAT_RIGHT) \
             for name, columnHeader, eventType, renderCallback in \
                ('totalTimeSpent', _('Total time spent'), 'effort.totalDuration',  
                 lambda effort: render.timeSpent(effort.duration(recursive=True))),
                ('totalRevenue', _('Total revenue'), 'effort.totalDuration',
                 lambda effort: render.amount(effort.revenue(recursive=True)))]
        
    def curselection(self):
        compositeEfforts = super(CompositeEffortListViewer, self).curselection()
        return [effort for compositeEffort in compositeEfforts for effort in compositeEffort]

    def createFilter(self, taskList):
        return self.EffortPerPeriod(base.SearchFilter(taskList))

    def getColumnUICommands(self):
        commands = super(CompositeEffortListViewer, self).getColumnUICommands()
        commands.insert(-1, 'viewtotalTimeSpent')
        commands.append('viewtotalRevenue')
        return commands
    

class EffortPerDayViewer(CompositeEffortListViewer):
    EffortPerPeriod = effort.EffortPerDay
    defaultTitle = _('Effort per day')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'effortperdayviewer')
        super(EffortPerDayViewer, self).__init__(*args, **kwargs)
    
    def renderEntirePeriod(self, compositeEffort):
        return render.date(compositeEffort.getStart().date())

        
class EffortPerWeekViewer(CompositeEffortListViewer):
    EffortPerPeriod = effort.EffortPerWeek
    defaultTitle = _('Effort per week')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'effortperweekviewer')
        super(EffortPerWeekViewer, self).__init__(*args, **kwargs)

    def renderEntirePeriod(self, compositeEffort):
        return render.weekNumber(compositeEffort.getStart())


class EffortPerMonthViewer(CompositeEffortListViewer):
    EffortPerPeriod = effort.EffortPerMonth
    defaultTitle = _('Effort per month')
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'effortpermonthviewer')
        super(EffortPerMonthViewer, self).__init__(*args, **kwargs)
    
    def renderEntirePeriod(self, compositeEffort):
        return render.month(compositeEffort.getStart())

