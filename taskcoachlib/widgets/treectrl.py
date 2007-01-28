import wx, itemctrl, thirdparty
import wx.gizmos as gizmos
import wx.lib.customtreectrl as customtree

        
class TreeMixin(object):
    ''' Methods common to both TreeCtrl and TreeListCtrl. '''
    
    def bindEventHandlers(self, selectCommand, editCommand, dragAndDropCommand):
        self.selectCommand = selectCommand
        self.editCommand = editCommand
        self.dragAndDropCommand = dragAndDropCommand
        self.__settingFocus = False
        self.__collapsing = False
        self.Bind(wx.EVT_SET_FOCUS, self.onSetFocus)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelect)
        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.onSelectionChanging)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.onExpand)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSING, self.onCollapse)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, editCommand)
        # We deal with double clicks ourselves, to prevent the default behaviour
        # of collapsing or expanding nodes on double click. 
        self.Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)
        # prepare for dragging of tree items
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.onBeginDrag)
        
    def onBeginDrag(self, event):
        self.dragItem = self.__getDraggedItem()
        if self.dragItem and self.dragAndDropCommand:
            event.Allow()
            self.GetMainWindow().Bind(wx.EVT_MOTION, self.onDragging)
            self.Bind(wx.EVT_TREE_END_DRAG, self.onEndDrag)
            self.__setCursorToDragging()
        else:
            event.Veto()
            
    def __getDraggedItem(self):
        selectedItems = self.GetSelections()
        if selectedItems:
            return selectedItems[0]
        else:
            return None
        
    def __setCursorToDragging(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        
    def __setCursorToDroppingImpossible(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_NO_ENTRY))
        
    def __resetCursor(self):
        self.SetCursor(wx.STANDARD_CURSOR)
        
    def draggedItems(self):
        return [self.index(self.dragItem)]
            
    def onEndDrag(self, event):
        self.GetMainWindow().Unbind(wx.EVT_MOTION)
        self.Unbind(wx.EVT_TREE_END_DRAG)
        self.__resetCursor()
        if self._isValidDropTarget(event.GetItem()):
            self.dragAndDropCommand(event)

    def onDragging(self, event):
        if not event.Dragging():
            self.GetMainWindow().Unbind(wx.EVT_MOTION)
            self.Unbind(wx.EVT_TREE_END_DRAG)
            self.__resetCursor()
            return
        item, flags, column = self.HitTest(wx.Point(event.GetX(), event.GetY()))
        if self._isValidDropTarget(item):
            self.__setCursorToDragging()
        else:
            self.__setCursorToDroppingImpossible()
        if flags & wx.TREE_HITTEST_ONITEMBUTTON:
            self.Expand(item)
        elif flags & (wx.TREE_HITTEST_NOWHERE | wx.TREE_HITTEST_BELOW | 
                      wx.TREE_HITTEST_ABOVE | wx.TREE_HITTEST_TOLEFT |
                      wx.TREE_HITTEST_TORIGHT):
            self.UnselectAll()
        selections = self.GetSelections()
        if item:
            if selections != [item]:
                self.UnselectAll()
                self.SelectItem(item)
        else:
            self.UnselectAll()
        event.Skip()
        
    def _isValidDropTarget(self, dropTarget):
        if dropTarget: 
            return self.dragItem != dropTarget and \
                self.GetItemParent(self.dragItem) != dropTarget and \
                dropTarget not in self.getChildren(self.dragItem,
                recursively=True)
        else:
            return True
            
    def onSetFocus(self, event):
        # When the TreeCtrl gets focus sometimes the selection is changed.
        # We want to prevent that from happening, so we need to keep track
        # of the fact that we have just received a EVT_SET_FOCUS
        self.__settingFocus = True
        event.Skip()

    def onSelectionChanging(self, event):
        if self._refreshing or self.__settingFocus:
            self.__settingFocus = False
            event.Veto()
        else:
            event.Skip()
        
    def onSelect(self, event):
        if not self._refreshing:
            self.selectCommand()
        event.Skip()
                    
    def onExpand(self, event):
        item = event.GetItem()
        # Apparently, this event handler is called for the root item somehow. This
        # only happens with the TreeListCtrl, not with the TreeCtrl.
        if item == self.GetRootItem(): 
            return
        itemIndex = self.index(item)
        self.addItemsRecursively(item, self.getChildIndices(itemIndex))
        
    def onCollapse(self, event):
        if self.__collapsing:
            event.Veto()
        else:
            self.__collapsing = True
            item = event.GetItem()
            itemIndex = self.index(item)
            self.CollapseAndReset(item)
            if self.getChildIndices(itemIndex) and not self.ItemHasChildren(item):
                self.SetItemHasChildren(item)
            self.__collapsing = False

    def onDoubleClick(self, event):
        if not self.isCollapseExpandButtonClicked(event):
            self.editCommand(event)
        event.Skip(False)

    def isCollapseExpandButtonClicked(self, event):
        item, flags, column = self.HitTest(event.GetPosition())
        return flags & wx.TREE_HITTEST_ONITEMBUTTON
    
    def __getitem__(self, index):
        ''' Return the item at position index in the *model* which is not
            necessarily the same index as in the Tree(List)Ctrl. '''
        for item in self.getChildren(recursively=True):
            if self.index(item) == index:
                return item
        raise IndexError
        
    def GetItem(self, index):
        ''' Return the item at position index in the *Tree(List)Ctrl* which is
            not necessarily the same index as in the model. This method also 
            mimics the ListCtrl API. '''
        for cursorIndex, item in enumerate(self.getChildren(recursively=True)):
            if index == cursorIndex:
                return item
        raise IndexError
        
    def getStyle(self):
        return wx.TR_HIDE_ROOT | wx.TR_MULTIPLE | wx.TR_HAS_BUTTONS

    def setItemGetters(self, getItemText, getItemImage, getItemAttr,
            getItemId, getRootIndices, getChildIndices):
        self.getItemText = getItemText
        self.getItemImage = getItemImage
        self.getItemAttr = getItemAttr
        self.getItemId = getItemId
        self.getRootIndices = getRootIndices
        self.getChildIndices = getChildIndices
    
    def GetItemCount(self):
        return self.GetCount()

    def refreshItem(self, index):
        try:
            self.renderNode(self[index], index)
        except IndexError:
            pass # Hidden item

    def refresh(self, count=0):
        self._count = count
        self._refreshing = True
        self._validItems = []
        self.itemsToExpandOrCollapse = {}
        self.itemsToSelect = []
        self.Freeze()
        rootItem = self.__getOrCreateRootItem()
        rootIndices = self.getRootIndices()
        self.addItemsRecursively(rootItem, rootIndices)
        self.deleteUnusedItems()
        self.restoreItemState()
        self.Thaw()
        self._refreshing = False

    def __getOrCreateRootItem(self):
        rootItem = self.GetRootItem()
        if not rootItem:
            rootItem = self.AddRoot('root')
        return rootItem
        
    def addItemsRecursively(self, parent, indices):
        for itemChildIndex, index in enumerate(indices):
            item = self.appendItem(parent, index, itemChildIndex)
            if self.IsExpanded(item) or \
                    self.itemsToExpandOrCollapse.get(item, False):
                self.addItemsRecursively(item, self.getChildIndices(index))
            elif self.getChildIndices(index) and not self.ItemHasChildren(item):
                self.SetItemHasChildren(item)
        
    def appendItem(self, parent, index, itemChildIndex):
        itemId = self.getItemId(index)
        oldItem = self.findItem(itemId)
        if oldItem and self.itemUnchanged(oldItem, index, itemChildIndex) and \
                self.GetItemParent(oldItem) == parent:
            newItem = oldItem
            render = False
        else:
            insertAfterChild = self.findInsertionPoint(parent)
            if insertAfterChild:
                newItem = self.InsertItem(parent, insertAfterChild, 
                    self.getItemText(index))
            else:
                newItem = self.PrependItem(parent, self.getItemText(index))
            render = True
            if not oldItem and parent != self.GetRootItem():
                self.itemsToExpandOrCollapse[parent] = True
            if oldItem:
                if self.IsSelected(oldItem):            
                    self.itemsToSelect.append(newItem)
                self.itemsToExpandOrCollapse[newItem] = self.IsExpanded(oldItem)
        if oldItem and len(self.getChildIndices(index)) > self.GetPyData(oldItem)[2]:
            self.itemsToExpandOrCollapse[newItem] = True
        self.SetPyData(newItem, self.__createPyData(index, itemChildIndex))
        self._validItems.append(newItem)
        if render:
            self.renderNode(newItem, index)
        return newItem
       
    def findItem(self, itemId):
        for child in self.getChildren(recursively=True):
            if self.GetPyData(child)[1] == itemId:
                return child
        return None        

    def getChildren(self, parent=None, recursively=False):
        if parent is None:
            parent = self.GetRootItem()
        child, cookie = self.GetFirstChild(parent)
        while child:
            yield (child)
            if recursively:
                for grandchild in self.getChildren(child, recursively):
                    yield (grandchild)
            child, cookie = self.GetNextChild(parent, cookie)
        
    def findInsertionPoint(self, parent):
        insertAfterChild = None
        for child in self.getChildren(parent):
            if child in self._validItems:
                insertAfterChild = child
        return insertAfterChild
            
    def renderNode(self, node, index):
        normalImageIndex = self.getItemImage(index)
        self.SetItemImage(node, normalImageIndex, wx.TreeItemIcon_Normal)
        if self.getChildIndices(index):
            expandedImageIndex = self.getItemImage(index, expanded=True)
            self.SetItemImage(node, expandedImageIndex, wx.TreeItemIcon_Expanded)
        self.SetItemTextColour(node, self.getItemAttr(index).GetTextColour())
        self.SetItemText(node, self.getItemText(index))

    def __createPyData(self, index, itemChildIndex):
        return (index, self.getItemId(index), len(self.getChildIndices(index)),
            self.getItemImage(index), self.getItemText(index),
            self.getItemAttr(index), itemChildIndex)

    def deleteUnusedItems(self):
        unusedItems = []
        for item in self.getChildren(recursively=True):
            if item not in self._validItems:
                unusedItems.append(item)
        for item in unusedItems:
            # Make sure we don't try to delete an item whose parent
            # has already been deleted; that would crash the TreeListCtrl.
            # The TreeCtrl is more forgiving, but since this code has to work
            # for both we have to be careful.
            if not self.anyAncestorInList(item, unusedItems):
                self.Delete(item)
        
    def anyAncestorInList(self, item, list):
        parent = self.GetItemParent(item)
        if parent == self.GetRootItem():
            return False
        else:
            return parent in list or self.anyAncestorInList(parent, list)
        
    def restoreItemState(self):
        for item, expand in self.itemsToExpandOrCollapse.items():
            if expand:
                self.Expand(item)
            else:
                self.CollapseAndReset(item)
        wx.CallAfter(self.restoreSelection)

    def restoreSelection(self):
        self.UnselectAll()
        for item in self.itemsToSelect:
            if item:
                self.SelectItem(item)

    def itemUnchanged(self, item, index, itemChildIndex):
        oldIndex, oldId, oldChildrenCount, oldImage, oldText, \
            oldAttr, oldChildIndex = self.GetPyData(item)
        hadChildren = bool(oldChildrenCount)
        hasChildren = bool(self.getChildIndices(index))
        return itemChildIndex == oldChildIndex and \
            hasChildren == hadChildren and \
            self.getItemImage(index) == oldImage and \
            self.getItemText(index) == oldText and \
            self.getItemAttr(index).GetTextColour() == oldAttr.GetTextColour()

    def expandAllItems(self):
        for item in self.getChildren(recursively=True):
            self.Expand(item)

    def collapseAllItems(self):
        for item in self.getChildren():
            self.CollapseAndReset(item)
            
    def expandSelectedItems(self):
        for item in self.GetSelections():
            self.Expand(item)
            for child in self.getChildren(item, recursively=True):
                self.Expand(child)
                
    def collapseSelectedItems(self):
        for item in self.GetSelections():
            self.CollapseAndReset(item)

    def index(self, item):
        return self.GetPyData(item)[0]

    def curselection(self):
        return [self.index(item) for item in self.GetSelections()]

    def clearselection(self):
        self.UnselectAll()
        self.selectCommand()

    def selectall(self):
        if self.GetCount() > 0:
            self.SelectAll()
        self.selectCommand()

    def invertselection(self):
        for item in self.getChildren(recursively=True):
            self.ToggleItemSelection(item)
        self.selectCommand()
        
    def isSelectionCollapsable(self):
        return self.isCollapsable(self.GetSelections())
    
    def isSelectionExpandable(self):
        return self.isExpandable(self.GetSelections())
    
    def isAnyItemCollapsable(self):
        return self.isCollapsable(self.getChildren(recursively=True))
    
    def isAnyItemExpandable(self):
        return self.isExpandable(self.getChildren(recursively=True))
    
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


