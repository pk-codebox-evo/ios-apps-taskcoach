import patterns, date

class Effort(patterns.Observable):
    def __init__(self, task, start=None, stop=None, *args, **kwargs):
        super(Effort, self).__init__(*args, **kwargs)
        self._task = task
        now = date.DateTime.now()
        self._start = start or now
        self._stop = stop or now
    
    def __getstate__(self):
        return {'_task' : self._task, '_start' : self._start, '_stop' : self._stop }
        
    def __setstate__(self, state):
        self.__dict__.update(state)
        self._notifyObserversOfChange()
        
    def task(self):
        return self._task
        
    def duration(self, now=date.DateTime.now):
        if self._stop:
            stop = self._stop
        else:
            stop = now()
        return stop - self._start
        
    def setStart(self, startDatetime):
        self._start = startDatetime
        self._notifyObserversOfChange()
        
    def getStart(self):
        return self._start
        
    def setStop(self, stopDatetime):
        self._stop = stopDatetime
        self._notifyObserversOfChange()
        
    def getStop(self):
        return self._stop

    def __cmp__(self, other):
        return cmp(self.getStart(), other.getStart())

        
class CompositeEffort(list):
    ''' CompositeEffort is a list of efforts for one (!) task. '''
    
    def duration(self):
        return sum([effort.duration() for effort in self], date.TimeDelta())
        
    def getStart(self):
        if self:
            return min([effort.getStart() for effort in self])
        else:
            return None
            
    def getStop(self):
        if self:
            return max([effort.getStop() for effort in self])
        else:
            return None
            
    def task(self):
        if self:
            return self[0].task()
        else:
            return None
            
    def __lt__(self, other):
        return self.getStart() < other.getStart() or \
            (self.getStart() == other.getStart() and \
            self.task().subject() < other.task().subject())
