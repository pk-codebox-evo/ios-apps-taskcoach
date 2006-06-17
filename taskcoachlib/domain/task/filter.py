import patterns, re, sets
import domain.date as date

class Filter(patterns.ObservableListObserver):
    def __init__(self, *args, **kwargs):
        self.setTreeMode(kwargs.pop('treeMode', False))
        super(Filter, self).__init__(*args, **kwargs)
        
    def setTreeMode(self, treeMode):
        self.__treeMode = treeMode
        
    def treeMode(self):
        return self.__treeMode
        
    def processChanges(self, notification):
        oldSelf = self[:]
        self[:] = [item for item in self.original() if self.filter(item)]
        notification['itemsAdded'] = [item for item in self if item not in oldSelf]
        notification['itemsRemoved'] = [item for item in oldSelf if item not in self]
        notification['itemsChanged'] = [item for item in notification.itemsChanged if item in self and item not in notification.itemsAdded+notification.itemsRemoved]
        return notification
            
    def filter(self, item):
        ''' filter returns False if the item should be hidden. '''
        raise NotImplementedError

    def rootTasks(self):
        return [task for task in self if task.parent() is None]

    def onSettingChanged(self, notification):
        self.reset()

    
class ViewFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        for setting in ('tasksdue', 'completedtasks', 'inactivetasks',
                        'activetasks', 'overduetasks', 'overbudgetasks'):
            self.__settings.registerObserver(self.onSettingChanged, 
                ('view', setting))
        super(ViewFilter, self).__init__(*args, **kwargs)
        
    def getViewTasksDueBeforeDate(self):
        dateFactory = { 'Today' : date.Today, 
                        'Tomorrow' : date.Tomorrow,
                        'Workweek' : date.NextFriday, 
                        'Week' : date.NextSunday, 
                        'Month' : date.LastDayOfCurrentMonth, 
                        'Year' : date.LastDayOfCurrentYear, 
                        'Unlimited' : date.Date }        
        return dateFactory[self.__settings.get('view', 'tasksdue')]()
        
    def filter(self, task):
        settings = self.__settings
        if task.completed() and not settings.getboolean('view', 'completedtasks'):
            return False
        if task.inactive() and not settings.getboolean('view', 'inactivetasks'):
            return False
        if task.overdue() and not settings.getboolean('view', 'overduetasks'):
            return False
        if task.active() and not settings.getboolean('view', 'activetasks'):
            return False
        if task.budgetLeft(recursive=True) < date.TimeDelta() and not \
                settings.getboolean('view', 'overbudgettasks'):
            return False
        if task.dueDate(recursive=self.treeMode()) > self.getViewTasksDueBeforeDate():
            return False        
        return True


class CompositeFilter(Filter):
    ''' Filter composite tasks '''
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        self.__settings.registerObserver(self.onSettingChanged, 
                                         ('view', 'compositetasks'))
        super(CompositeFilter, self).__init__(*args, **kwargs)

    def filter(self, task):
        return (not task.children()) or \
            self.__settings.getboolean('view', 'compositetasks')
    

class SearchFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        self.__settings.registerObserver(self.onSettingChanged, 
                                         ('view', 'tasksearchfilterstring'))
        self.__settings.registerObserver(self.onSettingChanged,
                                         ('view', 'tasksearchfiltermatchcase'))
        super(SearchFilter, self).__init__(*args, **kwargs)

    def filter(self, task):
        return self.__matches(task)
        
    def __matches(self, task):
        return re.search('.*%s.*'%self.__settings.get('view', 
            'tasksearchfilterstring'), 
            self.__taskSubject(task), 
            self.__matchCase())

    def __taskSubject(self, task):
        subject = task.subject()
        if self.treeMode():
            subject += ''.join([child.subject() for child in task.allChildren()
                if child in self.original()])
        return subject
    
    def __matchCase(self):
        if self.__settings.getboolean('view', 'tasksearchfiltermatchcase'):
            return 0
        else:
            return re.IGNORECASE


class CategoryFilter(Filter):
    def __init__(self, *args, **kwargs):
        self._categories = sets.Set()
        self.__settings = kwargs.pop('settings')
        self.__settings.registerObserver(self.onSettingChanged, 
                                         ('view', 'taskcategoryfiltermatchall'))
        super(CategoryFilter, self).__init__(*args, **kwargs)
        
    def filter(self, task):
        if not self._categories:
            return True
        filterOnlyWhenAllCategoriesMatch = self.__settings.getboolean('view', 
            'taskcategoryfiltermatchall')
        matches = [category in task.categories(recursive=True) 
                   for category in self._categories]
        if filterOnlyWhenAllCategoriesMatch:
            return False not in matches
        else:
            return True in matches
            
    def addCategory(self, category):
        self._categories.add(category)
        self.notifyObservers(patterns.Notification(self, category=category),
            'filter.category.add')
        self.reset()
        
    def removeCategory(self, category):
        self._categories.discard(category)
        self.notifyObservers(patterns.Notification(self, category=category),
            'filter.category.remove')
        self.reset()
        
    def removeAllCategories(self):
        self._categories.clear()
        self.notifyObservers(patterns.Notification(self),
            'filter.category.removeall')
        self.reset()
            
    def filteredCategories(self):
        return self._categories
                
