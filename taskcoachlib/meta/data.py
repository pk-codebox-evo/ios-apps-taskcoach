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

import re

name = 'Task Coach'
description = 'Your friendly task manager'
version = '0.70.0'
release_month = 'March'
release_month_nr = '%02d'%(['January', 'February', 'March', 'April', 'May', 
                    'June', 'July', 'August', 'September', 'October', 
                    'November', 'December'].index(release_month) + 1)
release_day = '0'
release_day_nr = '%02d'%int(release_day)
release_year = '2008'
release_status = 'Alpha'
date = release_month + ' ' + release_day + ', ' + release_year
long_description = 'Task Coach is a simple open source todo manager to manage' \
' personal tasks and todo lists. It grew out of a frustration that ' \
'well-known task managers, such as those provided with Outlook or Lotus ' \
'Notes, do not provide facilities for composite tasks. Often, tasks and ' \
'other things todo consist of several activities. Task Coach is designed ' \
'to deal with composite tasks. '
keywords = 'task manager, todo list, pim, time registration, track effort'
author_first = 'Frank'
author_last = 'Niessink'
author = author_first + ' ' + author_last
author_email = 'frank@niessink.com'
filename = 'TaskCoach'
filename_lower = filename.lower()
url = 'http://www.taskcoach.org/'
screenshot = url + 'screenshot-0.62-treeview.png'
icon = url + 'taskcoach.png'
pad = url + 'pad.xml'
download = url + 'download.html'
dist_download_prefix = 'http://downloads.sourceforge.net/%s'%filename_lower
copyright = 'Copyright (C) 2004-%s %s'%(release_year, author)
license = 'GNU General Public License version 3 or any later version'
license_notice = '''Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''
license_notice_html = '<p>%s</p>'%license_notice.replace('\n\n', '</p><p>')

platform = 'Any'
pythonversion = '2.4'
wxpythonversion = '2.8.6.0-unicode'
languages = {
    'English': None, 
    'Brazilian Portuguese': 'pt_BR',
    'Breton': 'br',
    'Bulgarian': 'bg',
    'Czech': 'cs',
    'Danish': 'da',
    'Dutch': 'nl',
    'French': 'fr', 
    'German': 'de',
    'Italian': 'it',
    'Latvian': 'lv',
    'Polish': 'pl',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'ChineseSimplified': 'zh_CN',
    'ChineseTraditional': 'zh_TW',
    'Japanese': 'ja',
    'Spanish': 'es',
    'Swedish': 'sv',
    'Slovak': 'sk',
    'Hungarian': 'hu',
    'Hebrew': 'he'}
languages_list = ','.join(languages.keys())

def __createDict(locals):
    ''' Provide the local variables as a dictionary for use in string
        formatting. '''
    metaDict = {}
    for key in locals:
        if not key.startswith('__'):
            metaDict[key] = locals[key]
    return metaDict

metaDict = __createDict(locals())

