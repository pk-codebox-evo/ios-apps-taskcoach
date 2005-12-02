import test, task, gui, wx, dummy, effort, config


class ViewerContainerTest(test.wxTestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.settings = config.Settings(load=False)
        self.container = gui.viewercontainer.ViewerNotebook(self.frame, 
            self.settings, 'mainviewer')
        self.container.addViewer(dummy.ViewerWithDummyWidget(self.container,
            self.taskList, dummy.DummyUICommands(), self.settings), 'Dummy')

    def testCreate(self):
        self.assertEqual(0, self.container.size())

    def testAddTask(self):
        self.taskList.append(task.Task())
        self.assertEqual(1, self.container.size())
