'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>
Copyright (C) 2008 Rob McMullen <rob.mcmullen@gmail.com>
Copyright (C) 2008 Thomas Sonne Olesen <tpo@sonnet.dk>

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

import wx
from taskcoachlib import patterns, command, widgets, domain
from taskcoachlib.domain import note
from taskcoachlib.i18n import _
from taskcoachlib.gui import uicommand, menu, dialog
import base, mixin

class NoteViewer(mixin.AttachmentDropTarget, mixin.FilterableViewerForNotes, 
                 mixin.SearchableViewer, base.SortableViewerWithColumns, 
                 mixin.SortableViewerForNotes, base.TreeViewer):
    SorterClass = note.NoteSorter
    defaultTitle = _('Notes')
    
    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories')
        kwargs.setdefault('settingsSection', 'noteviewer')
        super(NoteViewer, self).__init__(*args, **kwargs)
        for eventType in [note.Note.subjectChangedEventType()]:
            patterns.Publisher().registerObserver(self.onNoteChanged, 
                eventType)
        patterns.Publisher().registerObserver(self.onColorChange,
            eventType=note.Note.colorChangedEventType())
        
    def onColorChange(self, event):
        note = event.source()
        if note in self.model():
            self.widget.RefreshItem(self.getIndexOfItem(note))

    def createWidget(self):
        imageList = self.createImageList() # Has side-effects
        self._columns = self._createColumns()
        widget = widgets.TreeListCtrl(self, self.columns(), self.getItemText, 
            self.getItemTooltipData, self.getItemImage, self.getItemAttr, 
            self.getChildrenCount, self.getItemExpanded, self.onSelect,
            uicommand.NoteEdit(viewer=self, notes=self.model()),
            uicommand.NoteDragAndDrop(viewer=self, notes=self.model()),
            menu.NotePopupMenu(self.parent, self.settings, self.model(),
                               self.categories, self), 
            menu.ColumnPopupMenu(self),
            **self.widgetCreationKeywordArguments())
        widget.AssignImageList(imageList)
        return widget
    
    def createFilter(self, notes):
        notes = super(NoteViewer, self).createFilter(notes)
        # FIXMERGE
