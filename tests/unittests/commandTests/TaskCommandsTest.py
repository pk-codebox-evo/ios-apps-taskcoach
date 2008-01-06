import test, command, patterns, config
from unittests import asserts, dummy
from CommandTestCase import CommandTestCase
from domain import task, effort, date, category, attachment


class TaskCommandTestCase(CommandTestCase, asserts.Mixin):
    def setUp(self):
        self.list = self.taskList = task.TaskList()
        self.categories = category.CategoryList()
        self.category = category.Category('cat')
        self.categories.append(self.category)
        self.task1 = task.Task('task1')
        self.task2 = task.Task('task2')
        self.taskList.append(self.task1)
        self.originalList = [self.task1]
        self.taskRelationshipManager = \
            task.TaskRelationshipManager(taskList=self.taskList,
                                         settings=config.Settings(load=False))
        
    def tearDown(self):
        super(TaskCommandTestCase, self).tearDown()
        task.Clipboard().clear()

    def delete(self, items=None):
        if items == 'all':
            items = list(self.list)
        command.DeleteTaskCommand(self.list, items or []).do()
 
    def paste(self, items=None):
        if items:
            command.PasteIntoTaskCommand(self.taskList, items).do()
        else:
            super(TaskCommandTestCase, self).paste()

    def copy(self, items=None):
        command.CopyCommand(self.list, items or []).do()
        
    def markCompleted(self, tasks=None):
        command.MarkCompletedCommand(self.taskList, tasks or []).do()

    def newSubTask(self, tasks=None, markCompleted=False):
        tasks = tasks or []
        newSubTask = command.NewSubTaskCommand(self.taskList, tasks)
        if markCompleted:
            for subtask in newSubTask.items:
                subtask.setCompletionDate()
        newSubTask.do()

    def dragAndDrop(self, dropTarget, tasks=None):
        command.DragAndDropTaskCommand(self.taskList, tasks or [], 
                                       drop=dropTarget).do()
        
    def addAttachment(self, tasks=None, attachment=attachment.FileAttachment('attachment')):
        self.attachment = attachment
        addAttachmentCommand = command.AddAttachmentToTaskCommand(self.taskList,
            tasks or [], attachments=[attachment])
        addAttachmentCommand.do()


class CommandWithChildrenTestCase(TaskCommandTestCase):
    def setUp(self):
        super(CommandWithChildrenTestCase, self).setUp()
        self.parent = task.Task('parent')
        self.child = task.Task('child')
        self.parent.addChild(self.child)
        self.child2 = task.Task('child2')
        self.parent.addChild(self.child2)
        self.grandchild = task.Task('grandchild')
        self.child.addChild(self.grandchild)
        self.originalList.extend([self.parent, self.child, self.child2, self.grandchild])
        self.taskList.append(self.parent)
        

class CommandWithEffortTestCase(TaskCommandTestCase):
    def setUp(self):
        super(CommandWithEffortTestCase, self).setUp()
        self.list = self.effortList = effort.EffortList(self.taskList)
        self.effort1 = effort.Effort(self.task1)
        self.task1.addEffort(self.effort1)
        self.effort2 = effort.Effort(self.task2, 
            date.DateTime(2004,1,1), date.DateTime(2004,1,2))
        self.task2.addEffort(self.effort2)
        self.taskList.append(self.task2)
        self.originalEffortList = [self.effort1, self.effort2]


