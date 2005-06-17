# Makefile to create binary and source distributions and generate the 
# simple website (intermediate files are in ./build, the files for the
# website end up in ./dist)

PYTHON="/cygdrive/c/Program Files/Python24/python.exe"
INNOSETUP="/cygdrive/c/Program Files/Inno Setup 5/ISCC.exe"
WEBCHECKER="c:/Program Files/Python24/Tools/webchecker/webchecker.py" 
GETTEXT="c:/Program Files/Python24/Tools/i18n/pygettext.py"

all: windist sdist website

windist: icons
	$(PYTHON) make.py py2exe
	$(INNOSETUP) build/taskcoach.iss

wininstaller:
	$(INNOSETUP) build/taskcoach.iss

sdist: icons changes
	$(PYTHON) make.py sdist --formats=zip,gztar --no-prune

icons:
	cd icons.in; $(PYTHON) make.py

website: changes
	cd website.in; $(PYTHON) make.py; cd ..
	$(PYTHON) $(WEBCHECKER) dist/index.html

i18n:
	$(PYTHON) $(GETTEXT) --output-dir i18n.in taskcoachlib
	cd i18n.in; $(PYTHON) make.py

changes:
	$(PYTHON) changes.in/make.py text > CHANGES.txt
	$(PYTHON) changes.in/make.py html > website.in/changes.html
 

clean:
	rm -rf *.pyc */*.pyc */*/*.pyc dist build MANIFEST README.txt INSTALL.txt LICENSE.txt CHANGES.txt @webchecker.pickle

