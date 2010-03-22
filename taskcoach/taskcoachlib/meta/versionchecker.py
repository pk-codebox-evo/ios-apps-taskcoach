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

import threading, wx, urllib2
import data
 

class VersionChecker(threading.Thread):
    def __init__(self, settings):
        self.settings = settings
        super(VersionChecker, self).__init__()
        
    def _set_daemon(self):
        return True # Don't block application exit
        
    def run(self):
        latestVersionString = self.getLatestVersion()
        latestVersion = self.tupleVersion(latestVersionString)
        lastVersionNotified = self.tupleVersion(self.settings.get('version', 'notified'))
        currentVersion = self.tupleVersion(data.version)
        if latestVersion > lastVersionNotified and latestVersion > currentVersion:
            self.settings.set('version', 'notified', latestVersionString)
            self.notifyUser(latestVersionString)
            
    def getLatestVersion(self):
        try:
            versionText = self.parseVersionFile(self.retrieveVersionFile())
            return versionText.strip()
        except:
            return self.settings.get('version', 'notified') # pylint: disable-msg=W0702

    def parseVersionFile(self, versionFile):
        return versionFile.readline()

    def retrieveVersionFile(self):
        return urllib2.urlopen(data.version_url)

    def notifyUser(self, latestVersion):
        # Must use CallAfter because this is a non-GUI thread
        wx.CallAfter(self.showDialog, latestVersion)
        
    def showDialog(self, latestVersion, VersionDialog=None):
        # Import version here to prevent circular import:
        from taskcoachlib.gui.dialog import version 
        VersionDialog = VersionDialog or version.VersionDialog
        dialog = VersionDialog(wx.GetApp().GetTopWindow(), 
                               version=latestVersion, settings=self.settings)
        dialog.Show()
        return dialog

    @staticmethod
    def tupleVersion(versionString):
        return tuple(int(i) for i in versionString.split('.'))