class DeleteCommandWithTasksTest(TaskCommandTestCase):
    def testDeleteAllTasks(self):
        self.taskList.append(self.task2)
        self.delete('all')
        self.assertDoUndoRedo(self.assertEmptyTaskList, 
            lambda: self.assertTaskList([self.task1, self.task2]))

    def testDeleteOneTask(self):
        self.taskList.append(self.task2)
        self.delete([self.task1])
        self.assertDoUndoRedo(lambda: self.assertTaskList([self.task2]),
            lambda: self.assertTaskList([self.task1, self.task2]))

    def testDeleteEmptyList(self):
        self.taskList.remove(self.task1)
        self.delete('all')
        self.assertDoUndoRedo(self.assertEmptyTaskList)

    def testDeleteEmptyList_NoCommandHistory(self):
        self.taskList.remove(self.task1)
        self.delete('all')
        self.assertDoUndoRedo(lambda: self.assertHistoryAndFuture([], []))

    def testDelete(self):
        self.delete('all')
        self.assertDoUndoRedo(self.assertEmptyTaskList,
            lambda: self.assertTaskList(self.originalList))
        
    def testDeleteTaskWithCategory(self):
        self.category.addCategorizable(self.task1)
        self.task1.addCategory(self.category)
        self.delete('all')
        self.assertDoUndoRedo(lambda: self.failIf(self.category.categorizables()), 
            lambda: self.assertEqual([self.task1], self.category.categorizables()))
        
    def testDeleteTaskWithTwoCategories(self):
        cat1 = category.Category('category 1')
        cat2 = category.Category('category 2')
        self.categories.extend([cat1, cat2])
        for cat in cat1, cat2:
            cat.addCategorizable(self.task1)
            self.task1.addCategory(cat)
        self.delete('all')
        self.assertDoUndoRedo(lambda: self.failIf(cat1.categorizables() or cat2.categorizables()), 
            lambda: self.failUnless([self.task1] == cat1.categorizables() == cat2.categorizables()))
        

class DeleteCommandWithTasksWithChildrenTest(CommandWithChildrenTestCase):
    def assertDeleteWorks(self):
        self.assertDoUndoRedo(self.assertParentAndAllChildrenDeleted,
            self.assertTaskListUnchanged)

    def assertParentAndAllChildrenDeleted(self):
        self.assertTaskList([self.task1])

    def assertTaskListUnchanged(self):
        self.assertTaskList(self.originalList)
        self.failUnlessParentAndChild(self.parent, self.child)
        self.failUnlessParentAndChild(self.child, self.grandchild)

    def testDeleteParent(self):
        self.delete([self.parent])
        self.assertDeleteWorks()

    def testDeleteParentAndChild(self):
        self.delete([self.parent, self.child])
        self.assertDeleteWorks()

    def testDeleteParentAndGrandchild(self):
        self.delete([self.parent, self.grandchild])
        self.assertDeleteWorks()

    def testDeleteLastNotCompletedChildMarksParentAsCompleted(self):
        self.markCompleted([self.child2])
        self.delete([self.child])
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.parent.completed()), 
            lambda: self.failIf(self.parent.completed()))
        
    def testDeleteParentAndChildWhenChildBelongsToCategory(self):
        self.category.addCategorizable(self.child)
        self.child.addCategory(self.category)
        self.delete([self.parent])
        self.assertDoUndoRedo(lambda: self.failIf(self.category.categorizables()), 
            lambda: self.assertEqual([self.child], self.category.categorizables()))

    def testDeleteParentAndChildWhenParentAndChildBelongToDifferentCategories(self):
        cat1 = category.Category('category 1')
        cat2 = category.Category('category 2')
        self.categories.extend([cat1, cat2])
        cat1.addCategorizable(self.child)
        self.child.addCategory(cat1)
        cat2.addCategorizable(self.parent)
        self.parent.addCategory(cat2)
        self.delete([self.parent])
        self.assertDoUndoRedo(lambda: self.failIf(cat1.categorizables() or cat2.categorizables()), 
            lambda: self.failUnless([self.child] == cat1.categorizables() and \
                                    [self.parent] == cat2.categorizables()))

    def testDeleteParentAndChildWhenParentAndChildBelongToSameCategory(self):
        for task in self.parent, self.child:
            self.category.addCategorizable(task)
            task.addCategory(self.category)
        self.delete([self.parent])
        self.assertDoUndoRedo(lambda: self.failIf(self.category.categorizables()), 
            lambda: self.assertEqualLists([self.parent, self.child], self.category.categorizables()))


class DeleteCommandWithTasksWithEffortTest(CommandWithEffortTestCase):
    def testDeleteActiveTask(self):
        self.list = self.taskList
        self.delete([self.task1])
        self.assertDoUndoRedo(
            lambda: self.assertEqual(1, len(self.effortList)),
            lambda: self.assertEqual(2, len(self.effortList)))


