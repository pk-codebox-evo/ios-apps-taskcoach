'''
Task Coach - Your friendly task manager
Copyright (C) 2013 Task Coach developers <developers@taskcoach.org>

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

import os
from .base import Backend
from taskcoachlib.persistence.xml import reader, writer
from taskcoachlib.changes import sync
from taskcoachlib.domain import task, note, category
from taskcoachlib.thirdparty.guid import generate


class FileBackend(Backend):
    def __init__(self, store):
        super(FileBackend, self).__init__(store)
        self.__filename = ''
        self.__guid = generate()

    # XXXTODO: locking

    def filename(self):
        return self.__filename

    def setFilename(self, filename):
        self.__filename = filename

    def exists(self, suffix=''):
        return self.__filename and os.path.exists(self.__filename + suffix)

    def clear(self, store):
        if self.__filename:
            self.lock()
            try:
                deltaName = self.__filename + '.delta'
                if os.path.exists(deltaName):
                    with file(deltaName, 'rU') as fd:
                        allChanges = reader.ChangesXMLReader(fd).read()
                    if self.monitor().guid() in allChanges:
                        del allChanges[self.monitor().guid()]
                        with file(deltaName, 'wb') as fd:
                            writer.ChangesXMLWriter(fd).write(allChanges)
            finally:
                self.unlock()
        super(FileBackend, self).clear(store)

    def sync(self, store):
        self.lock()
        try:
            self.monitor().freeze()

            try:
                if self.exists():
                    with file(self.__filename, 'rU') as fd:
                        tasks, categories, notes, allChanges, guid = reader.XMLReader(fd).read()
                    self.__guid = guid
                else:
                    tasks, categories, notes, allChanges = [], [], [], {}

                tasks = task.TaskList(tasks)
                categories = category.CategoryList(categories)
                notes = note.NoteContainer(notes)

                for devGUID, changes in allChanges.items():
                    if devGUID != self.monitor().guid():
                        changes.merge(self.monitor())

                synchronizer = sync.ChangeSynchronizer(self.monitor(), allChanges)
                synchronizer.sync([(store.categories(), categories),
                                   (store.tasks(), tasks),
                                   (store.notes(), notes)])

                allChanges[self.monitor().guid()] = self.monitor()
            finally:
                self.monitor().thaw()

            #self.monitor().resetAllChanges()

            with file(self.__filename + '-tmp', 'wb') as fd:
                writer.XMLWriter(fd).write(store.tasks(), store.categories(), store.notes(), self.__guid)
            with file(self.__filename + '.delta-tmp', 'wb') as fd:
                writer.ChangesXMLWriter(fd).write(allChanges)
            if self.exists():
                os.remove(self.__filename)
            if self.exists('.delta'):
                os.remove(self.__filename + '.delta')
            os.rename(self.__filename + '-tmp', self.__filename)
            os.rename(self.__filename + '.delta-tmp', self.__filename + '.delta')
        finally:
            self.unlock()