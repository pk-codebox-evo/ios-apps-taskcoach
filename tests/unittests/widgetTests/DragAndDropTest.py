'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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

import test, wx
from taskcoachlib.widgets import draganddrop


class TreeCtrlUnderTest(draganddrop.TreeCtrlDragAndDropMixin, wx.TreeCtrl):
    def GetMainWindow(self):
        return self


class DummyEvent(object):
    def __init__(self, item=None):
        self.item = item
        self.vetoed = self.allowed = False
        
    def GetItem(self):
        return self.item
    
    def Veto(self):
        self.vetoed = True
        
    def Allow(self):
        self.allowed = True
    
    
class TreeCtrlDragAndDropMixinTest(test.wxTestCase):
    def setUp(self):
        self.treeCtrl = TreeCtrlUnderTest(self.frame)
        rootItem = self.treeCtrl.AddRoot('root')
        self.item = self.treeCtrl.AppendItem(rootItem, 'item')
        
    def assertEventIsVetoed(self, event):
        self.failUnless(event.vetoed)
        self.failIf(event.allowed)
        
    def assertEventIsAllowed(self, event):
        self.failUnless(event.allowed)
        self.failIf(event.vetoed)
        
    def testEventIsVetoedWhenDragBeginsWithoutItem(self): 
        event = DummyEvent()
        self.treeCtrl.OnBeginDrag(event)
        self.assertEventIsVetoed(event)
        
    def testEventIsAllowedWhenDragBeginsWithItem(self):
        event = DummyEvent(self.item)
        self.treeCtrl.OnBeginDrag(event)
        self.assertEventIsAllowed(event)
        
    def testEventIsAllowedWhenDragBeginWithSelectedItem(self):
        self.treeCtrl.SelectItem(self.item)
        event = DummyEvent(self.item)
        self.treeCtrl.OnBeginDrag(event)
        self.assertEventIsAllowed(event)
