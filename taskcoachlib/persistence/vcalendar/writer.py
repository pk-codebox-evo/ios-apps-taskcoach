
## Task Coach - Your friendly task manager
## Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
## Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>

## Task Coach is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.

## Task Coach is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

Writer to VCalendar format.

"""

from taskcoachlib.persistence.vcalendar import vcal


class VCalendarWriter(object):
    def __init__(self, fd):
        self.__fd = fd

    def write(self, viewer, selectionOnly=False):
        self.__fd.write('BEGIN:VCALENDAR\r\n')
        self.__fd.write('VERSION: 1.0\r\n')

        tree = viewer.isTreeViewer()
        if selectionOnly:
            selection = viewer.curselection()
            if tree:
                selection = extendedWithAncestors(selection)

        for task in viewer.visibleItems():
            if selectionOnly and task not in selection:
                continue
            self.__fd.write(vcal.VCalFromTask(task))

        self.__fd.write('END:VCALENDAR\r\n')
