import test, sets, patterns
import unittests.asserts as asserts
import domain.task as task
import domain.effort as effort
import domain.date as date

class TaskListTest(test.TestCase, asserts.TaskListAsserts):
    def setUp(self):
        self.taskList = task.TaskList()
        patterns.Publisher().registerObserver(self.onEvent,
            eventType=self.taskList.addItemEventType())
        patterns.Publisher().registerObserver(self.onEvent,
            eventType=self.taskList.removeItemEventType())
        self.task1 = task.Task(dueDate=date.Date(2010,1,1))
        self.task2 = task.Task(dueDate=date.Date(2011,1,1))
        self.task3 = task.Task()
        self.events = []

    def onEvent(self, event):
        self.events.append(event)

    def testCreate(self):
        self.assertEmptyTaskList()

    def testCreateWithArgs(self):
        self.taskList = task.TaskList([self.task1])
        self.assertTaskList([self.task1])

    def testGetItem(self):
        self.taskList.append(self.task1)
        self.assertTaskList([self.task1])
        
    def testCompareEmptyList(self):
        self.assertEqual(self.taskList, self.taskList)

    def testCompareEqualLists(self):
        self.taskList.append(self.task1)
        self.assertEqual(self.taskList, self.taskList)

    def testCompareDifferentLists(self):
        self.taskList.append(self.task1)
        anotherList = task.TaskList()
        self.failIf(self.taskList == anotherList)

    def testAppend(self):
        self.taskList.append(self.task1)
        self.assertTaskList([self.task1])

    def testAppendTaskAlreadyInList(self):
        self.taskList.append(self.task1)
        self.taskList.append(self.task1)
        self.assertTaskList([self.task1])

    def testAppendCausesNotification(self):
        self.taskList.append(self.task1)
        self.assertEqual(self.task1, self.events[0].value())

    def testAppendTwoItemsCausesTwoNotifications(self):
        self.taskList.append(self.task2)
        self.taskList.append(self.task1)
        self.assertEqual(2, len(self.events))

    def testAppendTaskWithChild(self):
        self.task1.addChild(self.task2)
        self.taskList.append(self.task1)
        self.assertTaskList([self.task1, self.task2])
    
    def testNrCompleted(self):
        self.assertEqual(0, self.taskList.nrCompleted())
        self.taskList.append(self.task1)
        self.assertEqual(0, self.taskList.nrCompleted())
        self.task1.setCompletionDate()
        self.assertEqual(1, self.taskList.nrCompleted())
    
    def testNrOverdue(self):
        self.assertEqual(0, self.taskList.nrOverdue())
        self.taskList.append(self.task1)
        self.assertEqual(0, self.taskList.nrOverdue())
        self.task1.setDueDate(date.Date(1990, 1, 1))
        self.assertEqual(1, self.taskList.nrOverdue())

    def testAllCompleted(self):
        self.failIf(self.taskList.allCompleted())
        self.task1.setCompletionDate()
        self.taskList.append(self.task1)
        self.failUnless(self.taskList.allCompleted())

    def testNrDueToday(self):
        self.assertEqual(0, self.taskList.nrDueToday())
        self.taskList.append(task.Task(dueDate=date.Today()))
        self.assertEqual(1, self.taskList.nrDueToday())
        
    def testNrBeingTracked(self):
        self.assertEqual(0, self.taskList.nrBeingTracked())
        activeTask = task.Task()
        activeTask.addEffort(effort.Effort(activeTask))
        self.taskList.append(activeTask)
        self.assertEqual(1, self.taskList.nrBeingTracked())

    def testRootTasks(self):
        self.assertEqual([], self.taskList.rootTasks())
        self.taskList.append(self.task1)
        self.assertEqual([self.task1], self.taskList.rootTasks())
        self.task2.addChild(self.task3)
        self.taskList.append(self.task2)
        self.assertEqualLists([self.task1, self.task2], 
            self.taskList.rootTasks())

    def testMinDate_EmptyTaskList(self):
        self.assertEqual(date.Date(), self.taskList.minDate())
        
    def testMinDate_TaskWithoutDates(self):
        self.taskList.append(task.Task(startDate=date.Date()))
        self.assertEqual(date.Date(), self.taskList.minDate())
        
    def testMinDate_TaskWithStartDate(self):
        self.taskList.append(task.Task())
        self.assertEqual(date.Today(), self.taskList.minDate())
        
    def testMinDate_TaskWithDueDate(self):
        self.taskList.append(task.Task(dueDate=date.Yesterday()))
        self.assertEqual(date.Yesterday(), self.taskList.minDate())

    def testMinDate_TaskWithCompletionDate(self):
        self.taskList.append(task.Task(completionDate=date.Yesterday()))
        self.assertEqual(date.Yesterday(), self.taskList.minDate())

    def testMaxDate_EmptyTaskList(self):
        self.assertEqual(date.Date(), self.taskList.maxDate())
        
    def testMaxDate_TaskWithoutDates(self):
        self.taskList.append(task.Task(startDate=date.Date()))
        self.assertEqual(date.Date(), self.taskList.maxDate())
        
    def testMaxDate_TaskWithStartDate(self):
        self.taskList.append(task.Task())
        self.assertEqual(date.Today(), self.taskList.maxDate())

    def testMaxDate_TaskWithDueDate(self):
        self.taskList.append(task.Task(dueDate=date.Tomorrow()))
        self.assertEqual(date.Tomorrow(), self.taskList.maxDate())
    
    def testMaxDate_TaskWithCompletionDate(self):
        self.taskList.append(task.Task(completionDate=date.Tomorrow()))
        self.assertEqual(date.Tomorrow(), self.taskList.maxDate())
        
    def testOriginalLength(self):
        self.assertEqual(0, self.taskList.originalLength())
        
        
