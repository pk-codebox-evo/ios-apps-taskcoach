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
from unittests import dummy
from taskcoachlib import gui, config, persistence, operating_system
from taskcoachlib.domain import task
from taskcoachlib.thirdparty.pubsub import pub


class DummyPane(object):
    optionActive = False

    def __init__(self, window):
        self.window = window
        
    def IsToolbar(self):
        return False


class DummyEvent(object):
    def __init__(self, pane):
        self._pane = pane
    
    def Skip(self):
        pass

    def GetPane(self):
        return self._pane


class DummyChangeEvent(DummyEvent):
    pass
        

class DummyCloseEvent(DummyEvent):
    def __init__(self, window):
        super(DummyCloseEvent, self).__init__(DummyPane(window))

    
class ViewerContainerTest(test.wxTestCase):
    def setUp(self):
        super(ViewerContainerTest, self).setUp()
        self.events = 0
        task.Task.settings = self.settings = config.Settings(load=False)
        self.settings.set('view', 'viewerwithdummywidgetcount', '2', new=True)
        self.taskFile = persistence.TaskFile()
        self.mainWindow = gui.mainwindow.MainWindow(None, self.taskFile, 
                                                    self.settings)
        self.container = gui.viewer.ViewerContainer(self.mainWindow,
                                                    self.settings)
        self.viewer1 = self.createViewer('taskviewer1')
        self.container.addViewer(self.viewer1)
        self.viewer2 = self.createViewer('taskviewer2')
        self.container.addViewer(self.viewer2)

    def tearDown(self):
        if operating_system.isMac():
            self.mainWindow.OnQuit() # Stop power monitoring thread
        self.mainWindow._idleController.stop()
        pub.unsubscribe(self.onEvent, 'viewer.status')
        super(ViewerContainerTest, self).tearDown()
        self.taskFile.close()
        self.taskFile.stop()

    def createViewer(self, settingsSection):
        self.settings.add_section(settingsSection)
        return dummy.ViewerWithDummyWidget(self.mainWindow, self.taskFile, 
            self.settings, settingsSection=settingsSection)
            
    def onEvent(self):
        self.events += 1
    
    def testCreate(self):
        self.assertEqual(0, self.container.size())

    def testAddTask(self):
        self.taskFile.tasks().append(task.Task())
        self.assertEqual(1, self.container.size())

    def testDefaultActiveViewer(self):
        self.assertEqual(self.viewer1, self.container.activeViewer())
        
    def testChangePage_ChangesActiveViewer(self):
        self.container.activateViewer(self.viewer2)
        self.assertEqual(self.viewer2, self.container.activeViewer())

    def testChangePage_NotifiesObserversAboutNewActiveViewer(self):
        pub.subscribe(self.onEvent, 'viewer.status')
        self.container.onPageChanged(DummyChangeEvent(self.viewer2))
        self.failUnless(self.events > 0)
        
    def testCloseViewer_RemovesViewerFromContainer(self):
        self.container.onPageClosed(DummyCloseEvent(self.viewer1))
        self.assertEqual([self.viewer2], self.container.viewers)
        
    def testCloseViewer_ChangesActiveViewer(self):
        self.container.onPageChanged(DummyChangeEvent(self.viewer2))
        self.container.onPageClosed(DummyCloseEvent(self.viewer2))
        self.assertEqual(self.viewer1, self.container.activeViewer())
        
    def testCloseViewer_NotifiesObserversAboutNewActiveViewer(self):
        self.container.activateViewer(self.viewer2)
        pub.subscribe(self.onEvent, 'viewer.status')
        self.container.closeViewer(self.viewer2)
        self.failUnless(self.events > 0)