class TreeCtrl(itemctrl.CtrlWithItems, TreeMixin, wx.TreeCtrl):
    def __init__(self, parent, getItemText, getItemImage, getItemAttr,
            getItemId, getRootIndices,
            getChildIndices, selectCommand, editCommand, dragAndDropCommand,
            itemPopupMenu=None, *args, **kwargs):
        super(TreeCtrl, self).__init__(parent, style=self.getStyle(), 
            itemPopupMenu=itemPopupMenu, *args, **kwargs)
        self.bindEventHandlers(selectCommand, editCommand, dragAndDropCommand)
        self.setItemGetters(getItemText, getItemImage, getItemAttr,
            getItemId, getRootIndices, getChildIndices)
        self.refresh()
        
    def getStyle(self):
        # Adding wx.TR_LINES_AT_ROOT is necessary to make the buttons 
        # (wx.TR_HAS_BUTTONS) appear. I think this is a bug in wx.TreeCtrl.
        return super(TreeCtrl, self).getStyle() | wx.TR_LINES_AT_ROOT

    # Adapters to make the TreeCtrl API more like the TreeListCtrl API:
        
    def SelectAll(self):
        for item in self.getChildren(recursively=True):
            self.SelectItem(item)

    def HitTest(self, *args, **kwargs):
        item, flags = super(TreeCtrl, self).HitTest(*args, **kwargs)
        column = 0
        return item, flags, column
    

