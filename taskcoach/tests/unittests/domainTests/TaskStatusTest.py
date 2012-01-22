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

import test
from taskcoachlib.domain import task, date
from taskcoachlib import config


class TaskStatusTest(test.TestCase):    
    def setUp(self):
        self.settings = task.Task.settings = config.Settings(load=False)
        self.now = date.Now()
        self.yesterday = self.now - date.oneDay
        self.tomorrow = self.now + date.oneDay
        self.dates = (self.yesterday, self.tomorrow)
        self.dayAfterTomorrow = self.tomorrow + date.oneDay

    def assertTaskStatus(self, status, **taskKwArgs):
        self.assertEqual(status, task.Task(**taskKwArgs).status())
        
    # No dates/times
    
    def testDefaultTaskIsInactive(self):
        self.assertTaskStatus('inactive')
    
    # One date/time
        
    def testTaskWithCompletionInThePastIsCompleted(self):
        self.assertTaskStatus('completed', completionDateTime=self.yesterday)
        
    def testTaskWithCompletionInTheFutureIsCompleted(self):
        # Maybe keep the task inactive until the completion date passes? 
        # That would be more consistent with the other date/times
        self.assertTaskStatus('completed', completionDateTime=self.tomorrow)

    def testTaskWithPlannedStartInThePastIsLate(self):
        self.assertTaskStatus('late', plannedStartDateTime=self.yesterday)
                
    def testTaskWithPlannedStartInTheFutureIsInactive(self):
        self.assertTaskStatus('inactive', plannedStartDateTime=self.tomorrow)
        
    def testTaskWithActualStartInThePastIsActive(self):
        self.assertTaskStatus('active', actualStartDateTime=self.yesterday)

    def testTaskWithActualStartInTheFutureIsInactive(self):
        self.assertTaskStatus('inactive', actualStartDateTime=self.tomorrow)
        
    def testTaskWithDueInThePastIsOverdue(self):
        self.assertTaskStatus('overdue', dueDateTime=self.yesterday)

    def testTaskWithDueInTheFutureIsInactive(self):
        self.assertTaskStatus('inactive', dueDateTime=self.dayAfterTomorrow)
        
    def testTaskWithDueInTheNearFutureIsDueSoon(self):
        self.assertTaskStatus('duesoon', dueDateTime=self.tomorrow)
    
    # Two dates/times
    
    # planned start date/time and actual start date/time
        
    def testTaskWithPlannedAndActualStartInThePastIsActive(self):
        self.assertTaskStatus('active', plannedStartDateTime=self.yesterday,
                                        actualStartDateTime=self.yesterday)
        
    def testTaskWithPlannedStartInThePastAndActualStartInTheFutureIsLate(self):
        self.assertTaskStatus('late', plannedStartDateTime=self.yesterday,
                                      actualStartDateTime=self.tomorrow)
        
    def testTaskWithPlannedStartInTheFutureAndActualStartInThePastIsActive(self):
        self.assertTaskStatus('active', plannedStartDateTime=self.tomorrow,
                                        actualStartDateTime=self.yesterday)

    def testTaskWithPlannedAndActualStartInTheFutureIsInactive(self):
        self.assertTaskStatus('inactive', plannedStartDateTime=self.tomorrow,
                                          actualStartDateTime=self.tomorrow)
    
    # planned start date/time and due date/time
        
    def testTaskWithPlannedStartAndDueInThePastIsOverdue(self):
        self.assertTaskStatus('overdue', plannedStartDateTime=self.yesterday,
                                         dueDateTime=self.yesterday)

    def testTaskWithPlannedStartInThePastAndDueInTheFutureIsLate(self):
        self.assertTaskStatus('late', plannedStartDateTime=self.yesterday,
                                      dueDateTime=self.dayAfterTomorrow)
       
    def testTaskWithPlannedStartInThePastAndDueInTheNearFutureIsDueSoon(self):
        self.assertTaskStatus('duesoon', plannedStartDateTime=self.yesterday,
                                         dueDateTime=self.tomorrow)
       
    def testTaskWithPlannedStartInTheFutureAndDueInThePastIsOverdue(self):
        self.assertTaskStatus('overdue', plannedStartDateTime=self.tomorrow,
                                         dueDateTime=self.yesterday)

    def testTaskWithPlannedStartInTheFutureAndDueInTheFutureIsLate(self):
        self.assertTaskStatus('inactive', plannedStartDateTime=self.tomorrow,
                                          dueDateTime=self.dayAfterTomorrow)
       
    def testTaskWithPlannedStartInTheFutureAndDueInTheNearFutureIsDueSoon(self):
        self.assertTaskStatus('duesoon', plannedStartDateTime=self.tomorrow,
                                         dueDateTime=self.tomorrow)

    # planned start date/time and completion date/time
    
    def testTaskWithPlannedStartAndCompletionInThePastIsCompleted(self):
        self.assertTaskStatus('completed', plannedStartDateTime=self.yesterday,
                                           completionDateTime=self.yesterday)

    def testTaskWithPlannedStartInThePastAndCompletionInTheFutureIsCompleted(self):
        self.assertTaskStatus('completed', plannedStartDateTime=self.yesterday,
                                           completionDateTime=self.tomorrow)

    def testTaskWithPlannedStartInTheFutureAndCompletionInThePastIsCompleted(self):
        self.assertTaskStatus('completed', plannedStartDateTime=self.tomorrow,
                                           completionDateTime=self.yesterday)

    def testTaskWithPlannedStartInTheFutureAndCompletionInTheFutureIsComplete(self):
        self.assertTaskStatus('completed', plannedStartDateTime=self.tomorrow,
                                           completionDateTime=self.tomorrow)
    
    # actual start date/time and due date/time
    
    def testTaskWithActualStartAndDueInThePastIsOverdue(self):
        self.assertTaskStatus('overdue', actualStartDateTime=self.yesterday,
                                         dueDateTime=self.yesterday)

    def testTaskWithActualStartInThePastAndDueInTheFutureIsActive(self):
        self.assertTaskStatus('active', actualStartDateTime=self.yesterday,
                                        dueDateTime=self.dayAfterTomorrow)

    def testTaskWithActualStartInThePastAndDueInTheNearFutureIsDueSoon(self):
        self.assertTaskStatus('duesoon', actualStartDateTime=self.yesterday,
                                         dueDateTime=self.tomorrow)

    def testTaskWithActualStartInTheFutureAndDueInThePastIsOverdue(self):
        self.assertTaskStatus('overdue', actualStartDateTime=self.tomorrow,
                                         dueDateTime=self.yesterday)

    def testTaskWithActualStartInTheFutureAndDueInTheFutureIsActive(self):
        self.assertTaskStatus('inactive', actualStartDateTime=self.tomorrow,
                                          dueDateTime=self.dayAfterTomorrow)

    def testTaskWithActualStartInTheFutureAndDueInTheNearFutureIsDueSoon(self):
        self.assertTaskStatus('duesoon', actualStartDateTime=self.tomorrow,
                                         dueDateTime=self.tomorrow)

    # actual start date/time and completion date/time
   
    def testTaskWithActualStartAndCompletionInThePastIsCompleted(self):
        self.assertTaskStatus('completed', actualStartDateTime=self.yesterday,
                                           completionDateTime=self.yesterday)

    def testTaskWithActualStartInThePastAndCompletionInTheFutureIsCompleted(self):
        self.assertTaskStatus('completed', actualStartDateTime=self.yesterday,
                                           completionDateTime=self.tomorrow)

    def testTaskWithActualStartInTheFutureAndCompletionInThePastIsCompleted(self):
        self.assertTaskStatus('completed', actualStartDateTime=self.tomorrow,
                                           completionDateTime=self.yesterday)

    def testTaskWithActualStartInTheFutureAndCompletionInTheFutureIsComplete(self):
        self.assertTaskStatus('completed', actualStartDateTime=self.tomorrow,
                                           completionDateTime=self.tomorrow)
   
    # due date/time and completion date/time
    
    def testTaskWithDueAndCompletionInThePastIsCompleted(self):
        self.assertTaskStatus('completed', dueDateTime=self.yesterday,
                                           completionDateTime=self.yesterday)

    def testTaskWithDueInThePastAndCompletionInTheFutureIsCompleted(self):
        self.assertTaskStatus('completed', dueDateTime=self.yesterday,
                                           completionDateTime=self.tomorrow)

    def testTaskWithDueInTheFutureAndCompletionInThePastIsCompleted(self):
        self.assertTaskStatus('completed', dueDateTime=self.tomorrow,
                                           completionDateTime=self.yesterday)

    def testTaskWithDueInTheFutureAndCompletionInTheFutureIsComplete(self):
        self.assertTaskStatus('completed', dueDateTime=self.tomorrow,
                                           completionDateTime=self.tomorrow)
   
    # Three dates/times
    
    # planned start date/time, actual start date/time and due date/time
    # (Other combinations are not interesting since they are always completed)
    
    def testTaskIsOverdueWheneverDueIsInThePast(self):
        for planned in self.dates:
            for actual in self.dates:
                self.assertTaskStatus('overdue', plannedStartDateTime=planned,
                                                 actualStartDateTime=actual,
                                                 dueDateTime=self.yesterday)

    def testTaskIsDuesoonWheneverDueIsInTheNearFuture(self):
        for planned in self.dates:
            for actual in self.dates:
                self.assertTaskStatus('duesoon', plannedStartDateTime=planned,
                                                 actualStartDateTime=actual,
                                                 dueDateTime=self.tomorrow)
         
    def testTaskIsOverdueWheneverDueIsInTheFuture(self):
        for planned in self.dates:
            expectedStatusBasedOnPlannedStart = 'late' if planned < self.now else 'inactive'
            for actual in self.dates:
                expectedStatus = 'active' if actual < self.now else expectedStatusBasedOnPlannedStart
                self.assertTaskStatus(expectedStatus, plannedStartDateTime=planned,
                                                      actualStartDateTime=actual,
                                                      dueDateTime=self.dayAfterTomorrow)
               
    # Four date/times (always completed)
    
    def testTaskWithCompletionDateTimeIsAlwaysCompleted(self):
        for planned in self.dates:
            for actual in self.dates:
                for due in self.dates + (self.dayAfterTomorrow,):
                    for completion in self.dates:
                        self.assertTaskStatus('completed', plannedStartDateTime=planned,
                                                           actualStartDateTime=actual,
                                                           dueDateTime=due,
                                                           completionDateTime=completion)

    # Prerequisites
    
    def testTaskWithUncompletedPrerequisiteIsNeverLate(self):
        prerequisite = task.Task()
        for planned in self.dates:
            self.assertTaskStatus('inactive', plannedStartDateTime=planned,
                                              prerequisites=[prerequisite])

    def testTaskWithCompletedPrerequisiteIsLateWhenPlannedStartIsInThePast(self):
        prerequisite = task.Task(completionDateTime=self.yesterday)
        for planned in self.dates:
            expectedStatus = 'late' if planned < self.now else 'inactive'
            self.assertTaskStatus(expectedStatus, plannedStartDateTime=planned,
                                                  prerequisites=[prerequisite])
             