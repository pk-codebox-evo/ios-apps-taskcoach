# Task Coach - Your friendly task manager
# Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
# 
# Task Coach is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Task Coach is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Makefile to create binary and source distributions and generate the 
# simple website (intermediate files are in ./build, distributions are
# put in ./dist, the files for the website end up in ./website.out)

PYTHON="python" # python should be on the path
DOT="dot"       # dot should be on the path

ifeq (CYGWIN_NT,$(findstring CYGWIN_NT,$(shell uname)))
    INNOSETUP="/cygdrive/c/Program Files/Inno Setup 5/ISCC.exe"
    EPYDOC=$(PYTHON) $(shell python -c "import os, sys; print \"'\" + os.path.join(os.path.split(sys.executable)[0], 'Scripts', 'epydoc.py') + \"'\"")
else
    EPYDOC="epydoc"
endif

TCVERSION=$(shell python -c "import taskcoachlib.meta.data as data; print data.version")

all: windist sdist website

windist: icons i18n
	$(PYTHON) make.py py2exe
	$(INNOSETUP) build/taskcoach.iss

sdist: icons changes i18n dist/TaskCoach-$(TCVERSION).tar.gz

dist/TaskCoach-$(TCVERSION).tar.gz:
	$(PYTHON) make.py sdist --formats=zip,gztar --no-prune

rpm: icons changes i18n
	$(PYTHON) make.py bdist_rpm --requires "python2.5,python-wxgtk2.8" --group "Applications/Productivity"

fedora: icons changes i18n
	$(PYTHON) make.py bdist_rpm_fedora 

deb: sdist
	$(PYTHON) make.py bdist_deb --sdist=dist/TaskCoach-$(TCVERSION).tar.gz

dmg: icons i18n
	$(PYTHON) make.py py2app
	hdiutil create -ov -imagekey zlib-level=9 -srcfolder build/TaskCoach.app dist/TaskCoach-$(TCVERSION).dmg

icons: taskcoachlib/gui/icons.py

templates: taskcoachlib/persistence/xml/templates.py

taskcoachlib/gui/icons.py: icons.in/iconmap.py icons.in/nuvola.zip icons.in/splash.png
	cd icons.in; $(PYTHON) make.py

taskcoachlib/persistence/xml/templates.py:
	cd templates.in; $(PYTHON) make.py

website: changes
	cd website.in; $(PYTHON) make.py; cd ..
	$(PYTHON) tools/webchecker.py website.out/index.html

epydoc:
	$(EPYDOC) --parse-only -o epydoc.out taskcoachlib taskcoach.py

dot:
	$(PYTHON) dot.py taskcoachlib/gui/viewer > dot.out/viewer.dot
	$(DOT) -Tpng -o"dot.out/viewer.png" -Kdot dot.out/viewer.dot

i18n: templates taskcoachlib/i18n/nl.py

taskcoachlib/i18n/nl.py: i18n.in/messages.pot $(shell find i18n.in -name '*.po')
	cd i18n.in; $(PYTHON) make.py

i18n.in/messages.pot: $(shell find taskcoachlib -name '*.py' | grep -v i18n)
	$(PYTHON) tools/pygettext.py --output-dir i18n.in taskcoachlib

changes:
	$(PYTHON) changes.in/make.py text > CHANGES.txt
	$(PYTHON) changes.in/make.py html > website.in/changes.html
 
unittests: icons templates
	cd tests; $(PYTHON) test.py

alltests: icons i18n
	cd tests; $(PYTHON) test.py --alltests

releasetests: icons templates
	cd tests; $(PYTHON) test.py --releasetests --no-unittests

integrationtests: icons i18n
	cd tests; $(PYTHON) test.py --integrationtests --no-unittests

languagetests: i18n
	cd tests; $(PYTHON) test.py integrationtests/TranslationIntegrityTest.py

# FIXME: disttests should depend on either windist, deb, rpm or dmg...
disttests:
	cd tests; $(PYTHON) test.py --disttests --no-unittests


CLEANFILES=build dist website.out dot.out MANIFEST README.txt INSTALL.txt LICENSE.txt CHANGES.txt @webchecker.pickle .profile
REALLYCLEANFILES=taskcoachlib/gui/icons.py taskcoachlib/persistence/templates.py \
	taskcoachlib/i18n/??_??.py .\#* */.\#* */*/.\#*

clean:
	$(PYTHON) make.py clean
	rm -rf $(CLEANFILES)

reallyclean:
	$(PYTHON) make.py clean --really-clean
	rm -rf $(CLEANFILES) $(REALLYCLEANFILES)

nuke:
	$(PYTHON) nuke.py