class CustomTreeCtrl(itemctrl.CtrlWithItems, customtree.CustomTreeCtrl, TreeMixin): 
    def __init__(self, parent, getItemText, getItemImage, getItemAttr,
            getItemId, getRootIndices, getChildIndices, selectCommand,
            editCommand, dragAndDropCommand, 
            itemPopupMenu=None, *args, **kwargs):
        super(CustomTreeCtrl, self).__init__(parent, ctstyle=self.getStyle(), 
            itemPopupMenu=itemPopupMenu, *args, **kwargs)
        self.bindEventHandlers(selectCommand, editCommand, dragAndDropCommand)
        self.setItemGetters(getItemText, getItemImage, getItemAttr,
            getItemId, getRootIndices, getChildIndices)
        self.refresh()
            
    # Adapters to make the CustomTreeCtrl API more like the TreeListCtrl API:
        
    def SelectAll(self):
        for item in self.getChildren(recursively=True):
            self.SelectItem(item)

    def HitTest(self, *args, **kwargs):
        item, flags = super(CustomTreeCtrl, self).HitTest(*args, **kwargs)
        column = 0
        return item, flags, column
    
    def GetItemCount(self):
        if self.GetWindowStyle() & wx.TR_HIDE_ROOT:
            hiddenRoot = 1
        else:
            hiddenRoot = 0
        return super(CustomTreeCtrl, self).GetItemCount() - hiddenRoot


