# -*- coding: UTF-8 -*-
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

import test
from taskcoachlib.gui.dialog import entry 


class LocalConv(dict):
    def __init__(self, decimal_point='.', thousands_sep=',', grouping=None):
        super(LocalConv, self).__init__()
        self.update(dict(decimal_point=decimal_point,
                         thousands_sep=thousands_sep,
                         grouping=grouping or []))


class AmountEntryTest(test.wxTestCase):
    def setUp(self):
        super(AmountEntryTest, self).setUp()
        self.amountEntry = entry.AmountEntry(self.frame)

    def testCreate(self):
        self.assertEqual(0.0, self.amountEntry.get())

    def testSetValue(self):
        self.amountEntry.set(1.0)
        self.assertEqual(1.0, self.amountEntry.get())

    def testDefaultLocalConventions(self):
        entry.AmountEntry(self.frame, localeconv=LocalConv())

    def testCommaAsDecimalSepAndNoGrouping(self):
        entry.AmountEntry(self.frame, localeconv=LocalConv(decimal_point=','))

    def testCommaAsDecimalSepAndGrouping(self):
        entry.AmountEntry(self.frame, localeconv=LocalConv(decimal_point=',',
            grouping=[3,3,3]))

    def testCommaAsBothDecimalSepAndThousandsSepButNoGrouping(self):
        entry.AmountEntry(self.frame, localeconv=LocalConv(decimal_point=',',
            thousands_sep=','))

    def testCommaAsBothDecimalSepAndThousandsSepAndGrouping(self):
        entry.AmountEntry(self.frame, localeconv=LocalConv(decimal_point=',',
            thousands_sep=',', grouping=[3,3,3]))

    def testSpaceIsNotAllowedAsDecimalPoint(self):
        try:
            entry.AmountEntry(self.frame, 
                              localeconv=LocalConv(decimal_point=' '))
            self.fail('Expected ValueError') # pragma: no cover
        except ValueError:
            pass

    def testNonAsciiDecimalPoint(self):
        entry.AmountEntry(self.frame, localeconv=LocalConv(decimal_point=u'é'))
        
    def testNonAsciiThousandsSeparator(self):
        entry.AmountEntry(self.frame, localeconv=LocalConv(thousands_sep=u'é', 
                                                           grouping=[3,3,3]))

    def testMultiCharThousandsSeparator(self):
        entry.AmountEntry(self.frame, localeconv=LocalConv(thousands_sep='..'))