class NewTaskCommandTest(TaskCommandTestCase):
    def new(self):
        newTaskCommand = command.NewTaskCommand(self.taskList)
        newTask = newTaskCommand.items[0]
        newTaskCommand.do()
        return newTask
    
    def testNewTask(self):
        newTask = self.new()
        self.assertDoUndoRedo(
            lambda: self.assertTaskList([self.task1, newTask]),
            lambda: self.assertTaskList(self.originalList))


class NewSubTaskCommandTest(TaskCommandTestCase):

    def testNewSubTask_WithoutSelection(self):
        self.newSubTask()
        self.assertDoUndoRedo(lambda: self.assertTaskList(self.originalList))

    def testNewSubTask(self):
        self.newSubTask([self.task1])
        newSubTask = self.task1.children()[0]
        self.assertDoUndoRedo(lambda: self.assertNewSubTask(newSubTask),
            lambda: self.assertTaskList(self.originalList))

    def assertNewSubTask(self, newSubTask):
        self.assertEqual(len(self.originalList)+1, len(self.taskList))
        self.assertEqualLists([newSubTask], self.task1.children())

    def testNewSubTask_MarksParentAsNotCompleted(self):
        self.markCompleted([self.task1])
        self.newSubTask([self.task1])
        self.assertDoUndoRedo(lambda: self.failIf(self.task1.completed()),
            lambda: self.failUnless(self.task1.completed()))

    def testNewSubTask_MarksGrandParentAsNotCompleted(self):
        self.newSubTask([self.task1])
        self.markCompleted([self.task1])
        self.newSubTask([self.task1.children()[0]])
        self.assertDoUndoRedo(lambda: self.failIf(self.task1.completed()),
            lambda: self.failUnless(self.task1.completed()))

    def testNewCompletedSubTask(self):
        self.newSubTask([self.task1], markCompleted=True)
        self.assertDoUndoRedo(lambda: self.failUnless(self.task1.completed()),
            lambda: self.failIf(self.task1.completed()))


class EditTaskCommandTest(TaskCommandTestCase):
    def edit(self, tasks=None):
        tasks = tasks or []
        editcommand = command.EditTaskCommand(self.taskList, tasks)
        for task in tasks:
            task.setSubject('New subject')
            task.setDescription('New description')
            task.setBudget(date.TimeDelta(hours=1))
            task.setCompletionDate()
            att = attachment.FileAttachment('attachment')
            if att in task.attachments():
                task.removeAttachments(att)
            else:
                task.addAttachments(att)
            if self.category in task.categories():
                task.removeCategory(self.category)
            else:
                task.addCategory(self.category)
        editcommand.do()

    def testEditTask(self):
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.assertEqual('New subject', self.task1.subject()),
            lambda: self.assertEqual('task1', self.task1.subject()))

    def testEditTask_MarkCompleted(self):
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.task1.completed()),
            lambda: self.failIf(self.task1.completed()))

    def testEditTaskWithChildren_MarkCompleted(self):
        self.newSubTask([self.task1])
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.task1.children()[0].completed()),
            lambda: self.failIf(self.task1.children()[0].completed()))

    def testEditDescription(self):
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.assertEqual('New description', self.task1.description()),
            lambda: self.assertEqual('', self.task1.description()))

    def testEditBudget(self):
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.assertEqual(date.TimeDelta(hours=1), self.task1.budget()),
            lambda: self.assertEqual(date.TimeDelta(), self.task1.budget()))

    def testAddAttachment(self):
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.assertEqual([attachment.FileAttachment('attachment')], self.task1.attachments()),
            lambda: self.assertEqual([], self.task1.attachments()))
            
    def testRemoveAttachment(self):
        self.task1.addAttachments(attachment.FileAttachment('attachment'))
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.assertEqual([], self.task1.attachments()),
            lambda: self.assertEqual([attachment.FileAttachment('attachment')], self.task1.attachments()))
        
    def testAddCategory(self):
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.assertEqual(set([self.category]), self.task1.categories()),
            lambda: self.failIf(self.task1.categories()))

    def testAddCategory_AffectsCategory(self):
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.assertEqual([self.task1], self.category.categorizables()),
            lambda: self.failIf(self.category.categorizables()))
        
    def testRemoveCategory(self):
        self.task1.addCategory(self.category)
        self.category.addCategorizable(self.task1)
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.failIf(self.task1.categories()),
            lambda: self.assertEqual(set([self.category]), self.task1.categories()))
        
    def testRemoveCategory_AffectsCategory(self):
        self.task1.addCategory(self.category)
        self.category.addCategorizable(self.task1)
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.failIf(self.category.categorizables()),
            lambda: self.assertEqual([self.task1], self.category.categorizables()))


