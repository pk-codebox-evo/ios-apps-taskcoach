import wx
from i18n import _

class StatusBar(wx.StatusBar):
    def __init__(self, parent, taskList, filteredList, viewer):
        super(StatusBar, self).__init__(parent, -1)
        self.SetFieldsCount(2)
        self.parent = parent
        self.taskList = taskList
        self.filteredList = filteredList
        self.viewer = viewer
        self.viewer.registerObserver(self.notify)
        self.scheduledStatusDisplay = None
        self.notify(None)
        parent.Bind(wx.EVT_MENU_HIGHLIGHT_ALL, self.resetStatusBar)
        parent.Bind(wx.EVT_TOOL_ENTER, self.resetStatusBar)

    def resetStatusBar(self, event):
        ''' Unfortunately, the menu's and toolbar don't restore the
        previous statusbar text after they have displayed their help
        text, so we have to do it by hand. '''
        try:
            id = event.GetSelection() # for CommandEvent from the Toolbar
        except AttributeError:
            id = event.GetMenuId() # for MenuEvent
        if id == -1:
            self._displayStatus()
        event.Skip()

    def notify(self, *args, **kwargs):
        # Give viewer a chance to update first:
        wx.CallAfter(self._displayStatus)

    def _displayStatus(self):
        status1, status2 = self.viewer.statusMessages()
        super(StatusBar, self).SetStatusText(status1, 0)
        super(StatusBar, self).SetStatusText(status2, 1)

    def SetStatusText(self, message, pane=0, delay=3000):
        if self.scheduledStatusDisplay:
            self.scheduledStatusDisplay.Stop()
        super(StatusBar, self).SetStatusText(message, pane)
        self.scheduledStatusDisplay = wx.FutureCall(delay, self._displayStatus)

    def Destroy(self):
        self.viewer.removeObserver(self.notify)
        self.parent.Unbind(wx.EVT_MENU_HIGHLIGHT_ALL)
        self.parent.Unbind(wx.EVT_TOOL_ENTER)
        if self.scheduledStatusDisplay:
            self.scheduledStatusDisplay.Stop()
