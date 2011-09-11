'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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

import wx, wx.html, os
from taskcoachlib.i18n import _
from taskcoachlib.thirdparty import aui, sized_controls
import notebook


class Dialog(sized_controls.SizedDialog):
    def __init__(self, parent, title, bitmap='edit', 
                 direction=None, *args, **kwargs):
        self._buttonTypes = kwargs.get('buttonTypes', wx.OK|wx.CANCEL)
        # On wxGTK, calling Raise() on the dialog causes it to be shown, which
        # is rather undesirable during testing, so provide a way to instruct 
        # the dialog to not call self.Raise():
        raiseDialog = kwargs.pop('raiseDialog', True)  
        super(Dialog, self).__init__(parent, -1, title,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.SetIcon(wx.ArtProvider_GetIcon(bitmap, wx.ART_FRAME_ICON,
            (16, 16)))
        self._panel = self.GetContentsPane()
        self._panel.SetSizerType('vertical')
        self._panel.SetSizerProps(expand=True, proportion=1)
        self._direction = direction
        self._interior = self.createInterior()
        self._interior.SetSizerProps(expand=True, proportion=1)
        self.fillInterior()
        self._buttons = self.createButtons()
        self._panel.Fit()
        self.Fit()
        self.CentreOnParent()
        if raiseDialog:
            wx.CallAfter(self.Raise)
        wx.CallAfter(self._panel.SetFocus)
        
    def createInterior(self):
        raise NotImplementedError

    def fillInterior(self):
        pass
    
    def createButtons(self):
        buttonSizer = self.CreateStdDialogButtonSizer(wx.OK if self._buttonTypes == wx.ID_CLOSE else self._buttonTypes)
        if self._buttonTypes & wx.OK or self._buttonTypes & wx.ID_CLOSE:
            buttonSizer.GetAffirmativeButton().Bind(wx.EVT_BUTTON, self.ok)
        if self._buttonTypes & wx.CANCEL:
            buttonSizer.GetCancelButton().Bind(wx.EVT_BUTTON, self.cancel)
        if self._buttonTypes == wx.ID_CLOSE:
            buttonSizer.GetAffirmativeButton().SetLabel(_('Close'))
        self.SetButtonSizer(buttonSizer)
        return buttonSizer
    
    def ok(self, event=None):
        if event:
            event.Skip()
        self.Close(True)
        self.Destroy()
        
    def cancel(self, event=None):
        if event:
            event.Skip()
        self.Close(True)
        self.Destroy()
        
    def disableOK(self):
        self._buttons.GetAffirmativeButton().Disable()
        
    def enableOK(self):
        self._buttons.GetAffirmativeButton().Enable()


class NotebookDialog(Dialog):    
    def createInterior(self):
        return notebook.Notebook(self._panel, 
            agwStyle=aui.AUI_NB_DEFAULT_STYLE & ~aui.AUI_NB_TAB_SPLIT & \
                     ~aui.AUI_NB_TAB_MOVE & ~aui.AUI_NB_DRAW_DND_TAB)

    def fillInterior(self):
        self.addPages()
            
    def __getitem__(self, index):
        return self._interior[index]
    
    def cancelPages(self, pagesToCancel):
        ''' Close the pages and remove them from our interior book widget. '''
        for pageIndex, page in enumerate(self):
            if page in pagesToCancel:
                self._interior.GetPage(pageIndex).Close()
                self._interior.RemovePage(pageIndex)
       
    def ok(self, *args, **kwargs):
        self.okPages()
        super(NotebookDialog, self).ok(*args, **kwargs)
        
    def okPages(self, *args, **kwargs):
        for page in self._interior:
            page.ok(*args, **kwargs)

    def addPages(self):
        raise NotImplementedError 

        
class HtmlWindowThatUsesWebBrowserForExternalLinks(wx.html.HtmlWindow):
    def OnLinkClicked(self, linkInfo): # pylint: disable-msg=W0221
        openedLinkInExternalBrowser = False
        if linkInfo.GetTarget() == '_blank':
            import webbrowser # pylint: disable-msg=W0404
            try:
                webbrowser.open(linkInfo.GetHref())
                openedLinkInExternalBrowser = True
            except webbrowser.Error:
                pass
        if not openedLinkInExternalBrowser:
            super(HtmlWindowThatUsesWebBrowserForExternalLinks, 
                  self).OnLinkClicked(linkInfo)


class HTMLDialog(Dialog):
    def __init__(self, title, htmlText, *args, **kwargs):
        self._htmlText = htmlText
        super(HTMLDialog, self).__init__(None, title, buttonTypes=wx.ID_CLOSE, 
                                         *args, **kwargs)
        
    def createInterior(self):
        interior = HtmlWindowThatUsesWebBrowserForExternalLinks(self._panel, 
            -1, size=(550,400))
        if self._direction:
            interior.SetLayoutDirection(self._direction)
        return interior
        
    def fillInterior(self):
        self._interior.AppendToPage(self._htmlText)

    def OnLinkClicked(self, linkInfo):
        pass
        
        
def AttachmentSelector(**callerKeywordArguments):
    kwargs = {'message': _('Add attachment'),
              'default_path' : os.getcwd(), 
              'wildcard' : _('All files (*.*)|*'), 
              'flags': wx.OPEN}
    kwargs.update(callerKeywordArguments)
    return wx.FileSelector(**kwargs) # pylint: disable-msg=W0142