class MarkCompletedCommandTest(CommandWithChildrenTestCase):
    def testMarkCompleted(self):
        self.markCompleted([self.task1])
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.task1.completed()),
            lambda: self.failIf(self.task1.completed()))

    def testMarkCompleted_TaskAlreadyCompleted(self):
        self.task1.setCompletionDate()
        self.markCompleted([self.task1])
        self.assertDoUndoRedo(
            lambda: self.failIf(self.task1.completed()),
            lambda: self.failUnless(self.task1.completed()))

    def testMarkCompletedParent(self):
        self.markCompleted([self.parent])
        self.assertDoUndoRedo(lambda: self.failUnless(self.child.completed()
            and self.child2.completed() and self.grandchild.completed()),
            lambda: self.failIf(self.child.completed() or
            self.child2.completed() or self.grandchild.completed()))

    def testMarkCompletedParent_WhenChildAlreadyCompleted(self):
        self.markCompleted([self.child])
        self.markCompleted([self.parent])
        self.assertDoUndoRedo(lambda: self.failUnless(self.child.completed()))

    def testMarkCompletedGrandChild(self):
        self.markCompleted([self.grandchild])
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.child.completed() and 
                not self.parent.completed()), 
            lambda: self.failIf(self.child.completed() or 
                self.parent.completed()))

    def testMarkCompletedStopsEffortTracking(self):
        self.task1.addEffort(effort.Effort(self.task1))
        self.markCompleted([self.task1])
        self.assertDoUndoRedo(lambda: self.failIf(self.task1.isBeingTracked()), 
            lambda: self.failUnless(self.task1.isBeingTracked()))
            
    def testMarkCompletedChildDoesNotStopEffortTrackingOfParent(self):
        self.parent.addEffort(effort.Effort(self.parent))
        self.markCompleted([self.child])
        self.assertDoUndoRedo(lambda: self.failUnless(self.parent.isBeingTracked()))

        
class DragAndDropTaskCommandTest(CommandWithChildrenTestCase):
    def testCannotDropOnParent(self):
        self.dragAndDrop([self.parent], [self.child])
        self.failIf(patterns.CommandHistory().hasHistory())
        
    def testCannotDropOnChild(self):
        self.dragAndDrop([self.child], [self.parent])
        self.failIf(patterns.CommandHistory().hasHistory())
        
    def testCannotDropOnGrandchild(self):
        self.dragAndDrop([self.grandchild], [self.parent])
        self.failIf(patterns.CommandHistory().hasHistory())

    def testDropAsRootTask(self):
        self.dragAndDrop([], [self.grandchild])
        self.assertDoUndoRedo(lambda: self.assertEqual(None, 
            self.grandchild.parent()), lambda:
            self.assertEqual(self.child, self.grandchild.parent()))
        

class AddAttachmentToTaskCommandTest(TaskCommandTestCase):
    def testAddOneAttachmentToOneTask(self):
        self.addAttachment([self.task1])
        self.assertDoUndoRedo(lambda: self.assertEqual([self.attachment], 
            self.task1.attachments()), lambda: self.assertEqual([], 
            self.task1.attachments()))
            
    def testAddOneAttachmentToTwoTasks(self):
        self.addAttachment([self.task1, self.task2])
        self.assertDoUndoRedo(lambda: self.failUnless([self.attachment] == \
            self.task1.attachments() == self.task2.attachments()), 
            lambda: self.failUnless([] == self.task1.attachments() == \
            self.task2.attachments()))
    

