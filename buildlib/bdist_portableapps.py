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

import os, glob, zipfile
from distutils.core import Command
from distutils.file_util import copy_file
from distutils import log, errors


class bdist_portableapps(Command, object):
    
    description = 'create a PortableApps package'
    
    user_options = [
        ('bdist-base=', None, 
         'base directory for creating built distributions [build]'),
        ('dist-dir=', 'd', 'directory to put final package files in [dist]'),
        ('name=', None, 'name of the application'),
        ('version=', None, 'version of the application'),
        ('license=', None, 'license (title) of the application'),
        ('url=', None, 'url of the application homepage'),
        ('filename=', None, 'filename of the application without extension'),
        ('date=', None, 'the release date')]
    
    def initialize_options(self):
        self.bdist_base = 'build'
        self.dist_dir = 'dist'
        self.name = self.version = self.license = self.url = self.filename = self.date = None
    
    def finalize_options(self):
        mandatoryOptions = [('name', 'the name of the application'),
                            ('version', 'the version of the application'),
                            ('license', 'the title of the license'),
                            ('url', 'the url of the application homepage'),
                            ('filename', 'the filename of the application without extension'),
                            ('date', 'the release date')]
        for option, description in mandatoryOptions:
            if not getattr(self, option):
                raise errors.DistutilsOptionError, \
                    'you must provide %s (--%s)'%(description, option)

    def run(self):
        self.bdist_base_pa = os.path.join(self.bdist_base, 'TaskCoachPortable')
        self.create_portableapps_paths()
        self.copy_launcher()
        self.copy_appinfo()
        self.copy_defaultdata()
        self.copy_bin()
        self.copy_other()
        #self.zip()
        
    def create_portableapps_paths(self):
        for pathComponents in [('App', 'AppInfo'),
                               ('App', 'DefaultData', 'settings'),
                               ('App', 'TaskCoach'), 
                               ('Data', ),
                               ('Other', 'Help', 'images'), 
                               ('Other', 'Source')]:
            path = os.path.join(self.bdist_base_pa, *pathComponents)
            if not os.path.exists(path):
                os.makedirs(path)
                    
    def copy_launcher(self):
        launcher_src = os.path.join('build.in', 'portableapps')
        self.copy_files(launcher_src, self.bdist_base_pa)
               
    def copy_appinfo(self):
        src = os.path.join('build.in', 'portableapps', 'App', 'AppInfo')
        dest = os.path.join(self.bdist_base_pa, 'App', 'AppInfo')
        self.copy_files(src, dest)
        
    def copy_defaultdata(self):
        src = os.path.join('build.in', 'portableapps', 'App', 'DefaultData', 'settings')
        dest = os.path.join(self.bdist_base_pa, 'App', 'DefaultData', 'settings')
        self.copy_files(src, dest)

    def copy_bin(self):
        src = os.path.join(self.bdist_base, 'TaskCoach-%s-win32exe'%self.version)
        dest = os.path.join(self.bdist_base_pa, 'App', 'TaskCoach')
        self.copy_files(src, dest, copy_recursively=True)
        
    def copy_other(self):
        src = os.path.join('build.in', 'portableapps', 'Other')
        dest = os.path.join(self.bdist_base_pa, 'Other')
        self.copy_files(src, dest, copy_recursively=True)
        
            
    def copy_files(self, src_dir, dest_dir, copy_recursively=False):
        if not os.path.exists(dest_dir):
            os.mkdir(dest_dir)
        for entry in os.listdir(src_dir):
            abs_entry = os.path.join(src_dir, entry)
            if os.path.isfile(abs_entry):
                if os.path.splitext(abs_entry)[1] in ('.txt', '.ini'):
                    self.copy_and_expand(abs_entry, dest_dir)
                else:
                    copy_file(abs_entry, dest_dir)
            elif os.path.isdir(abs_entry) and copy_recursively:
                self.copy_files(abs_entry, os.path.join(dest_dir, entry), copy_recursively)
                
    def copy_and_expand(self, src_filename, dest_dir):
        log.info('copying and expanding %s to %s'%(src_filename, dest_dir))
        src_file = file(src_filename, 'rb')
        contents = src_file.read()
        src_file.close()
        contents = contents%self.__dict__
        dest_filename = os.path.join(dest_dir, os.path.basename(src_filename))
        dest_file = file(dest_filename, 'wb')
        dest_file.write(contents)
        dest_file.close()
        
    def zip(self):
        archive_filename = os.path.join(self.dist_dir, 'X-TaskCoach_%s_rev1.zip'%self.version)
        archive = zipfile.ZipFile(archive_filename, 'w', zipfile.ZIP_DEFLATED)
        for dirpath, dirnames, filenames in os.walk(self.bdist_base_wpp):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                arcname = filepath[len(self.bdist_base_wpp):]
                archive.write(filepath, arcname)
        archive.close()