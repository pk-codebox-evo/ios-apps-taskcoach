import wx, uicommand
from i18n import _
   
class Menu(wx.Menu, uicommand.UICommandContainer):
    def __init__(self, window):
        super(Menu, self).__init__()
        self._window = window
        
    def __len__(self):
        return self.GetMenuItemCount()

    def appendUICommand(self, uiCommand):
        return uiCommand.appendToMenu(self, self._window)    
    
    def appendMenu(self, text, subMenu):
        subMenuItem = wx.MenuItem(self, -1, text, subMenu=subMenu)
        # hack to force a 16 bit margin. SetMarginWidth doesn't work
        if '__WXMSW__' in wx.PlatformInfo:
            subMenuItem.SetBitmap(wx.ArtProvider_GetBitmap('nobitmap', wx.ART_MENU, (16,16)))
        self.AppendItem(subMenuItem)

    def invokeMenuItem(self, menuItem):
        ''' Programmatically invoke the menuItem. This is mainly for testing purposes. '''
        self._window.ProcessEvent(wx.CommandEvent(wx.wxEVT_COMMAND_MENU_SELECTED, winid=menuItem.GetId()))
    
    def openMenu(self):
        ''' Programmatically open the menu. This is mainly for testing purposes. '''
        self._window.ProcessEvent(wx.MenuEvent(wx.wxEVT_MENU_OPEN, menu=self))


class MainMenu(wx.MenuBar):
    def __init__(self, mainwindow, uiCommands, settings):
        super(MainMenu, self).__init__()
        self.Append(FileMenu(mainwindow, uiCommands, settings), _('&File'))
        self.Append(EditMenu(mainwindow, uiCommands), _('&Edit'))
        self.Append(ViewMenu(mainwindow, uiCommands), _('&View'))
        self.Append(TaskMenu(mainwindow, uiCommands), _('&Task'))
        self.Append(EffortMenu(mainwindow, uiCommands), _('Eff&ort'))
        self.Append(HelpMenu(mainwindow, uiCommands), _('&Help'))


class FileMenu(Menu):
    def __init__(self, mainwindow, uiCommands, settings):
        super(FileMenu, self).__init__(mainwindow)
        self.__settings = settings
        self.__uiCommands = uiCommands
        self.__fileMenuUICommands = ['open', 'merge', 'close', None, 
            'save', 'saveas', 'saveselection', None, 'quit']
        self.__recentFileUICommands = []
        self.__separator = None
        self.appendUICommands(uiCommands, self.__fileMenuUICommands)
        self._window.Bind(wx.EVT_MENU_OPEN, self.onOpenMenu)

    def onOpenMenu(self, event):
        self.__removeRecentFileMenuItems()
        self.__insertRecentFileMenuItems()        
        event.Skip()
    
    def __insertRecentFileMenuItems(self):
        self.__recentFileUICommands = []
        self.__separator = None
        recentFilesStartPosition = self.__recentFilesStartPosition()
        recentFiles = eval(self.__settings.get('file', 'recentfiles'))
        maximumNumberOfRecentFiles = self.__settings.getint('file', 'maxrecentfiles')
        recentFiles = recentFiles[:maximumNumberOfRecentFiles]
        if recentFiles:
            for index, recentFile in enumerate(recentFiles):
                recentFileNumber = index + 1 # Only computer nerds start counting at 0 :-)
                recentFileMenuPosition = recentFilesStartPosition + index
                recentFileOpenUICommand = self.__uiCommands.createRecentFileOpenUICommand(recentFile, recentFileNumber)
                recentFileOpenUICommand.appendToMenu(self, self._window, recentFileMenuPosition)
                self.__recentFileUICommands.append(recentFileOpenUICommand)
            self.__separator = self.InsertSeparator(recentFileMenuPosition+1)

    def __removeRecentFileMenuItems(self):
        for recentFileUICommand in self.__recentFileUICommands:
            recentFileUICommand.removeFromMenu(self, self._window)
        if self.__separator:
            self.RemoveItem(self.__separator)

    def __recentFilesStartPosition(self):
        return len(self.__fileMenuUICommands) - 1 # Start just before the Quit menu item
        
    def __recentFilesStopPosition(self):
        return len(self) - 1 # Stop just before the Quit menu item
        
        
class EditMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(EditMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['undo', 'redo', None, 'cut', 
            'copy', 'paste', 'pasteintotask', None])
        # the spaces are to leave room for command names in the Undo and Redo menuitems:
        self.appendMenu(_('&Select')+' '*50, SelectMenu(mainwindow, uiCommands))
        self.appendUICommands(uiCommands, [None, 'editpreferences'])


class SelectMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(SelectMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['selectall', 'invertselection', 
            'clearselection'])


class ViewMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewalltasks'])
        self.appendMenu(_('Tas&ks that are'), 
            ViewTaskStatesMenu(mainwindow, uiCommands))
        self.appendMenu(_('Tasks &due before end of'),
            ViewTasksByDueDateMenu(mainwindow, uiCommands))
        self.appendUICommands(uiCommands, ['viewcategories', None])
        self.appendMenu(_('&Columns'), ViewColumnsMenu(mainwindow, uiCommands))
        self.appendUICommands(uiCommands, [None])
        self.appendMenu(_('Task &list options'), 
            ViewTaskListMenu(mainwindow, uiCommands))
        self.appendMenu(_('Task &tree options'), 
            ViewTaskTreeMenu(mainwindow, uiCommands))
        self.appendUICommands(uiCommands, [None])
        self.appendMenu(_('&Sort'), SortMenu(mainwindow, uiCommands))
        self.appendUICommands(uiCommands, [None])
        self.appendMenu(_('T&oolbar'), ToolBarMenu(mainwindow, uiCommands))        
        self.appendUICommands(uiCommands, ['viewfinddialog', 'viewstatusbar'])   


class ViewColumnsMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewColumnsMenu, self).__init__(mainwindow)
        self.appendMenu(_('&Dates'), ViewDateColumnsMenu(mainwindow, uiCommands))
        self.appendMenu(_('&Budget'), ViewBudgetColumnsMenu(mainwindow, uiCommands))
        self.appendMenu(_('&Financial'), ViewFinancialColumnsMenu(mainwindow, uiCommands))
        self.appendUICommands(uiCommands, ['viewpriority', 'viewtotalpriority', 
        'viewlastmodificationtime', 'viewtotallastmodificationtime'])


class ViewDateColumnsMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewDateColumnsMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewalldatecolumns', None, 
            'viewstartdate', 'viewduedate', 'viewcompletiondate', 
            'viewtimeleft'])


class ViewBudgetColumnsMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewBudgetColumnsMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewallbudgetcolumns', None, 
            'viewbudget', 'viewtotalbudget', 'viewtimespent',
            'viewtotaltimespent', 'viewbudgetleft', 'viewtotalbudgetleft'])


class ViewFinancialColumnsMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewFinancialColumnsMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewallfinancialcolumns', None, 
            'viewhourlyfee', 'viewfixedfee', 'viewtotalfixedfee', 
            'viewrevenue', 'viewtotalrevenue'])

           
class ViewTaskStatesMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewTaskStatesMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewactivetasks',
            'viewinactivetasks', 'viewcompletedtasks', None,
            'viewoverduetasks', 'viewoverbudgettasks'])

                
class ViewTaskListMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewTaskListMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewcompositetasks'])

           
class ViewTaskTreeMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewTaskTreeMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewexpandselected', 
            'viewcollapseselected', None, 'viewexpandall', 'viewcollapseall'])


class SortMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(SortMenu, self).__init__(mainwindow)
        # NOTE: 'viewsortorder' needs to be added first to properly initialize 
        # ascending/descending order
        self.appendUICommands(uiCommands, ['viewsortorder', 
            'viewsortcasesensitive', 'viewsortbystatusfirst', None, 
            'viewsortbysubject', 'viewsortbystartdate', 'viewsortbyduedate',
            'viewsortbytimeleft', 'viewsortbycompletiondate',
            'viewsortbybudget', 'viewsortbytotalbudget', 'viewsortbytimespent',
            'viewsortbytotaltimespent', 'viewsortbybudgetleft',
            'viewsortbytotalbudgetleft', 'viewsortbypriority',
            'viewsortbytotalpriority', 'viewsortbyhourlyfee',
            'viewsortbyfixedfee', 'viewsortbylastmodificationtime', 
            'viewsortbytotallastmodificationtime'])
                
    
class ToolBarMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ToolBarMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['toolbarhide', 'toolbarsmall',
            'toolbarmedium', 'toolbarbig'])


class ViewTasksByDueDateMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewTasksByDueDateMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewdueunlimited', 'viewduetoday',
            'viewduetomorrow', 'viewdueworkweek', 'viewdueweek',
            'viewduemonth', 'viewdueyear'])


class TaskMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(TaskMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['new', 'newsubtask', 
            None, 'edit', 'markcompleted', None, 'delete'])
            
            
class EffortMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(EffortMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['neweffort', 'editeffort', 'deleteeffort', None, 
            'starteffort', 'stopeffort'])
        
        
class HelpMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(HelpMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['helptasks', 'helpcolors', None, 
            'about', 'license'])


class TaskBarMenu(Menu):
    def __init__(self, taskBarIcon, uiCommands):
        super(TaskBarMenu, self).__init__(taskBarIcon)
        self.appendUICommands(uiCommands, ['new', 'neweffort', 'stopeffort', None, 'restore', 'quit'])


class TaskPopupMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(TaskPopupMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['cut', 'copy', 'paste',
            'pasteintotask', None, 'new', 'newsubtask', None, 'edit', 
            'markcompleted', None, 'delete', None, 'neweffort', 'starteffort',
            'stopeffort', None, 'viewexpandselected', 'viewcollapseselected'])


class EffortPopupMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(EffortPopupMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['cut', 'copy', 'paste', 
           'pasteintotask', None, 'new', None, 'neweffort', 'editeffort', 
           'deleteeffort', None, 'stopeffort'])


class TaskViewerColumnPopupMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(TaskViewerColumnPopupMenu, self).__init__(mainwindow)
        # FIXME: Can't remember why we need a wx.FutureCall here? Maybe
        # because we need time for the viewer to add columns, so these commands
        # can then hide the right columns?
        wx.FutureCall(1000, lambda: self.fillMenu(mainwindow, uiCommands))
        
    def fillMenu(self, mainwindow, uiCommands):
        self.appendMenu(_('&Dates'), ViewDateColumnsMenu(mainwindow, uiCommands)),
        self.appendMenu(_('&Budget'), ViewBudgetColumnsMenu(mainwindow, uiCommands)),
        self.appendMenu(_('&Financial'), ViewFinancialColumnsMenu(mainwindow, uiCommands))
        self.appendUICommands(uiCommands, [
            'viewpriority', 'viewtotalpriority',
            'viewlastmodificationtime',
            'viewtotallastmodificationtime'])