class PriorityCommandTestCase(TaskCommandTestCase):
    def setUp(self):
        super(PriorityCommandTestCase, self).setUp()
        self.taskList.append(self.task2)

    def assertDoUndoRedo(self, priority1do, priority2do, priority1undo, priority2undo):
        super(PriorityCommandTestCase, self).assertDoUndoRedo(
            lambda: self.failUnless(priority1do == self.task1.priority() and
                    priority2do == self.task2.priority()),
            lambda: self.failUnless(priority1undo == self.task1.priority() and
                    priority2undo == self.task2.priority()))

        
class MaxPriorityCommandTest(PriorityCommandTestCase):
    def maxPriority(self, tasks=None):
        command.MaxPriorityCommand(self.taskList, tasks or []).do()        
        
    def testEmptySelection(self):
        self.maxPriority()
        self.assertDoUndoRedo(0, 0, 0, 0)
        
    def testOneTaskWhenBothTasksHaveSamePriority(self):
        self.maxPriority([self.task1])
        self.assertDoUndoRedo(1, 0, 0, 0)
        
    def testBothTasksWhenBothTasksHaveSamePriority(self):
        self.maxPriority([self.task1, self.task2])
        self.assertDoUndoRedo(1, 1, 0, 0)
        
    def testMakeLowestPriorityTheMaxPriority(self):
        self.task2.setPriority(2)
        self.maxPriority([self.task1])
        self.assertDoUndoRedo(3, 2, 0, 2)


class MinPriorityCommandTest(PriorityCommandTestCase):        
    def minPriority(self, tasks=None):
        command.MinPriorityCommand(self.taskList, tasks or []).do()        

    def testEmptySelection(self):
        self.minPriority()
        self.assertDoUndoRedo(0, 0, 0, 0)
        
    def testOneTaskWhenBothTasksHaveSamePriority(self):
        self.minPriority([self.task1])
        self.assertDoUndoRedo(-1, 0, 0, 0)
        
    def testBothTasksWhenBothTasksHaveSamePriority(self):
        self.minPriority([self.task1, self.task2])
        self.assertDoUndoRedo(-1, -1, 0, 0)
        
    def testMakeLowestPriorityTheMaxPriority(self):
        self.task2.setPriority(-2)
        self.minPriority([self.task1])
        self.assertDoUndoRedo(-3, -2, 0, -2)


class IncreasePriorityCommandTest(PriorityCommandTestCase):
    def incPriority(self, tasks=None):
        command.IncPriorityCommand(self.taskList, tasks or []).do()
        
    def testEmptySelection(self):
        self.incPriority()
        self.assertDoUndoRedo(0, 0, 0, 0)
        
    def testOneTaskWhenBothTasksHaveSamePriority(self):
        self.incPriority([self.task1])
        self.assertDoUndoRedo(1, 0, 0, 0)
        
    def testBothTasksWhenBothTasksHaveSamePriority(self):
        self.incPriority([self.task1, self.task2])
        self.assertDoUndoRedo(1, 1, 0, 0)
        
    def testIncLowestPriority(self):
        self.task2.setPriority(-2)
        self.incPriority([self.task2])
        self.assertDoUndoRedo(0, -1, 0, -2)
    

class DecreasePriorityCommandTest(PriorityCommandTestCase):
    def decPriority(self, tasks=None):
        command.DecPriorityCommand(self.taskList, tasks or []).do()
        
    def testEmptySelection(self):
        self.decPriority()
        self.assertDoUndoRedo(0, 0, 0, 0)
        
    def testOneTaskWhenBothTasksHaveSamePriority(self):
        self.decPriority([self.task1])
        self.assertDoUndoRedo(-1, 0, 0, 0)
        
    def testBothTasksWhenBothTasksHaveSamePriority(self):
        self.decPriority([self.task1, self.task2])
        self.assertDoUndoRedo(-1, -1, 0, 0)
        
    def testDecLowestPriority(self):
        self.task2.setPriority(-2)
        self.decPriority([self.task2])
        self.assertDoUndoRedo(0, -3, 0, -2)
    
