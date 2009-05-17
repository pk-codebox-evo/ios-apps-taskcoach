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

import wx, itemctrl
import wx.gizmos as gizmos
from wx.lib import customtreectrl as customtree
from taskcoachlib.thirdparty import treemixin, hypertreelist

        
class TreeMixin(treemixin.VirtualTree, treemixin.DragAndDrop):
    ''' Methods common to both TreeCtrl and TreeListCtrl. '''
        
    def OnGetChildrenCount(self, index):
        return self.getChildrenCount(index)
        
    def OnGetItemText(self, index, column=0):
        args = (index, column) if column else (index,)
        text = self.getItemText(*args)
        if text.count('\n') > 3:
            text = '\n'.join(text.split('\n')[:3] + ['...'])
        return text
        
    def OnGetItemExpanded(self, index):
        return self.getItemExpanded(index)

    def OnGetItemTooltipData(self, index, column=0):
        args = (index, column) if column else (index,)
        return self.getItemTooltipData(*args)

    def OnGetItemImage(self, index, which, column=0):
        args = (index, which, column) if column else (index, which)
        return self.getItemImage(*args)
        
    def OnGetItemTextColour(self, index):
        return self.getItemAttr(index).GetTextColour()
    
    def OnGetItemBackgroundColour(self, index):
        return self.getItemAttr(index).GetBackgroundColour()

    def bindEventHandlers(self, selectCommand, editCommand, dragAndDropCommand):
        self.selectCommand = selectCommand
        self.editCommand = editCommand
        self.dragAndDropCommand = dragAndDropCommand
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelect)
        self.Bind(wx.EVT_TREE_KEY_DOWN, self.onKeyDown)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onItemActivated)
        # We deal with double clicks ourselves, to prevent the default behaviour
        # of collapsing or expanding nodes on double click. 
        self.GetMainWindow().Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)
               
    def onKeyDown(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.editCommand(event)
        else:
            event.Skip()
         
    def OnDrop(self, dropItem, dragItem):
        if dropItem == self.GetRootItem():
            dropItemIndex = -1
        else:
            dropItemIndex = self.GetIndexOfItem(dropItem)
        self.dragAndDropCommand(dropItemIndex, self.GetIndexOfItem(dragItem))
                
    def onSelect(self, event):
        # Use CallAfter to prevent handling the select while items are 
        # being deleted:
        wx.CallAfter(self.selectCommand) 
        event.Skip()
                    
    def onDoubleClick(self, event):
        if not self.isClickablePartOfNodeClicked(event):
            self.onItemActivated(event)
        else:
            event.Skip(False)
        
    def onItemActivated(self, event):
        self.editCommand(event)
        event.Skip(False)
        
    def isClickablePartOfNodeClicked(self, event):
        ''' Return whether the user double clicked some part of the node that
            can also receive regular mouse clicks. '''
        return self.isCollapseExpandButtonClicked(event)
    
    def isCollapseExpandButtonClicked(self, event):
        item, flags, column = self.HitTest(event.GetPosition(), 
                                           alwaysReturnColumn=True)
        return flags & wx.TREE_HITTEST_ONITEMBUTTON
        
    def getStyle(self):
        return wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.TR_MULTIPLE | \
            wx.TR_HAS_BUTTONS

    def setItemGetters(self, getItemText, getItemTooltipData, getItemImage, getItemAttr,
            getChildrenCount, getItemExpanded):
        self.getItemText = getItemText
        self.getItemTooltipData = getItemTooltipData
        self.getItemImage = getItemImage
        self.getItemAttr = getItemAttr
        self.getChildrenCount = getChildrenCount
        self.getItemExpanded = getItemExpanded
    
    def GetItemCount(self):
        return self.GetCount()

    def refresh(self, count=0):
        self.RefreshItems()
                 
    def expandAllItems(self):
        self.ExpandAll()

    def collapseAllItems(self):
        for item in self.GetItemChildren():
            self.Collapse(item)
            
    def expandSelectedItems(self):
        for item in self.GetSelections():
            self.Expand(item)
            for child in self.GetItemChildren(item, recursively=True):
                self.Expand(child)
                
    def collapseSelectedItems(self):
        for item in self.GetSelections():
            self.Collapse(item)

    def curselection(self):
        return [self.GetIndexOfItem(item) for item in self.GetSelections()]
    
    def select(self, selection):
        for item in self.GetItemChildren(recursively=True):
            self.SelectItem(item, self.GetIndexOfItem(item) in selection)
        if self.GetSelections():
            self.SetCurrentItem(self.GetSelections()[0])
        
    def clearselection(self):
        self.UnselectAll()
        self.selectCommand()

    def selectall(self):
        if self.GetCount() > 0:
            self.SelectAll()
        self.selectCommand()

    def invertselection(self):
        for item in self.GetItemChildren(recursively=True):
            self.ToggleItemSelection(item)
        self.selectCommand()
        
    def isSelectionCollapsable(self):
        return self.isCollapsable(self.GetSelections())
    
    def isSelectionExpandable(self):
        return self.isExpandable(self.GetSelections())
    
    def isAnyItemCollapsable(self):
        return self.isCollapsable(self.GetItemChildren(recursively=True))
    
    def isAnyItemExpandable(self):
        return self.isExpandable(self.GetItemChildren(recursively=True))
    
    def isExpandable(self, items):
        for item in items:
            if self.ItemHasChildren(item) and not self.IsExpanded(item):
                return True
        return False
    
    def isCollapsable(self, items):
        for item in items:
            if self.ItemHasChildren(item) and self.IsExpanded(item):
                return True
        return False
    

class TreeListCtrl(itemctrl.CtrlWithItems, itemctrl.CtrlWithColumns, 
                   itemctrl.CtrlWithToolTip, TreeMixin, hypertreelist.HyperTreeList):
    # TreeListCtrl uses ALIGN_LEFT, ..., ListCtrl uses LIST_FORMAT_LEFT, ... for
    # specifying alignment of columns. This dictionary allows us to map from the 
    # ListCtrl constants to the TreeListCtrl constants:
    alignmentMap = {wx.LIST_FORMAT_LEFT: wx.ALIGN_LEFT, 
                    wx.LIST_FORMAT_CENTRE: wx.ALIGN_CENTRE,
                    wx.LIST_FORMAT_CENTER: wx.ALIGN_CENTER,
                    wx.LIST_FORMAT_RIGHT: wx.ALIGN_RIGHT}
    
    def __init__(self, parent, columns, getItemText, getItemTooltipData, getItemImage,
            getItemAttr, getChildrenCount, getItemExpanded, selectCommand, 
            editCommand, dragAndDropCommand,
            itemPopupMenu=None, columnPopupMenu=None, *args, **kwargs):    
        self.setItemGetters(getItemText, getItemTooltipData, getItemImage, getItemAttr,
            getChildrenCount, getItemExpanded)
        super(TreeListCtrl, self).__init__(parent, style=self.getStyle(), 
            columns=columns, resizeableColumn=0, itemPopupMenu=itemPopupMenu,
            columnPopupMenu=columnPopupMenu, *args, **kwargs)
        self.bindEventHandlers(selectCommand, editCommand, dragAndDropCommand)
        
    # Extend CtrlWithColumns with TreeListCtrl specific behaviour:
        
    def _setColumns(self, *args, **kwargs):
        super(TreeListCtrl, self)._setColumns(*args, **kwargs)
        self.SetMainColumn(0)
                        
    # Extend TreeMixin with TreeListCtrl specific behaviour:

    def getStyle(self):
        return super(TreeListCtrl, self).getStyle() | wx.TR_FULL_ROW_HIGHLIGHT \
            | wx.WANTS_CHARS | customtree.TR_HAS_VARIABLE_ROW_HEIGHT  
        
    def allItems(self):
        for rowIndex in range(self._count):
            try:
                yield rowIndex, self[rowIndex]
            except IndexError:
                pass # Item is hidden

    # Adapters to make the TreeListCtrl more like the ListCtrl
    
    def DeleteColumn(self, columnIndex):
        self.RemoveColumn(columnIndex)
        
    def InsertColumn(self, columnIndex, columnHeader, *args, **kwargs):
        format = self.alignmentMap[kwargs.pop('format', wx.LIST_FORMAT_LEFT)]
        if columnIndex == self.GetColumnCount():
            self.AddColumn(columnHeader, *args, **kwargs)
        else:
            super(TreeListCtrl, self).InsertColumn(columnIndex, columnHeader, 
                *args, **kwargs)
        # Put a default value in the new column otherwise GetItemText will fail
        for item in self.GetItemChildren(recursively=True):
            self.SetItemText(item, '', self.GetColumnCount()-1)
            self.SetItemImage(item, -1, column=self.GetColumnCount()-1)
        self.SetColumnAlignment(columnIndex, format)
    
    def GetCountPerPage(self):
        ''' ListCtrlAutoWidthMixin expects a GetCountPerPage() method,
            else it will throw an AttributeError. So for controls that have
            no such method (such as TreeListCtrl), we have to add it
            ourselves. '''
        count = 0
        item = self.GetFirstVisibleItem()
        while item:
            count += 1
            item = self.GetNextVisible(item)
        return count

    def onItemActivated(self, event):
        ''' Override TreeMixin default behavior to attach the column clicked on
            to the event so we can use it elsewhere. '''
        mousePosition = self.GetMainWindow().ScreenToClient(wx.GetMousePosition())
        item, flags, column = self.HitTest(mousePosition, alwaysReturnColumn=True)
        if item:
            # Only get the column name if the hittest returned an item,
            # otherwise the item was activated from the menu or by double 
            # clicking on a portion of the tree view not containing an item.
            column = max(0, column) # FIXME: Why can the column be -1?
            event.columnName = self._getColumn(column).name()
        super(TreeListCtrl, self).onItemActivated(event)


class CheckTreeCtrl(TreeListCtrl):
    def __init__(self, parent, columns, getItemText, getItemTooltipData, getItemImage,
            getItemAttr, getChildrenCount, getItemExpanded, getIsItemChecked,
            selectCommand, checkCommand, editCommand, dragAndDropCommand, 
            itemPopupMenu=None, *args, **kwargs):
        self.getIsItemChecked = getIsItemChecked
        super(CheckTreeCtrl, self).__init__(parent, columns, getItemText, 
            getItemTooltipData, getItemImage, getItemAttr, getChildrenCount, 
            getItemExpanded, selectCommand, editCommand, dragAndDropCommand, 
            itemPopupMenu, *args, **kwargs)
        self.Bind(hypertreelist.EVT_TREE_ITEM_CHECKED, checkCommand)
        
    def OnGetItemType(self, index):
        return 1
    
    def OnGetItemChecked(self, index):
        return self.getIsItemChecked(index)

    def isClickablePartOfNodeClicked(self, event):
        ''' Return whether the user double clicked some part of the node that
            can also receive regular mouse clicks. '''
        return super(CheckTreeCtrl, self).isClickablePartOfNodeClicked(event) or \
            self.isCheckBoxClicked(event)
            
    def isCheckBoxClicked(self, event):
        item, flags, column = self.HitTest(event.GetPosition(), 
                                           alwaysReturnColumn=True)
        return flags & customtree.TREE_HITTEST_ONITEMCHECKICON

    def onItemActivated(self, event):
        if self.isDoubleClicked(event):
            # Invoke super.onItemActivated to edit the item
            super(CheckTreeCtrl, self).onItemActivated(event)
        else:
            # Item is activated, let another event handler deal with the event 
            event.Skip()
            
    def isDoubleClicked(self, event):
        return hasattr(event, 'LeftDClick') and event.LeftDClick()
