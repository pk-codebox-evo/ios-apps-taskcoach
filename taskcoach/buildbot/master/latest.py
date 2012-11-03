#!/usr/bin/python

import os, re, sys

def findLatest(path, valid):
    rx = re.compile(r'(.*)(\d+\.\d+\.\d+\.\d+)(.*)')

    results = dict()

    for name in os.listdir(path):
        if (name.lower().startswith('taskcoach') or name.lower().startswith('x-taskcoach')) and valid(name):
            mt = rx.search(name)
            if mt:
                ls = results.get((mt.group(1), mt.group(3)), [])
                ls.append(map(int, mt.group(2).split('.')))
                results[(mt.group(1), mt.group(3))] = ls

    packages = []

    for (part1, part3), versions in results.items():
        versions.sort()
        packages.append('%s%s%s' % (part1, '.'.join(map(str, versions[-1])), part3))

    packages.sort()

    return packages


def listPath(path):
    def isSource(name):
        if name.endswith('.tar.gz') or name.endswith('.src.rpm'):
            return True
        if name.endswith('.zip'):
            return not name.endswith('_rev1.zip')
        return False

    changelog = os.path.join(path, 'changelog_content')
    if os.path.exists(changelog):
        print '<pre>'
        print file(changelog, 'rb').read()
        print '</pre>'

    print '<h2>Sources</h2>'
    print '<ul>'

    for pkgname in findLatest(path, isSource):
        if path == '.' or path == 'all':
            print '<li><a href="http://www.fraca7.net/TaskCoach-packages/%s">%s</a></li>' % (pkgname, pkgname)
        else:
            print '<li><a href="http://www.fraca7.net/TaskCoach-packages/%s/%s">%s</a></li>' % (path, pkgname, pkgname)

    print '</ul>'

    print '<h2>Binaries</h2>'
    print '<ul>'

    for pkgname in findLatest(path, lambda x: not isSource(x)):
        if path == '.' or path == 'all':
            print '<li><a href="http://www.fraca7.net/TaskCoach-packages/%s">%s</a></li>' % (pkgname, pkgname)
        else:
            print '<li><a href="http://www.fraca7.net/TaskCoach-packages/%s/%s">%s</a></li>' % (path, pkgname, pkgname)

    print '</ul>'

def main(path):
    print 'Content-type: text/html'
    print

    print '<html><head><title>Latest Task Coach builds</title>'
    print '<style type="text/css" media="screen">@import "default.css";</style>'
    print '</head></body>'

    if path == '.' or path == 'all':
        print '<h1>New developments (from trunk)</h1>'
        listPath('.')

    if path != '.':
        for name in os.listdir(path):
            if name.startswith('Release') or name.startswith('Feature'):
                fname = os.path.join(path, name)
                if os.path.isdir(fname):
                    if name.startswith('Release'):
                        print '<h1>Bug fixes (from %s)</h1>' % name
                    else:
                        print '<h1>Experimental features (from %s)</h1>' % name
                    listPath(fname)

    print '<a href="http://www.taskcoach.org/download.html>Back to Task Coach downloads</a>'

    print '</body></html>'

if __name__ == '__main__':
    if sys.argv[0].endswith('latest_features.py'):
        main('.')
    elif sys.argv[0].endswith('latest_bugfixes.py'):
        main('branches')
    else:
        main('all')