##         return base.DeletedFilter(base.SearchFilter(notes, treeMode=True))
        return domain.base.DeletedFilter(notes)

    def createImageList(self):
        imageList = wx.ImageList(16, 16)
        self.imageIndex = {}
        for index, image in enumerate(['ascending', 'descending', 'attachment']):
            imageList.Add(wx.ArtProvider_GetBitmap(image, wx.ART_MENU, (16,16)))
            self.imageIndex[image] = index
        return imageList

    def attachmentImageIndex(self, note, which):
        if note.attachments():
            return self.imageIndex['attachment'] 
        else:
            return -1

    def createToolBarUICommands(self):
        commands = super(NoteViewer, self).createToolBarUICommands()
        commands[-2:-2] = [None,
                           uicommand.NoteNew(notes=self.model(),
                                             categories=self.categories,
                                             settings=self.settings),
                           uicommand.NoteNewSubNote(notes=self.model(),
                                                    viewer=self),
                           uicommand.NoteEdit(notes=self.model(),
                                              viewer=self),
                           uicommand.NoteDelete(notes=self.model(),
                                                viewer=self)]
        return commands

    def createColumnUICommands(self):
        return [\
            uicommand.ToggleAutoColumnResizing(viewer=self,
                                               settings=self.settings),
            None,
            uicommand.ViewColumn(menuText=_('&Description'),
                helpText=_('Show/hide description column'),
                setting='description', viewer=self),
            uicommand.ViewColumn(menuText=_('&Attachments'),
                helpText=_('Show/hide attachments column'),
                setting='attachments', viewer=self),
            uicommand.ViewColumn(menuText=_('&Categories'),
                helpText=_('Show/hide categories column'),
                setting='categories', viewer=self),
            uicommand.ViewColumn(menuText=_('Overall categories'),
                helpText=_('Show/hide overall categories column'),
                setting='totalCategories', viewer=self)]

    def _createColumns(self):
        columns = [widgets.Column(name, columnHeader,
                width=self.getColumnWidth(name), 
                resizeCallback=self.onResizeColumn,
                renderCallback=renderCallback, 
                sortCallback=uicommand.ViewerSortByCommand(viewer=self, 
                    value=name.lower(), menuText=sortMenuText, 
                    helpText=sortHelpText),
                *eventTypes) \
            for name, columnHeader, sortMenuText, sortHelpText, eventTypes, renderCallback in \
            ('subject', _('Subject'), _('&Subject'), _('Sort notes by subject'), 
                (note.Note.subjectChangedEventType(),), 
                lambda note: note.subject(recursive=False)),
            ('description', _('Description'), _('&Description'), 
                _('Sort notes by description'), 
                (note.Note.descriptionChangedEventType(),), 
                lambda note: note.description()),
            ('categories', _('Categories'), _('&Categories'), 
                _('Sort notes by categories'), 
                (note.Note.categoryAddedEventType(), 
                 note.Note.categoryRemovedEventType(), 
                 note.Note.categorySubjectChangedEventType()), 
                self.renderCategory),
            ('totalCategories', _('Overall categories'), 
                _('&Overall categories'), _('Sort notes by overall categories'),
                 (note.Note.totalCategoryAddedEventType(),
                  note.Note.totalCategoryRemovedEventType(),
                  note.Note.totalCategorySubjectChangedEventType()), 
                 self.renderCategory)]
        attachmentsColumn = widgets.Column('attachments', '', 
            note.Note.attachmentsChangedEventType(),
            width=self.getColumnWidth('attachments'),
            alignment=wx.LIST_FORMAT_LEFT,
            imageIndexCallback=self.attachmentImageIndex,
            headerImageIndex=self.imageIndex['attachment'],
            renderCallback=lambda note: '')
        columns.insert(2, attachmentsColumn)
        return columns
                     
    def onNoteChanged(self, event):
        note = event.source()
        if note in self.list:
            self.widget.RefreshItem(self.getIndexOfItem(note))
            
    def getItemText(self, index, column=0):
        item = self.getItemWithIndex(index)
        column = self.visibleColumns()[column]
        return column.render(item)

    def getItemTooltipData(self, index, column=0):
        if self.settings.getboolean('view', 'descriptionpopups'):
            note = self.getItemWithIndex(index)
            if note.description():
                result = [(None, map(lambda x: x.rstrip('\r'), note.description().split('\n')))]
            else:
                result = []
            result.append(('attachment', [unicode(attachment) for attachment in note.attachments()]))
            return result
        else:
            return []
    
    def getBackgroundColor(self, note):
        return note.color()
    
    def getItemAttr(self, index):
        note = self.getItemWithIndex(index)
        return wx.ListItemAttr(None, self.getBackgroundColor(note))
                
    def isShowingNotes(self):
        return True

    def statusMessages(self):
        status1 = _('Notes: %d selected, %d total')%\
            (len(self.curselection()), len(self.list))
        status2 = _('Status: n/a')
        return status1, status2

    def newItemDialog(self, *args, **kwargs):
        filteredCategories = [category for category in self.categories if
                              category.isFiltered()]
        newCommand = command.NewNoteCommand(self.list, categories=filteredCategories, 
            *args, **kwargs)
        newCommand.do()
        return self.editItemDialog(bitmap=kwargs['bitmap'], items=newCommand.items)
    
    # See TaskViewer for why the methods below have two names.
    
    def editItemDialog(self, *args, **kwargs):
        return dialog.editor.NoteEditor(wx.GetTopLevelParent(self),
            command.EditNoteCommand(self.list, kwargs['items']),
            self.settings, self.list, self.categories, bitmap=kwargs['bitmap'])
    
    def deleteItemCommand(self):
        return command.DeleteCommand(self.list, self.curselection(),
                  shadow=True)
    
    def newSubItemDialog(self, *args, **kwargs):
        newCommand = command.NewSubNoteCommand(self.list, self.curselection())
        newCommand.do()
        return self.editItemDialog(bitmap=kwargs['bitmap'], items=newCommand.items)
        
    newSubNoteDialog = newSubItemDialog