class NotificationTimingTest(test.TestCase):
    def setUp(self):
        self.task1 = task.Task()
        self.task2 = task.Task()
        self.taskList = task.TaskList([self.task1])
        patterns.Publisher().registerObserver(self.onEvent, 
            eventType=self.taskList.addItemEventType())
        patterns.Publisher().registerObserver(self.onEvent,
            eventType=self.taskList.removeItemEventType())
        self.events = []
        self.assertions = {}

    def onEvent(self, event):
        self.events.append(event)
        self.assertions.get(len(self.events), lambda: 1)()

    def testAddChild(self):
        self.task2.setParent(self.task1)
        self.assertions = {1: lambda: self.assertEqual(2, len(self.taskList))}
        self.taskList.append(self.task2)
        self.assertEqual(self.task2, self.events[0].value())

    def testRemoveChild(self):
        self.task2.setParent(self.task1)
        self.assertions = {3 : lambda: self.assertEqual(1, len(self.taskList)),
            4: lambda: self.assertEqual([], self.task1.children()) }
        self.taskList.append(self.task2)
        self.taskList.remove(self.task2)
        self.assertEqual(2, len(self.events))


class RemoveTasksFromTaskListTest(test.TestCase, asserts.TaskListAsserts, 
        asserts.TaskAsserts):
    def setUp(self):
        self.task1 = task.Task('Task 1')
        self.task2 = task.Task('Task 2')
        self.task1.addChild(self.task2)
        self.task3 = task.Task('Task 3')
        self.task2.addChild(self.task3)
        self.task4 = task.Task('Task 4')
        self.taskList = task.TaskList([self.task1, self.task4])
        self.originalList = [self.task1, self.task2, self.task3, self.task4]
        patterns.Publisher().registerObserver(self.onEvent,
            eventType=self.taskList.addItemEventType())
        patterns.Publisher().registerObserver(self.onEvent,
            eventType=self.taskList.removeItemEventType())
        self.events = []

    def onEvent(self, event):
        self.events.append(event)

    def testRemoveTask(self):
        self.taskList.remove(self.task3)
        self.assertTaskList([self.task1, self.task2, self.task4])
        self.assertEqual(self.task3, self.events[0].value())
        self.failIf(self.task2.children())

    def testRemoveTaskWithChild(self):
        self.taskList.remove(self.task2)
        self.assertTaskList([self.task1, self.task4])
        self.assertEqualLists((self.task2, self.task3), self.events[0].values())
        self.failIf(self.task1.children())

    def testRemoveTaskWithGrandchild(self):
        self.taskList.remove(self.task1)
        self.assertTaskList([self.task4])
        self.assertEqualLists((self.task1, self.task2, self.task3), 
            self.events[0].values())

    def testAddRemovedTask(self):
        self.taskList.remove(self.task4)
        self.taskList.append(self.task4)
        self.assertEqual(2, len(self.events))

    def testAddRemovedTaskWithChild(self):
        self.taskList.remove(self.task2)
        self.taskList.append(self.task2)
        self.assertTaskList(self.originalList)
        self.assertEqual(2, len(self.events))
        self.failUnlessParentAndChild(self.task2, self.task3)
        self.failUnlessParentAndChild(self.task1, self.task2)

    def testAddRemovedTaskWithGrandchild(self):
        self.taskList.remove(self.task1)
        self.taskList.append(self.task1)
        self.assertTaskList(self.originalList)
        self.assertEqual(2, len(self.events))

    def testExtendWithRemovedTasks(self):
        self.taskList.remove(self.task1)
        self.taskList.remove(self.task4)
        self.taskList.extend([self.task1, self.task4])
        self.assertTaskList(self.originalList)
        self.failUnlessParentAndChild(self.task2, self.task3)
        self.failUnlessParentAndChild(self.task1, self.task2)

    def testRemoveTaskNotInList(self):
        task5 = task.Task()
        self.taskList.remove(task5)
        self.assertTaskList(self.originalList)

    def testRemoveTasks_ParentOnly(self):
        self.taskList.removeItems([self.task1])
        self.assertTaskList([self.task4])
        self.assertEqual(1, len(self.events))

    def testRemoveTasks_GrandchildOnly(self):
        self.taskList.removeItems([self.task3])
        self.assertTaskList([self.task1, self.task2, self.task4])
        self.failIfParentHasChild(self.task2, self.task3)
        self.assertEqual(1, len(self.events))

    def testRemoveTasks_ChildOnly(self):
        self.taskList.removeItems([self.task2])
        self.assertTaskList([self.task1, self.task4])
        self.failIfParentHasChild(self.task1, self.task2)
        self.failUnlessParentAndChild(self.task2, self.task3)
        self.assertEqual(1, len(self.events))

    def testRemoveTasks_ChildAndOtherTask(self):
        self.taskList.removeItems([self.task2, self.task4])
        self.assertTaskList([self.task1])
        self.failIfParentHasChild(self.task1, self.task2)
        self.failUnlessParentAndChild(self.task2, self.task3)
        self.assertEqual(1, len(self.events))


class TaskListTaskCategoriesTest(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.task = task.Task()
        self.task2 = task.Task()
        self.task2.addCategory('new')
        self.task.addCategory('test')
        
    def assertCategoriesEquals(self, expected):
        self.assertEqual(set(expected), self.taskList.categories())
        
    def testInitial(self):
        self.assertCategoriesEquals([])
        
    def testOneTaskWithoutCategories(self):
        self.taskList.append(task.Task())
        self.assertCategoriesEquals([])

    def testOneTaskWithOneCategory(self):
        self.taskList.append(self.task)
        self.assertCategoriesEquals(['test'])
        
    def testOneTaskWithTwoCategories(self):
        self.task.addCategory('second')
        self.taskList.append(self.task)
        self.assertCategoriesEquals(['test', 'second'])
        
    def testTwoTasksWithDifferentCategories(self):
        self.taskList.append(self.task)
        self.taskList.append(self.task2)
        self.assertCategoriesEquals(['test', 'new'])
        
    def testTwoTasksWithOverlappingCategories(self):
        self.taskList.append(self.task)
        self.task2.addCategory('test')
        self.taskList.append(self.task2)
        self.assertCategoriesEquals(['test', 'new'])