class CheckTreeCtrl(CustomTreeCtrl):
    def __init__(self, parent, getItemText, getItemImage, getItemAttr,
            getItemId, getRootIndices, getChildIndices, getIsItemChecked,
            selectCommand, checkCommand, editCommand, dragAndDropCommand, 
            itemPopupMenu=None, *args, **kwargs):
        self.getIsItemChecked = getIsItemChecked
        super(CheckTreeCtrl, self).__init__(parent, getItemText, getItemImage, 
            getItemAttr, getItemId, getRootIndices, getChildIndices, 
            selectCommand, editCommand, dragAndDropCommand, 
            itemPopupMenu, *args, **kwargs)
        self.Bind(customtree.EVT_TREE_ITEM_CHECKED, checkCommand)
        
    def renderNode(self, node, index):
        super(CheckTreeCtrl, self).renderNode(node, index)
        shouldItemBeChecked = self.getIsItemChecked(index)
        if shouldItemBeChecked != node.IsChecked():
            self.CheckItem(node, checked=shouldItemBeChecked)
        
    def itemUnchanged(self, item, index, itemChildIndex):
        return super(CheckTreeCtrl, self).itemUnchanged(item, index, itemChildIndex) \
            and self.getIsItemChecked(index) == item.IsChecked()
        
    def getStyle(self):
        return super(CheckTreeCtrl, self).getStyle() | \
            customtree.TR_AUTO_CHECK_CHILD
            
    def InsertItem(self, *args, **kwargs):
        kwargs['ct_type'] = 1
        return super(CheckTreeCtrl, self).InsertItem(*args, **kwargs)

    def PrependItem(self, *args, **kwargs):
        kwargs['ct_type'] = 1
        return super(CheckTreeCtrl, self).PrependItem(*args, **kwargs)
        

