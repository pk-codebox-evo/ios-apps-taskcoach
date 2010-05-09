'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Frank Niessink <frank@niessink.com>

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
from taskcoachlib import gui, config, persistence
from taskcoachlib.domain import task

       
class TreeViewerTest(test.wxTestCase):
    def setUp(self):
        super(TreeViewerTest, self).setUp()
        task.Task.settings = self.settings = config.Settings(load=False)
        taskFile = persistence.TaskFile(self.settings)
        self.viewer = gui.viewer.TaskViewer(self.frame, taskFile,
            self.settings)
        self.expansionContext = self.viewer.settingsSection()
        self.parent = task.Task('parent')
        self.child = task.Task('child')
        self.parent.addChild(self.child)
        self.child.setParent(self.parent)
        taskFile.tasks().extend([self.parent, self.child])
        self.viewer.refresh()
        self.widget = self.viewer.widget

    def firstItem(self):
        root = self.widget.GetRootItem()
        return self.widget.GetFirstChild(root)[0]
                
    def testWidgetDisplayAllItems(self):
        self.assertEqual(2, self.viewer.widget.GetItemCount())
        
    def testExpand(self):
        self.widget.Expand(self.firstItem())
        self.failUnless(self.parent.isExpanded(context=self.expansionContext))
        
    def testCollapse(self):
        firstVisibleItem = self.firstItem()
        self.widget.Expand(firstVisibleItem)
        self.widget.Collapse(firstVisibleItem)
        self.failIf(self.parent.isExpanded(context=self.expansionContext))
        
    def testExpandall(self):
        self.viewer.expandAll()
        self.failUnless(self.parent.isExpanded(context=self.expansionContext))
