'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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

from taskcoachlib import meta
import sys, os, glob
from setup import setupOptions
from buildlib import clean
import taskcoach # to add taskcoachlib to the searchpath


setupOptions['cmdclass'] = dict(clean=clean)
                                
distdir = 'dist'
builddir = 'build'

manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
    <assemblyIdentity version="0.64.1.0" processorArchitecture="x86" 
    name="Controls" type="win32"/>
    <description>%s</description>
    <dependency>
        <dependentAssembly>
            <assemblyIdentity type="win32" 
            name="Microsoft.Windows.Common-Controls" version="6.0.0.0" 
            processorArchitecture="X86" publicKeyToken="6595b64144ccf1df"
            language="*"/>
        </dependentAssembly>
    </dependency>
</assembly>
"""%meta.name

script = r'''
; Inno Setup Script

[Setup]
AppName=%(name)s
AppVerName=%(name)s %(version)s
AppPublisher=%(author)s
AppPublisherURL=%(url)s
AppSupportURL=%(url)s
AppUpdatesURL=%(url)s
DefaultDirName={pf}\%(filename)s
DefaultGroupName=%(name)s
AllowNoIcons=yes
LicenseFile=../LICENSE.txt
Compression=lzma
SolidCompression=yes
OutputDir=../dist
OutputBaseFilename=%(filename)s-%(version)s-win32
ChangesAssociations=yes 
WizardImageFile=..\icons.in\splash_inno.bmp
PrivilegesRequired=none

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: associate; Description: "{cm:AssocFileExtension,{app},.tsk}"; GroupDescription: "Other tasks:"; Flags: unchecked

[Files]
Source: "%(filename)s-%(version)s-win32exe\%(filename)s.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "%(filename)s-%(version)s-win32exe\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[INI]
Filename: "{app}\%(filename)s.url"; Section: "InternetShortcut"; Key: "URL"; String: "%(url)s"

[Registry]
Root: HKCR; Subkey: ".tsk"; ValueType: string; ValueName: ""; ValueData: "TaskCoach"; Flags: uninsdeletevalue; Check: IsAdminLoggedOn
Root: HKCR; Subkey: "TaskCoach"; ValueType: string; ValueName: ""; ValueData: "%(name)s File"; Flags: uninsdeletekey; Check: IsAdminLoggedOn
Root: HKCR; Subkey: "TaskCoach\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\%(filename)s.EXE,0"; Check: IsAdminLoggedOn
Root: HKCR; Subkey: "TaskCoach\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\%(filename)s.EXE"" ""%%1"""; Check: IsAdminLoggedOn
Root: HKCU; Subkey: "Software\Classes\.tsk"; ValueType: string; ValueName: ""; ValueData: "TaskCoachFile"; Flags: uninsdeletevalue; Check: not IsAdminLoggedOn
Root: HKCU; Subkey: "Software\Classes\TaskCoachFile"; ValueType: string; ValueName: ""; ValueData: "%(name)s File"; Flags: uninsdeletekey; Check: not IsAdminLoggedOn
Root: HKCU; Subkey: "Software\Classes\TaskCoachFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\%(filename)s.EXE,0"; Check: not IsAdminLoggedOn
Root: HKCU; Subkey: "Software\Classes\TaskCoachFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\%(filename)s.EXE"" ""%%1"""; Check: not IsAdminLoggedOn

[Icons]
Name: "{group}\%(name)s"; Filename: "{app}\%(filename)s.exe"; WorkingDir: "{app}"
Name: "{group}\{cm:ProgramOnTheWeb,%(name)s}"; Filename: "{app}\%(filename)s.url"
Name: "{group}\{cm:UninstallProgram,%(name)s}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\%(name)s"; Filename: "{app}\%(filename)s.exe"; Tasks: desktopicon; WorkingDir: "{app}"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\%(name)s"; Filename: "{app}\%(filename)s.exe"; Tasks: quicklaunchicon; WorkingDir: "{app}"

[Run]
Filename: "{app}\%(filename)s.exe"; Description: "{cm:LaunchProgram,%(name)s}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\%(filename)s.url"
'''

def writeFile(filename, text, directory='.'):
    file = open(os.path.join(directory, filename), 'w')
    file.write(text)
    file.close()

def createDocumentation():
    import help
    writeFile('README.txt',  help.aboutText)
    writeFile('INSTALL.txt', help.installText)
    writeFile('LICENSE.txt', meta.licenseText)

def createInnoSetupScript():
    writeFile('taskcoach.iss', script%meta.metaDict, builddir)

if sys.argv[1] == 'py2exe':
    from distutils.core import setup
    import py2exe
    py2exeDistdir = '%s-%s-win32exe'%(meta.filename, meta.version)
    setupOptions.update({
        'windows' : [{ 'script' : 'taskcoach.pyw', 
            'other_resources' : [(24, 1, manifest)],
            'icon_resources': [(1, 'icons.in/taskcoach.ico')]}],
        'options' : {'py2exe' : {
            'compressed' : 1, 
            'includes' : ['xml.dom.minidom', 'gui.dialog.editor'],
            'excludes' : ['taskcoachlib'],
            'optimize' : 2, 
            'packages' : ['i18n'],
            'dist_dir' : os.path.join(builddir, py2exeDistdir)}},
        'data_files': [('', ['dist.in/gdiplus.dll', 'dist.in/MSVCP71.DLL'])]})
 
elif sys.argv[1] == 'py2app':
    from setuptools import setup
    setupOptions.update(dict(app=['taskcoach.py'], 
        setup_requires=['py2app'],
        options=dict(py2app=dict(argv_emulation=True, compressed=True,
            dist_dir=builddir, optimize=2, iconfile='icons.in/taskcoach.icns', 
            packages=['i18n'],
            plist=dict(CFBundleIconFile='taskcoach.icns')))))
else:
    from distutils.core import setup
    # On Fedora, to keep the rpm build process going when it finds 
    # unpackaged files you need to create a ~/.rpmmacros file 
    # containing the line '%_unpackaged_files_terminate_build 0'.


if __name__ == '__main__':
    for directory in builddir, distdir:
        if not os.path.exists(directory):
            os.mkdir(directory)
    createDocumentation()
    setup(**setupOptions)
    if sys.argv[1] == 'py2exe':
        createInnoSetupScript()