class TreeListCtrl(itemctrl.CtrlWithItems, itemctrl.CtrlWithColumns, TreeMixin, gizmos.TreeListCtrl):
    # TreeListCtrl uses ALIGN_LEFT, ..., ListCtrl uses LIST_FORMAT_LEFT, ... for
    # specifying alignment of columns. This dictionary allows us to map from the 
    # ListCtrl constants to the TreeListCtrl constants:
    alignmentMap = {wx.LIST_FORMAT_LEFT: wx.ALIGN_LEFT, 
                    wx.LIST_FORMAT_CENTRE: wx.ALIGN_CENTRE,
                    wx.LIST_FORMAT_CENTER: wx.ALIGN_CENTER,
                    wx.LIST_FORMAT_RIGHT: wx.ALIGN_RIGHT}
    
    def __init__(self, parent, columns, getItemText, getItemImage, getItemAttr,
            getItemId, getRootIndices, getChildIndices, selectCommand, 
            editCommand, dragAndDropCommand,
            itemPopupMenu=None, columnPopupMenu=None, *args, **kwargs):
        self._count = 0 # Need to set this early because InsertColumn invokes refreshColumn
        super(TreeListCtrl, self).__init__(parent, style=self.getStyle(), 
            columns=columns, resizeableColumn=0, itemPopupMenu=itemPopupMenu,
            columnPopupMenu=columnPopupMenu, *args, **kwargs)
        self.setItemGetters(getItemText, getItemImage, getItemAttr,
            getItemId, getRootIndices, getChildIndices)
        self.bindEventHandlers(selectCommand, editCommand, dragAndDropCommand)
        self.refresh()
        
    # Extend CtrlWithColumns with TreeListCtrl specific behaviour:
        
    def _setColumns(self, *args, **kwargs):
        super(TreeListCtrl, self)._setColumns(*args, **kwargs)
        self.SetMainColumn(0)
                        
    # Extend TreeMixin with TreeListCtrl specific behaviour:

    def getStyle(self):
        return super(TreeListCtrl, self).getStyle() | wx.TR_FULL_ROW_HIGHLIGHT

    def renderNode(self, item, rowIndex):
        super(TreeListCtrl, self).renderNode(item, rowIndex)
        for columnIndex in range(1, self.GetColumnCount()):
            column = self._getColumn(columnIndex)
            self.refreshCell(item, column, rowIndex, columnIndex)
                        
    def refreshColumn(self, columnIndex):
        column = self._getColumn(columnIndex)
        for rowIndex, item in self.allItems():
            self.refreshCell(item, column, rowIndex, columnIndex)
            
    def refreshColumns(self):
        for columnIndex in range(1, self.GetColumnCount()):
            self.refreshColumn(columnIndex)

    def refreshCell(self, item, column, rowIndex, columnIndex):
        self.SetItemText(item, self.getItemText(rowIndex, column), columnIndex)
        self.SetItemImage(item, self.getItemImage(rowIndex, column), 
            wx.TreeItemIcon_Normal, columnIndex)
        
    def allItems(self):
        for rowIndex in range(self._count):
            try:
                yield rowIndex, self[rowIndex]
            except IndexError:
                pass # Item is hidden
            
    # Adapters to make the TreeListCtrl API more like the TreeCtrl API:
        
    def SelectItem(self, item, select=True):
        ''' SelectItem takes an item and an optional boolean that indicates 
            whether the item should be selected (True, default) or unselected 
            (False). This makes SelectItem more similar to 
            TreeCtrl.SelectItem. '''
        if select:
            self.selectItems(item)
        elif not select and self.IsSelected(item):
            # Take the current selection and remove item from it. This is a
            # bit more wordy then I'd like, but TreeListCtrl has no 
            # UnselectItem.
            currentSelection = self.GetSelections()
            currentSelection.remove(item)
            self.UnselectAll()
            self.selectItems(*currentSelection)
    
    def selectItems(self, *items):
        for item in items:
            if not self.IsSelected(item):
                super(TreeListCtrl, self).SelectItem(item, unselect_others=False)
        
    def ToggleItemSelection(self, item):
        ''' TreeListCtrl doesn't have a ToggleItemSelection. '''
        self.SelectItem(item, not self.IsSelected(item))
        
    def SetItemImage(self, item, imageIndex, which, column=0):
        super(TreeListCtrl, self).SetItemImage(item, imageIndex, column, which)
        
    # Adapters to make the TreeListCtrl more like the ListCtrl
    
    def DeleteColumn(self, columnIndex):
        self.RemoveColumn(columnIndex)
        self.refreshColumns()
        
    def InsertColumn(self, columnIndex, columnHeader, *args, **kwargs):
        format = self.alignmentMap[kwargs.pop('format', wx.LIST_FORMAT_LEFT)]
        if columnIndex == self.GetColumnCount():
            self.AddColumn(columnHeader, *args, **kwargs)
        else:
            super(TreeListCtrl, self).InsertColumn(columnIndex, columnHeader, 
                *args, **kwargs)
        self.SetColumnAlignment(columnIndex, format)
        self.refreshColumns()
    
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
