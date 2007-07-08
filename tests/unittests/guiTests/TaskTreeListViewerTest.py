import test, gui, widgets, TaskTreeViewerTest, TaskListViewerTest
from unittests import dummy
from gui import render
from domain import task, date, effort, category, note

class TaskTreeListViewerUnderTest(gui.viewer.TaskTreeListViewer):
    def createWidgetWithColumns(self):
        widget = widgets.TreeListCtrl(self, self.columns(), self.getItemText,
            self.getItemImage, self.getItemAttr, self.getItemId,
            self.getRootIndices, self.getChildIndices,
            self.onSelect, dummy.DummyUICommand())
        widget.AssignImageList(self.createImageList())
        return widget

class TaskTreeListViewerTest(TaskTreeViewerTest.CommonTests,
                             TaskListViewerTest.CommonTests,
                             TaskTreeViewerTest.TaskTreeViewerTestCase):
    def setUp(self):
        super(TaskTreeListViewerTest, self).setUp()
        effortList = effort.EffortList(self.taskList)
        categories = category.CategoryList()
        viewerContainer = gui.viewercontainer.ViewerContainer(None, 
            self.settings, 'mainviewer')
        self.viewer = TaskTreeListViewerUnderTest(self.frame,
            self.taskList, gui.uicommand.UICommands(self.frame, None, 
                viewerContainer, self.settings, self.taskList, effortList, 
                categories, note.NoteContainer()), 
            self.settings, categories=categories)
          
    def testOneDayLeft(self):
        self.settings.set('view', 'timeleft', 'True')
        self.task.setDueDate(date.Tomorrow())
        self.taskList.append(self.task)
        firstItem, cookie = self.viewer.widget.GetFirstChild(self.viewer.widget.GetRootItem())
        self.assertEqual(render.daysLeft(self.task.timeLeft()), 
            self.viewer.widget.GetItemText(firstItem, 3))
        
    def testReverseSortOrderWithGrandchildren(self):
        self.viewer.sortBy('subject')
        self.viewer.setSortOrderAscending(True)
        child = task.Task(subject='child')
        self.task.addChild(child)
        grandchild = task.Task(subject='grandchild')
        child.addChild(grandchild)
        task2 = task.Task(subject='zzz')
        self.taskList.extend([self.task, task2])
        self.viewer.setSortOrderAscending(False)
        self.assertItems(task2, (self.task, 1), (child, 1), grandchild)
                
    def testReverseSortOrder(self):
        self.viewer.sortBy('subject')
        self.viewer.setSortOrderAscending(True)
        child = task.Task(subject='child')
        self.task.addChild(child)
        task2 = task.Task(subject='zzz')
        self.taskList.extend([self.task, task2])
        self.viewer.setSortOrderAscending(False)
        self.assertItems(task2, (self.task, 1), child)

    def testSortByDueDate(self):
        self.viewer.sortBy('subject')
        child = task.Task(subject='child')
        self.task.addChild(child)
        task2 = task.Task('zzz')
        child2 = task.Task('child 2')
        task2.addChild(child2)
        self.taskList.extend([self.task, task2])
        self.assertItems((self.task, 1), child, (task2, 1), child2)
        child2.setDueDate(date.Today())
        self.viewer.sortBy('dueDate')
        self.assertItems((task2, 1), child2, (self.task, 1), child)
        

