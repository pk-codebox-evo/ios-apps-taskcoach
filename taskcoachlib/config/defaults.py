import meta

defaults = { \
'view': { \
    'tasklistviewercount': '1',
    'tasktreelistviewercount': '1',
    'categoryviewercount': '1',
    'effortlistviewercount': '1',
    'effortperdayviewercount': '0',
    'effortperweekviewercount': '0',
    'effortpermonthviewercount': '0',
    'noteviewercount': '0',
    'statusbar': 'True',
    'toolbar': '(32, 32)',
    'completedtasks': 'True',
    'inactivetasks': 'True',
    'activetasks': 'True',
    'overduetasks': 'True',
    'overbudgettasks': 'True',
    'compositetasks': 'True',
    'categories': 'False',
    'startdate': 'True',
    'duedate': 'True',
    'timeleft': 'False',
    'completiondate': 'False',
    'taskdescription': 'False',
    'categories': 'False',
    'budget': 'False',
    'totalbudget': 'False',
    'timespent': 'False',
    'totaltimespent': 'False',
    'budgetleft': 'False',
    'totalbudgetleft': 'False',
    'priority': 'False',
    'totalpriority': 'False',
    'reminder': 'False',
    'lastmodificationtime': 'False',
    'totallastmodificationtime': 'False',
    'hourlyfee': 'False',
    'fixedfee': 'False',
    'totalfixedfee': 'False',
    'revenue': 'False',
    'totalrevenue': 'False',
    'attachments': 'False',
    'alldatecolumns' : 'False',
    'allbudgetcolumns': 'False',
    'allfinancialcolumns': 'False',
    'efforttimespent': 'True',
    'totalefforttimespent': 'True',
    'effortrevenue': 'True',
    'totaleffortrevenue': 'True',
    'effortdescription': 'False',
    'tasksdue': 'Unlimited',
    'mainviewer': '0',
    'effortviewerineditor': '0',
    'language': 'en_US',
    'tasksearchfilterstring': '',
    'tasksearchfiltermatchcase': 'False',
    'taskcategoryfiltermatchall': 'True'},
'tasklistviewer': { \
    'sortby': 'dueDate',
    'sortascending': 'True',
    'sortbystatusfirst': 'True',
    'sortcasesensitive': 'True' },
'tasktreelistviewer': { \
    'sortby': 'dueDate',
    'sortascending': 'True',
    'sortbystatusfirst': 'True',
    'sortcasesensitive': 'True' },
'window': { \
    'size': '(600, 500)',
    'position': '(-1, -1)',
    'iconized': 'False',
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
    'duetodaytasks': '(255, 128, 0)'},
'version': { \
    'notified': meta.data.version,
    'notify': 'True'},
'behavior': { \
    'markparentcompletedwhenallchildrencompleted': 'True'},
'feature': { \
    'notes': 'False'}}
