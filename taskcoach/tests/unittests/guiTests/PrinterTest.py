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

import wx
import test
from taskcoachlib import gui, config


class PrinterTest(test.TestCase):
    def setUp(self):
        super(PrinterTest, self).setUp()
        self.settings = config.Settings(load=False)
        self.margins = dict(top=1, left=2, bottom=3, right=4)
        self.printerSettings = gui.printer.PrinterSettings(self.settings)
        self.pageSetupData = wx.PageSetupDialogData()

    def tearDown(self):
        super(PrinterTest, self).tearDown()
        gui.printer.PrinterSettings.deleteInstance()
 
    def testInitialSettings(self):
        printerSettings = self.printerSettings
        self.assertEqual(wx.Point(0, 0), printerSettings.GetMarginTopLeft())
        self.assertEqual(0, printerSettings.GetPaperId())
        self.assertEqual(wx.PORTRAIT, printerSettings.GetOrientation())

    def testSetMargin(self):
        self.pageSetupData.SetMarginTopLeft(wx.Point(10, 1))
        self.printerSettings.updatePageSetupData(self.pageSetupData)
        self.assertEqual(wx.Point(10, 1), 
                         self.printerSettings.GetMarginTopLeft())

    def testDefaultMarginsFromSettings(self):
        settings = self.settings
        for margin in self.margins:
            self.assertEqual(0, settings.getint('printer', 'margin_'+margin))

    def testSetPaperId(self):
        self.pageSetupData.SetPaperId(1)
        self.printerSettings.updatePageSetupData(self.pageSetupData)
        self.assertEqual(1, self.printerSettings.GetPaperId())

    def testDefaultPaperIdFromSettings(self):
        self.assertEqual(0, self.settings.getint('printer', 'paper_id'))

    def testSetOrientation(self):
        self.pageSetupData.GetPrintData().SetOrientation(wx.LANDSCAPE)
        self.printerSettings.updatePageSetupData(self.pageSetupData)
        self.assertEqual(wx.LANDSCAPE, self.printerSettings.GetOrientation())

    def testDefaultOrientationFromSettings(self):
        self.assertEqual(wx.PORTRAIT, 
                         self.settings.getint('printer', 'orientation'))

    def testUpdateMarginsInPageSetupDataUpdatesSettings(self):
        self.pageSetupData.SetMarginTopLeft(wx.Point(self.margins['top'], 
                                                     self.margins['left']))
        self.pageSetupData.SetMarginBottomRight(wx.Point(self.margins['bottom'], 
                                                         self.margins['right']))
        self.printerSettings.updatePageSetupData(self.pageSetupData)
        for margin in self.margins:
            self.assertEqual(self.margins[margin], 
                             self.settings.getint('printer', 'margin_'+margin))

    def testUpdatePaperIdInPageSetupDataUpdatesSettings(self):
        self.pageSetupData.SetPaperId(1)
        self.printerSettings.updatePageSetupData(self.pageSetupData)
        self.assertEqual(1, self.settings.getint('printer', 'paper_id'))

    def testUpdateOrientationInPageSetupDataUpdatesSettings(self):
        self.pageSetupData.GetPrintData().SetOrientation(wx.LANDSCAPE)
        self.printerSettings.updatePageSetupData(self.pageSetupData)
        self.assertEqual(wx.LANDSCAPE, 
                         self.settings.getint('printer', 'orientation'))

    def testMarginsInPageSetupDataAreUpdatedFromSettings(self):
        gui.printer.PrinterSettings.deleteInstance()
        for margin in self.margins:
            self.settings.set('printer', 'margin_'+margin, 
                              str(self.margins[margin]))
        printerSettings = gui.printer.PrinterSettings(self.settings)
        self.assertEqual(wx.Point(1, 2), printerSettings.GetMarginTopLeft())
        self.assertEqual(wx.Point(3, 4), printerSettings.GetMarginBottomRight())
        
    def testPaperIdInPageSetupDataIsUpdatedFromSettings(self):
        gui.printer.PrinterSettings.deleteInstance()
        self.settings.set('printer', 'paper_id', '1')
        printerSettings = gui.printer.PrinterSettings(self.settings)
        self.assertEqual(1, printerSettings.GetPaperId())

    def testOrientationInPageSetupDataIsUpdatedFromSettings(self):
        gui.printer.PrinterSettings.deleteInstance()
        self.settings.set('printer', 'orientation', str(wx.LANDSCAPE))
        printerSettings = gui.printer.PrinterSettings(self.settings)
        self.assertEqual(wx.LANDSCAPE, printerSettings.GetOrientation())


class HTMLPrintoutTest(test.TestCase):
    def testCreate(self):
        class DummyViewer(object):
            def title(self):
                return 'title'
            def visibleColumns(self):
                return []
            def isShowingTasks(self):
                return True
            def isTreeViewer(self):
                return False
            def visibleItems(self):
                return []
            
        printOut = gui.printer.HTMLPrintout(DummyViewer(), 
                                            config.Settings(load=False))
        