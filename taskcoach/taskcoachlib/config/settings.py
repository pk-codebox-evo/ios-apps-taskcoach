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

import ConfigParser, os, sys, wx
from taskcoachlib import meta, patterns, operating_system
from taskcoachlib.i18n import _
from taskcoachlib.thirdparty.pubsub import pub
import defaults


class UnicodeAwareConfigParser(ConfigParser.RawConfigParser):
    def set(self, section, setting, value): # pylint: disable-msg=W0222
        if type(value) == type(u''):
            value = value.encode('utf-8')
        ConfigParser.RawConfigParser.set(self, section, setting, value)

    def get(self, section, setting): # pylint: disable-msg=W0221
        value = ConfigParser.RawConfigParser.get(self, section, setting)
        return value.decode('utf-8') # pylint: disable-msg=E1103


class CachingConfigParser(UnicodeAwareConfigParser):
    ''' ConfigParser is rather slow, so cache its values. '''
    def __init__(self, *args, **kwargs):
        self.__cachedValues = dict()
        UnicodeAwareConfigParser.__init__(self, *args, **kwargs)
        
    def read(self, *args, **kwargs):
        self.__cachedValues = dict()
        return UnicodeAwareConfigParser.read(self, *args, **kwargs)

    def set(self, section, setting, value):
        self.__cachedValues[(section, setting)] = value
        UnicodeAwareConfigParser.set(self, section, setting, value)
        
    def get(self, section, setting):
        cache, key = self.__cachedValues, (section, setting)
        if key not in cache:
            cache[key] = UnicodeAwareConfigParser.get(self, *key) # pylint: disable-msg=W0142
        return cache[key]
        
        
