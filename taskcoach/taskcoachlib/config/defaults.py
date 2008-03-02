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

import meta, sys, wx

defaults = { \
'view': { \
    'statusbar': 'True',
    'toolbar': '(22, 22)',
    'mainviewer': '0',               # Index of active viewer in main window
    'effortviewerintaskeditor': '0', # Index of active effort viewer in task editor
    'tasklistviewercount': '1',      # Number of task list viewers in main window
    'tasktreeviewercount': '0',      # (This viewer is currently not used)
    'tasktreelistviewercount': '1',  # Number of task tree list viewers in main window
    'categoryviewercount': '1',      # etc.
    'noteviewercount': '0',
    'effortlistviewercount': '1',
    'effortperdayviewercount': '1',
    'effortperweekviewercount': '0',
    'effortpermonthviewercount': '0',
    'language': 'en_US',
    'taskcategoryfiltermatchall': 'True',
    'descriptionpopups': 'True'},
'tasklistviewer': { \
    'title': '',
    'sortby': 'dueDate',
    'sortascending': 'True',
    'sortbystatusfirst': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'columns': "['startDate', 'dueDate']",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{'attachments': 28}",
    'tasksdue': 'Unlimited',
    'hidecompletedtasks': 'False',
    'hideinactivetasks': 'False',
    'hideactivetasks': 'False',
    'hideoverduetasks': 'False',
    'hideoverbudgettasks': 'False',
    'hidecompositetasks': 'False', },
'tasktreeviewer': { \
    'title': '',
    'sortby': 'dueDate',
    'sortascending': 'True',
    'sortbystatusfirst': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'tasksdue': 'Unlimited',
    'hidecompletedtasks': 'False',
    'hideinactivetasks': 'False',
    'hideactivetasks': 'False',
    'hideoverduetasks': 'False',
    'hideoverbudgettasks': 'False' },
'tasktreelistviewer': { \
    'title': '',
    'sortby': 'dueDate',
    'sortascending': 'True',
    'sortbystatusfirst': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'columns': "['startDate', 'dueDate']",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{'attachments': 28}",
    'tasksdue': 'Unlimited',
    'hidecompletedtasks': 'False',
    'hideinactivetasks': 'False',
    'hideactivetasks': 'False',
    'hideoverduetasks': 'False',
    'hideoverbudgettasks': 'False' },
'categoryviewer': { \
    'title': '',
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'noteviewer': { \
    'title': '',
    'sortby': 'subject',
    'sortascending': 'True',
    'sortcasesensitive': 'True',
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False',
    'columns': "[]",
    'columnsalwaysvisible': "['subject']",
    'columnwidths': "{}" },
'effortlistviewer': { \
    'title': '',
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortlistviewerintaskeditor': { \
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortperdayviewer': { \
    'title': '',
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortperdayviewerintaskeditor': { \
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortperweekviewer': { \
    'title': '',
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortperweekviewerintaskeditor': { \
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortpermonthviewer': { 
    'title': '',
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'effortpermonthviewerintaskeditor': { 
    'columns': "['timeSpent', 'revenue']",
    'columnsalwaysvisible': "['period', 'task']",
    'columnwidths': "{}",
    'searchfilterstring': '',
    'searchfiltermatchcase': 'False',
    'searchfilterincludesubitems': 'False' },
'window': { \
    'size': '(600, 500)',
    'position': '(-1, -1)',
    'iconized': 'False',
    'starticonized': 'WhenClosedIconized', # 'Never', 'Always', 'WhenClosedIconized'
    'splash': 'True',
    'hidewheniconized': 'False',
    'hidewhenclosed': 'False',
    'tips': 'True',
    'tipsindex': '0',
    'blinktaskbariconwhentrackingeffort': 'True' },
'file': { \
    'recentfiles': '[]',
    'maxrecentfiles': '4',
    'lastfile': '',
    'autosave': 'False',
    'backup': 'False',
    'saveinifileinprogramdir': 'False' },
'color': { \
    'activetasks': '(0, 0, 0)',
    'completedtasks': '(0, 255, 0)',
    'overduetasks': '(255, 0, 0)',
    'inactivetasks': '(192, 192, 192)',
    'duetodaytasks': '(255, 128, 0)' },
'editor': { \
    'maccheckspelling': 'True' },
'version': { \
    'python': '', # Filled in by the Settings class when saving the settings
    'wxpython': '', # Idem
    'pythonfrozen': '', # Idem
    'current': meta.data.version,
    'notified': meta.data.version,
    'notify': 'True' },
'behavior': { \
    'markparentcompletedwhenallchildrencompleted': 'True' },
'feature': { \
    'notes': 'True' }}
