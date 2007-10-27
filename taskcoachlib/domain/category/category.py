import patterns
from domain import base

class Category(base.Object, patterns.ObservableComposite):
    def __init__(self, subject, tasks=None, children=None, filtered=False, 
                 parent=None, description=''):
        super(Category, self).__init__(subject=subject, children=children or [], 
                                       parent=parent, description=description)
        self.__tasks = tasks or []
        self.__filtered = filtered
            
    @classmethod
    def filterChangedEventType(class_):
        return 'category.filter'
        
    def __getstate__(self):
        state = super(Category, self).__getstate__()
        state.update(dict(tasks=self.__tasks[:], 
                          filtered=self.__filtered))
        return state
        
    def __setstate__(self, state):
        super(Category, self).__setstate__(state)
        self.__tasks = state['tasks']
        self.__filtered = state['filtered']
        
    def __repr__(self):
        return self.subject()
                    
    def subject(self, recursive=False):
        mySubject = super(Category, self).subject()
        if recursive and self.parent():
            return '%s -> %s'%(self.parent().subject(recursive=True), 
                               mySubject)
        else:
            return mySubject
    
    def tasks(self, recursive=False):
        result = []
        if recursive:
            for child in self.children():
                result.extend(child.tasks(recursive))
        result.extend(self.__tasks)
        return result
    
    def addTask(self, task):
        if task not in self.__tasks: # FIXME: use set
            self.__tasks.append(task)
            
    def removeTask(self, task):
        if task in self.__tasks:
            self.__tasks.remove(task)
        
    def isFiltered(self):
        return self.__filtered
    
    def setFiltered(self, filtered=True):
        if filtered != self.__filtered:
            self.__filtered = filtered
            self.notifyObservers(patterns.Event(self, 
                self.filterChangedEventType(), filtered))
        
    def contains(self, task, treeMode=False):
        containedTasks = self.tasks(recursive=True)
        if treeMode:
            tasksToInvestigate = task.family()
        else:
            tasksToInvestigate = [task] + task.ancestors()
        for task in tasksToInvestigate:
            if task in containedTasks:
                return True
        return False