class Settings(object, CachingConfigParser):
    def __init__(self, load=True, iniFile=None, *args, **kwargs):
        # Sigh, ConfigParser.SafeConfigParser is an old-style class, so we 
        # have to call the superclass __init__ explicitly:
        CachingConfigParser.__init__(self, *args, **kwargs) 
        self.initializeWithDefaults()
        self.__loadAndSave = load
        self.__iniFileSpecifiedOnCommandLine = iniFile
        if load:
            # First, try to load the settings file from the program directory,
            # if that fails, load the settings file from the settings directory
            try:
                if not self.read(self.filename(forceProgramDir=True)):
                    self.read(self.filename())
                errorMessage = ''
            except ConfigParser.ParsingError, errorMessage:
                # Ignore exceptions and simply use default values. 
                # Also record the failure in the settings:
                self.initializeWithDefaults()
            self.setLoadStatus(unicode(errorMessage))
        else:
            # Assume that if the settings are not to be loaded, we also 
            # should be quiet (i.e. we are probably in test mode):
            self.__beQuiet()
        pub.subscribe(self.onSettingsFileLocationChanged, 
                      'settings.file.saveinifileinprogramdir')
        
    def onSettingsFileLocationChanged(self, value):
        saveIniFileInProgramDir = value
        if not saveIniFileInProgramDir:
            try:
                os.remove(self.generatedIniFilename(forceProgramDir=True))
            except: 
                return # pylint: disable-msg=W0702
            
    def initializeWithDefaults(self):
        for section in self.sections():
            self.remove_section(section)
        for section, settings in defaults.defaults.items():
            self.add_section(section)
            for key, value in settings.items():
                # Don't notify observers while we are initializing
                super(Settings, self).set(section, key, value)
                
    def setLoadStatus(self, message):
        self.set('file', 'inifileloaded', 'False' if message else 'True')
        self.set('file', 'inifileloaderror', message)

    def __beQuiet(self):
        noisySettings = [('window', 'splash', 'False'), 
                         ('window', 'tips', 'False'), 
                         ('window', 'starticonized', 'Always')]
        for section, setting, value in noisySettings:
            self.set(section, setting, value)
            
    def add_section(self, section, copyFromSection=None):  # pylint: disable-msg=W0221
        result = super(Settings, self).add_section(section)
        if copyFromSection:
            for name, value in self.items(copyFromSection):
                super(Settings, self).set(section, name, value)
        return result
    
    def getRawValue(self, section, option):
        return super(Settings, self).get(section, option)

    def get(self, section, option):
        try:
            result = super(Settings, self).get(section, option)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            return self.getDefault(section, option)
        result = self._fixValuesFromOldIniFiles(section, option, result)
        result = self._ensureMinimum(section, option, result)
        return result

    def getDefault(self, section, option):
        defaultSectionKey = section.strip('0123456789')
        try:
            defaultSection = defaults.defaults[defaultSectionKey]
        except KeyError:
            raise ConfigParser.NoSectionError, defaultSectionKey
        try:
            return defaultSection[option]
        except KeyError:
            raise ConfigParser.NoOptionError, (option, defaultSection)
            
    def _ensureMinimum(self, section, option, result):
        # Some settings may have a minimum value, make sure we return at 
        # least that minimum value:
        if section in defaults.minimum and option in defaults.minimum[section]:
            result = max(result, defaults.minimum[section][option])
        return result
    
    def _fixValuesFromOldIniFiles(self, section, option, result):
        ''' Try to fix settings from old TaskCoach.ini files that are no longer 
            valid. '''
        original = result
        # Starting with release 1.1.0, the date properties of tasks (startDate,
        # dueDate and completionDate) are datetimes: 
        taskDateColumns = ('startDate', 'dueDate', 'completionDate')
        if option == 'sortby' and result in taskDateColumns:
            result += 'Time'
        elif option == 'columns':
            columns = [(col + 'Time' if col in taskDateColumns else col) for col in eval(result)]
            result = str(columns)
        elif option == 'columnwidths':
            widths = dict()
            try:
                columnWidthMap = eval(result)
            except SyntaxError:
                columnWidthMap = dict()
            for column, width in columnWidthMap.items():
                if column in taskDateColumns:
                    column += 'Time'
                widths[column] = width
            result = str(widths)
        elif section == 'feature' and option == 'notifier' and result == 'Native':
            result = 'Task Coach'
        elif section == 'editor' and option == 'preferencespages':
            result = result.replace('colors', 'appearance')
        if result != original:
            super(Settings, self).set(section, option, result)
        return result

    def set(self, section, option, value, new=False): # pylint: disable-msg=W0221
        if new:
            currentValue = 'a new option, so use something as current value'\
                ' that is unlikely to be equal to the new value'
        else:
            currentValue = self.get(section, option)
        if value != currentValue:
            super(Settings, self).set(section, option, value)
            patterns.Event('%s.%s'%(section, option), self, value).send()
            return True
        else:
            return False
            
    def setboolean(self, section, option, value):
        if self.set(section, option, str(value)):
            pub.sendMessage('settings.%s.%s'%(section, option), value=value)
            
    setvalue = settuple = setlist = setdict = setboolean
    
    def getlist(self, section, option):
        return self.getEvaluatedValue(section, option, eval)
        
    getvalue = gettuple = getdict = getlist

    def getint(self, section, option):
        return self.getEvaluatedValue(section, option, int)
    
    def getboolean(self, section, option):
        return self.getEvaluatedValue(section, option, self.evalBoolean)

    @staticmethod
    def evalBoolean(stringValue):
        if stringValue in ('True', 'False'):
            return 'True' == stringValue
        else:
            raise ValueError, "invalid literal for Boolean value: '%s'"%stringValue
         
    def getEvaluatedValue(self, section, option, evaluate=eval, showerror=wx.MessageBox):
        stringValue = self.get(section, option)
        try:
            return evaluate(stringValue)
        except Exception, exceptionMessage: # pylint: disable-msg=W0703
            message = '\n'.join([ \
                _('Error while reading the %s-%s setting from %s.ini.')%(section, option, meta.filename),
                _('The value is: %s')%stringValue,
                _('The error is: %s')%exceptionMessage,
                _('%s will use the default value for the setting and should proceed normally.')%meta.name])
            showerror(message, caption=_('Settings error'), style=wx.ICON_ERROR)
            defaultValue = self.getDefault(section, option)
            self.set(section, option, defaultValue, new=True) # Ignore current value
            return evaluate(defaultValue)
        
    def save(self, showerror=wx.MessageBox, file=file): # pylint: disable-msg=W0622
        self.set('version', 'python', sys.version)
        self.set('version', 'wxpython', '%s-%s @ %s'%(wx.VERSION_STRING, wx.PlatformInfo[2], wx.PlatformInfo[1]))
        self.set('version', 'pythonfrozen', str(hasattr(sys, 'frozen')))
        self.set('version', 'current', meta.data.version)
        if not self.__loadAndSave:
            return
        try:
            path = self.path()
            if not os.path.exists(path):
                os.mkdir(path)
            iniFile = file(self.filename(), 'w')
            self.write(iniFile)
            iniFile.close()
        except Exception, message: # pylint: disable-msg=W0703
            showerror(_('Error while saving %s.ini:\n%s\n')% \
                      (meta.filename, message), caption=_('Save error'), 
                      style=wx.ICON_ERROR)

    def filename(self, forceProgramDir=False):
        if self.__iniFileSpecifiedOnCommandLine:
            return self.__iniFileSpecifiedOnCommandLine
        else:
            return self.generatedIniFilename(forceProgramDir) 
    
    def path(self, forceProgramDir=False, environ=os.environ): # pylint: disable-msg=W0102
        if self.__iniFileSpecifiedOnCommandLine:
            return self.pathToIniFileSpecifiedOnCommandLine()
        elif forceProgramDir or self.getboolean('file', 
                                                'saveinifileinprogramdir'):
            return self.pathToProgramDir()
        else:
            return self.pathToConfigDir(environ)

    def pathToProgramDir(self):
        path = sys.argv[0]
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        return path
    
    def pathToConfigDir(self, environ):
        try:
            path = os.path.join(environ['APPDATA'], meta.filename)
        except Exception:
            path = os.path.expanduser("~") # pylint: disable-msg=W0702
            if path == "~":
                # path not expanded: apparently, there is no home dir
                path = os.getcwd()
            path = os.path.join(path, '.%s'%meta.filename)
        return path

    def pathToTemplatesDir(self):
        path = os.path.join(self.path(), 'taskcoach-templates')

        if operating_system.isWindows():
            # Under Windows, check for a shortcut and follow it if it
            # exists.

            if os.path.exists(path + '.lnk'):
                from win32com.client import Dispatch # pylint: disable-msg=F0401

                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortcut(path + '.lnk')
                return shortcut.TargetPath

        try:
            os.makedirs(path)
        except OSError:
            pass
        return path

    def pathToIniFileSpecifiedOnCommandLine(self):
        return os.path.dirname(self.__iniFileSpecifiedOnCommandLine) or '.'
    
    def generatedIniFilename(self, forceProgramDir):
        return os.path.join(self.path(forceProgramDir), '%s.ini'%meta.filename)
