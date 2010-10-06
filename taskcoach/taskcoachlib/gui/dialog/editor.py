# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>
Copyright (C) 2008 Rob McMullen <rob.mcmullen@gmail.com>
Copyright (C) 2008 Carl Zmola <zmola@acm.org>

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

import wx, os.path
from taskcoachlib import widgets, patterns, command
from taskcoachlib.gui import viewer, artprovider
from taskcoachlib.i18n import _
from taskcoachlib.domain import task, date, note, attachment
from taskcoachlib.gui.dialog import entry


class Page(widgets.BookPage):
    columns = 2
    
    def __init__(self, items, *args, **kwargs):
        self.items = items
        super(Page, self).__init__(columns=self.columns, *args, **kwargs)
        self.addEntries()
        self.fit()
        
    def addEntries(self):
        raise NotImplementedError
        
    def entries(self):
        ''' A mapping of names of columns to entries on this editor page. '''
        return dict()
    
    def setFocusOnEntry(self, columnName):
        try:
            theEntry = self.entries()[columnName]
        except KeyError:
            theEntry = self.entries()['firstEntry']
        try:
            theEntry.SetSelection(-1, -1) # Select all text
        except (AttributeError, TypeError):
            pass # Not a TextCtrl
        theEntry.SetFocus()


class SubjectPage(Page):        
    pageName = 'subject'
    pageTitle = _('Description')
    pageIcon = 'pencil_icon'
    
    def addEntries(self):
        self.addSubjectEntry()
        self.addDescriptionEntry()
        
    def addSubjectEntry(self):
        # pylint: disable-msg=W0201
        self._currentSubject = self.items[0].subject() if len(self.items) == 1 else _('Edit to change all subjects')
        self._subjectEntry = widgets.SingleLineTextCtrl(self, self._currentSubject)
        self._subjectEntry.Bind(wx.EVT_KILL_FOCUS, self.onSubjectEdited)
        self.addEntry(_('Subject'), self._subjectEntry)
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onSubjectChanged, 
                                                  eventType=self.items[0].subjectChangedEventType(),
                                                  eventSource=self.items[0])

    def onSubjectEdited(self, event):
        event.Skip()
        newSubject = self._subjectEntry.GetValue()
        if newSubject != self._currentSubject:
            command.EditSubjectCommand(None, self.items, subject=newSubject).do()
            self._currentSubject = newSubject
            
    def onSubjectChanged(self, event):
        newSubject = event.value()
        if newSubject != self._currentSubject:
            self._currentSubject = newSubject 
            self.setSubject(newSubject)

    def setSubject(self, subject):
        self._subjectEntry.SetValue(subject)
            
    def addDescriptionEntry(self):
        # pylint: disable-msg=W0201
        self._currentDescription = self.items[0].description() if len(self.items) == 1 else _('Edit to change all descriptions')
        self._descriptionEntry = widgets.MultiLineTextCtrl(self, self._currentDescription)
        self._descriptionEntry.Bind(wx.EVT_KILL_FOCUS, self.onDescriptionEdited)
        self._descriptionEntry.SetSizeHints(450, 150)
        self.addEntry(_('Description'), self._descriptionEntry, growable=True)
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onDescriptionChanged,
                                                  eventType=self.items[0].descriptionChangedEventType(),
                                                  eventSource=self.items[0])
        
    def onDescriptionEdited(self, event):
        event.Skip()
        newDescription = self._descriptionEntry.GetValue()
        if newDescription != self._currentDescription:
            command.EditDescriptionCommand(None, self.items, description=newDescription).do()
            self._currentDescription = newDescription
            
    def onDescriptionChanged(self, event):
        newDescription = event.value()
        if newDescription != self._currentDescription:
            self._currentDescription = newDescription
            self.setDescription(newDescription)
        
    def setDescription(self, description):
        self._descriptionEntry.SetValue(description)
                
    def entries(self):
        return dict(firstEntry=self._subjectEntry,
                    subject=self._subjectEntry, 
                    description=self._descriptionEntry)

    
class TaskSubjectPage(SubjectPage):
    def addEntries(self):
        super(TaskSubjectPage, self).addEntries()
        self.addPriorityEntry()
         
    def addPriorityEntry(self):
        # pylint: disable-msg=W0201
        self._currentPriority = self.items[0].priority() if len(self.items) == 1 else 0
        self._priorityEntry = widgets.SpinCtrl(self, size=(100, -1),
            value=str(self._currentPriority), initial=self._currentPriority)
        self._priorityEntry.Bind(wx.EVT_SPINCTRL, self.onPriorityEdited)
        self.addEntry(_('Priority'), self._priorityEntry, flags=[None, wx.ALL])
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onPriorityChanged,
                                                  eventType='task.priority',
                                                  eventSource=self.items[0])
    
    def onPriorityEdited(self, event):
        event.Skip()
        newPriority = self._priorityEntry.GetValue()
        if newPriority != self._currentPriority:
            command.EditPriorityCommand(None, self.items, priority=newPriority).do()
            self._currentPriority = newPriority
            
    def onPriorityChanged(self, event):
        newPriority = event.value()
        if newPriority != self._currentPriority:
            self._currentPriority = newPriority
            self._priorityEntry.SetValue(newPriority)
            
    def entries(self):
        entries = super(TaskSubjectPage, self).entries()
        entries['priority'] = self._priorityEntry
        return entries
            

class CategorySubjectPage(SubjectPage):
    def addEntries(self):
        super(CategorySubjectPage, self).addEntries()
        self.addExclusiveSubcategoriesEntry()
       
    def addExclusiveSubcategoriesEntry(self):
        # pylint: disable-msg=W0201
        self._currentExclusivity = self.items[0].hasExclusiveSubcategories() if len(self.items) == 1 else False
        self._exclusiveSubcategoriesCheckBox = \
            wx.CheckBox(self, label=_('Mutually exclusive')) 
        self._exclusiveSubcategoriesCheckBox.SetValue(self._currentExclusivity)
        self._exclusiveSubcategoriesCheckBox.Bind(wx.EVT_CHECKBOX, 
                                                  self.onExclusivityEdited)
        self.addEntry(_('Subcategories'), self._exclusiveSubcategoriesCheckBox,
                      flags=[None, wx.ALL])
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onExclusivityChanged, 
                                                  eventType=self.items[0].exclusiveSubcategoriesChangedEventType(), 
                                                  eventSource=self.items[0])
        
    def onExclusivityEdited(self, event):
        event.Skip()
        newExclusivity = self._exclusiveSubcategoriesCheckBox.GetValue()
        if newExclusivity != self._currentExclusivity:
            self._currentExclusivity = newExclusivity
            command.EditExclusiveSubcategoriesCommand(None, self.items, 
                                                      exclusivity=newExclusivity).do()
                    
    def onExclusivityChanged(self, event):
        newExclusivity = event.value()
        if newExclusivity != self._currentExclusivity:
            self._currentExclusivity = newExclusivity
            self._exclusiveSubcategoriesCheckBox.SetValue(newExclusivity)
            

class AttachmentSubjectPage(SubjectPage):
    def __init__(self, attachments, parent, basePath, *args, **kwargs):
        super(AttachmentSubjectPage, self).__init__(attachments, parent, 
                                                    *args, **kwargs)
        self.basePath = basePath
        
    def addEntries(self):
        # Override addEntries to insert a location entry between the subject
        # and description entries 
        self.addSubjectEntry()
        self.addLocationEntry()
        self.addDescriptionEntry()

    def addLocationEntry(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        # pylint: disable-msg=W0201
        self._currentLocation = self.items[0].location() if len(self.items) == 1 else _('Edit to change location of all attachments')
        self._locationEntry = widgets.SingleLineTextCtrl(panel, self._currentLocation)
        self._locationEntry.Bind(wx.EVT_KILL_FOCUS, self.onLocationEdited)
        sizer.Add(self._locationEntry, 1, wx.ALL, 3)
        if all(item.type_ == 'file' for item in self.items):
            button = wx.Button(panel, wx.ID_ANY, _('Browse'))
            sizer.Add(button, 0, wx.ALL, 3)
            wx.EVT_BUTTON(button, wx.ID_ANY, self.onSelectLocation)
        panel.SetSizer(sizer)
        self.addEntry(_('Location'), panel, flags=[None, wx.ALL|wx.EXPAND])
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onLocationChanged,
                                                  eventType=self.items[0].locationChangedEventType(),
                                                  eventSource=self.items[0])
        
    def onLocationEdited(self, event):
        event.Skip()
        newLocation = self._locationEntry.GetValue()
        if newLocation != self._currentLocation:
            self._currentLocation = newLocation
            command.EditAttachmentLocationCommand(None, self.items, location=newLocation).do()

    def onLocationChanged(self, event):
        newLocation = event.value()
        if newLocation != self._currentLocation:
            self._currentLocation = newLocation
            self._locationEntry.SetValue(newLocation)
            
    def onSelectLocation(self, event): # pylint: disable-msg=W0613
        if self.items[0].type_ == 'file':
            basePath = os.path.split(self.items[0].normalizedLocation())[0]
        else:
            basePath = os.getcwd()

        filename = widgets.AttachmentSelector(default_path=basePath)

        if filename:
            if self.basePath:
                filename = attachment.getRelativePath(filename, self.basePath)
            self._subjectEntry.SetValue(os.path.split(filename)[-1])
            self._locationEntry.SetValue(filename)
            self.onSubjectEdited(event)
            self.onLocationEdited(event)
        

class AppearancePage(Page):
    pageName = 'appearance'
    pageTitle = _('Appearance')
    pageIcon = 'palette_icon'
    columns = 5
    
    def addEntries(self):
        self.addColorEntries()
        self.addFontEntry()
        self.addIconEntry()
        
    def addColorEntries(self):
        self.addFgColorEntry()
        self.addBgColorEntry()
        
    def addFgColorEntry(self):
        self.addColorEntry(_('Foreground color'), 'foreground', wx.BLACK)

    def addBgColorEntry(self):
        self.addColorEntry(_('Background color'), 'background', wx.WHITE)
        
    def addColorEntry(self, labelText, colorType, defaultColor):
        checkBox = wx.CheckBox(self, label=_('Use color:'))
        setattr(self, '_%sColorCheckBox'%colorType, checkBox)
        currentColor = getattr(self.items[0], '%sColor'%colorType)(recursive=False) if len(self.items) == 1 else None
        setattr(self, '_current%sColor'%colorType.capitalize(), currentColor)
        checkBox.SetValue(currentColor is not None)
        checkBoxHandlerName = 'on%sColourCheckBoxChecked'%colorType.capitalize()
        checkBoxHandler = getattr(self, checkBoxHandlerName)
        checkBox.Bind(wx.EVT_CHECKBOX, checkBoxHandler)
        # wx.ColourPickerCtrl on Mac OS X expects a wx.Color and fails on tuples
        # so convert the tuples to a wx.Color:
        currentColor = wx.Color(*currentColor) if currentColor else defaultColor # pylint: disable-msg=W0142
        button = wx.ColourPickerCtrl(self, col=currentColor)
        setattr(self, '_%sColorButton'%colorType, button)
        buttonHandler = getattr(self, 'on%sColourPicked'%colorType.capitalize())
        button.Bind(wx.EVT_COLOURPICKER_CHANGED, buttonHandler)
        self.addEntry(labelText, checkBox, button, flags=[None, None, wx.ALL])
        if len(self.items) == 1:
            handler = getattr(self, 'on%sColourChanged'%colorType.capitalize())
            eventType = getattr(self.items[0], '%sColorChangedEventType'%colorType)()
            patterns.Publisher().registerObserver(handler, eventType=eventType,
                                                  eventSource=self.items[0])
            
    # pylint: disable-msg=E1101
    
    def onForegroundColourCheckBoxChecked(self, event):
        ''' User toggled the foreground colour check box. Update the colour
            of the font colour button. '''
        self._fontButton.SetColour(self._foregroundColorButton.GetColour() if \
                                   event.IsChecked() else wx.NullColour)
        self.onForegroundColorEdited(event)
        
    def onForegroundColourPicked(self, event): # pylint: disable-msg=W0613 
        ''' User picked a foreground colour. Check the foreground colour check
            box and update the font colour button. '''
        self._foregroundColorCheckBox.SetValue(True)
        self._fontButton.SetColour(self._foregroundColorButton.GetColour())
        self.onForegroundColorEdited(event)
        
    def onForegroundColorEdited(self, event):
        event.Skip()
        checked = self._foregroundColorCheckBox.GetValue()
        newColor = self._foregroundColorButton.GetColour() if checked else None
        if newColor != self._currentForegroundColor: # pylint: disable-msg=E0203
            self._currentForegroundColor = newColor # pylint: disable-msg=W0201
            command.EditForegroundColorCommand(None, self.items, color=newColor).do()
            
    def onForegroundColourChanged(self, event):
        newColor = event.value()
        if newColor != self._currentForegroundColor:
            self._currentForegroundColor = newColor
            self._foregroundColorCheckBox.SetValue(newColor is not None)
            self._foregroundColorButton.SetColour(newColor)

    def onBackgroundColourCheckBoxChecked(self, event):
        ''' User toggled the background colour check box. '''
        self.onBackgroundColorEdited(event)
        
    def onBackgroundColourPicked(self, event): # pylint: disable-msg=W0613 
        ''' User picked a background colour. Check the background colour check
            box. '''
        self._backgroundColorCheckBox.SetValue(True)
        self.onBackgroundColorEdited(event)
        
    def onBackgroundColorEdited(self, event):
        event.Skip()
        checked = self._backgroundColorCheckBox.GetValue()
        newColor = self._backgroundColorButton.GetColour() if checked else None
        if newColor != self._currentBackgroundColor: # pylint: disable-msg=E0203
            self._currentBackgroundColor = newColor # pylint: disable-msg=W0201
            command.EditBackgroundColorCommand(None, self.items, color=newColor).do()

    def onBackgroundColourChanged(self, event):
        newColor = event.value()
        if newColor != self._currentBackgroundColor:
            self._currentBackgroundColor = newColor
            self._backgroundColorCheckBox.SetValue(newColor is not None)
            self._backgroundColorButton.SetColour(newColor)

    def addFontEntry(self):
        # pylint: disable-msg=W0201
        self._fontCheckBox = wx.CheckBox(self, label=_('Use font:'))
        self._currentFont = self.items[0].font() if len(self.items) == 1 else None
        currentColor = self._foregroundColorButton.GetColour()
        self._fontCheckBox.SetValue(self._currentFont is not None)
        self._fontCheckBox.Bind(wx.EVT_CHECKBOX, self.onFontEdited)
        self._defaultFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self._fontButton = widgets.FontPickerCtrl(self,
            font=self._currentFont or self._defaultFont, colour=currentColor)
        self._fontButton.Bind(wx.EVT_FONTPICKER_CHANGED, self.onFontPicked)
        self.addEntry(_('Font'), self._fontCheckBox, self._fontButton,
                      flags=[None, None, wx.ALL])
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onFontChanged, 
                                                  eventType=self.items[0].fontChangedEventType(), 
                                                  eventSource=self.items[0])

    def onFontPicked(self, event): # pylint: disable-msg=W0613 
        ''' User picked a font. Check the font check box and change the
            foreground color if needed. '''
        self._fontCheckBox.SetValue(True)
        if self._fontButton.GetSelectedColour() != self._foregroundColorButton.GetColour():
            self._foregroundColorCheckBox.SetValue(True)
            self._foregroundColorButton.SetColour(self._fontButton.GetSelectedColour())
        self.onFontEdited(event)
        
    def onFontEdited(self, event):
        event.Skip()
        checked = self._fontCheckBox.GetValue()
        newFont = self._fontButton.GetSelectedFont() if checked else None        
        if newFont != self._currentFont:
            self._currentFont = newFont
            command.EditFontCommand(None, self.items, font=newFont).do()
            
    def onFontChanged(self, event):
        newFont = event.value()
        if newFont != self._currentFont:
            self._currentFont = newFont
            checked = newFont is not None
            self._fontCheckBox.SetValue(checked)
            if checked:
                self._fontButton.SetFont(newFont or self._defaultFont)
        
    def addIconEntry(self):
        # pylint: disable-msg=W0201
        self._iconEntry = wx.combo.BitmapComboBox(self, style=wx.CB_READONLY)
        self._iconEntry.Bind(wx.EVT_COMBOBOX, self.onIconEdited)
        size = (16, 16)
        imageNames = sorted(artprovider.chooseableItemImages.keys())
        for imageName in imageNames:
            label = artprovider.chooseableItemImages[imageName]
            bitmap = wx.ArtProvider_GetBitmap(imageName, wx.ART_MENU, size)
            self._iconEntry.Append(label, bitmap, clientData=imageName)
        self._currentIcon = self.items[0].icon() if len(self.items) == 1 else ''
        currentSelectionIndex = imageNames.index(self._currentIcon)
        self._iconEntry.SetSelection(currentSelectionIndex)
        self.addEntry(_('Icon'), self._iconEntry, flags=[None, wx.ALL])
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onIconChanged, 
                                                  eventType=self.items[0].iconChangedEventType(), 
                                                  eventSource=self.items[0])
        
    def onIconEdited(self, event):
        event.Skip()
        newIcon = self._iconEntry.GetClientData(self._iconEntry.GetSelection())
        if newIcon != self._currentIcon:
            selectedIcon = newIcon[:-len('_icon')] + '_open_icon' \
                if (newIcon.startswith('folder') and newIcon.count('_') == 2) \
                else newIcon
            self._currentIcon = newIcon
            command.EditIconCommand(None, self.items, icon=newIcon, selectedIcon=selectedIcon).do()
            
    def onIconChanged(self, event):
        newIcon = event.value()
        if newIcon != self._currentIcon:
            self._currentIcon = newIcon
            imageNames = sorted(artprovider.chooseableItemImages.keys())
            newSelectionIndex = imageNames.index(newIcon)
            self._iconEntry.SetSelection(newSelectionIndex)
    
    def entries(self):
        return dict(firstEntry=self._foregroundColorCheckBox)
    

class DatesPage(Page):
    pageName = 'dates'
    pageTitle = _('Dates') 
    pageIcon = 'calendar_icon'
    
    def __init__(self, theTask, parent, settings, *args, **kwargs):
        self.__settings = settings
        super(DatesPage, self).__init__(theTask, parent, *args, **kwargs)
        
    def addEntries(self):
        self.addDateEntries()
        self.addLine()
        self.addReminderEntry()
        self.addLine()
        self.addRecurrenceEntries()
        
    def addDateEntries(self):
        for label, taskMethodName in [(_('Start date'), 'startDateTime'),
                                      (_('Due date'), 'dueDateTime'),
                                      (_('Completion date'), 'completionDateTime')]:
            self.addDateEntry(label, taskMethodName)
            
    def addDateEntry(self, label, taskMethodName):
        def capitalize(string):
            return string[0].capitalize()+string[1:]

        dateTime = getattr(self.items[0], taskMethodName)() if len(self.items) == 1 else date.DateTime()
        setattr(self, '_current%s'%capitalize(taskMethodName), dateTime)
        callback = getattr(self, 'on%sEdited'%capitalize(taskMethodName))
        dateTimeEntry = entry.DateTimeEntry(self, self.__settings, dateTime,
                                            callback=callback)
        setattr(self, '_%sEntry'%taskMethodName, dateTimeEntry)
        self.addEntry(label, dateTimeEntry)
        if len(self.items) == 1:
            eventHandler = getattr(self, 'on%sChanged'%capitalize(taskMethodName))
            eventType = 'task.%s'%taskMethodName
            patterns.Publisher().registerObserver(eventHandler, 
                                                  eventType=eventType, 
                                                  eventSource=self.items[0])
        
    def addReminderEntry(self):
        # pylint: disable-msg=W0201
        self._currentReminderDateTime = self.items[0].reminder() if len(self.items) == 1 else date.DateTime()
        self._reminderDateTimeEntry = entry.DateTimeEntry(self, self.__settings, 
                                                          self._currentReminderDateTime)
        # If the user has not set a reminder, make sure that the default 
        # date time in the reminder entry is a reasonable suggestion:
        if self._reminderDateTimeEntry.get() == date.DateTime():
            self.suggestReminder()
        self.addEntry(_('Reminder'), self._reminderDateTimeEntry)
        self._reminderDateTimeEntry.setCallback(self.onReminderEdited)
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onReminderChanged, 
                                                  eventType='task.reminder', 
                                                  eventSource=self.items[0])
        
    def addRecurrenceEntries(self):
        # pylint: disable-msg=W0201
        recurrencePanel = wx.Panel(self)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._recurrenceEntry = wx.Choice(recurrencePanel, 
            choices=[_('None'), _('Daily'), _('Weekly'), _('Monthly'), _('Yearly')])        
        self._recurrenceEntry.Bind(wx.EVT_CHOICE, self.onRecurrencePeriodEdited)
        panelSizer.Add(self._recurrenceEntry, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        staticText = wx.StaticText(recurrencePanel, label=_(', every'))
        panelSizer.Add(staticText, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._recurrenceFrequencyEntry = widgets.SpinCtrl(recurrencePanel, 
                                                          size=(50,-1), 
                                                          initial=1, min=1)
        self._recurrenceFrequencyEntry.Bind(wx.EVT_SPINCTRL, self.onRecurrenceEdited)
        panelSizer.Add(self._recurrenceFrequencyEntry, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._recurrenceStaticText = wx.StaticText(recurrencePanel, 
                                                   label='reserve some space')
        panelSizer.Add(self._recurrenceStaticText, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3, -1))
        self._recurrenceSameWeekdayCheckBox = wx.CheckBox(recurrencePanel, 
            label=_('keeping dates on the same weekday'))
        self._recurrenceSameWeekdayCheckBox.Bind(wx.EVT_CHECKBOX, self.onRecurrenceEdited)
        panelSizer.Add(self._recurrenceSameWeekdayCheckBox, proportion=1, 
                       flag=wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        recurrencePanel.SetSizerAndFit(panelSizer)
        self._recurrenceSizer = panelSizer

        maxPanel = wx.Panel(self)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._maxRecurrenceCheckBox = wx.CheckBox(maxPanel)
        self._maxRecurrenceCheckBox.Bind(wx.EVT_CHECKBOX, self.onMaxRecurrenceChecked)
        panelSizer.Add(self._maxRecurrenceCheckBox, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._maxRecurrenceCountEntry = widgets.SpinCtrl(maxPanel, size=(50,-1), 
                                                         initial=1, min=1)
        self._maxRecurrenceCountEntry.Bind(wx.EVT_SPINCTRL, self.onRecurrenceEdited)
        panelSizer.Add(self._maxRecurrenceCountEntry)
        maxPanel.SetSizerAndFit(panelSizer)
        self.addEntry(_('Recurrence'), recurrencePanel)
        self.addEntry(_('Maximum number\nof recurrences'), maxPanel)
        self._currentRecurrence = self.items[0].recurrence() if len(self.items) == 1 else date.Recurrence()
        self.setRecurrence(self._currentRecurrence)
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onRecurrenceChanged, 
                                                  eventType='task.recurrence', 
                                                  eventSource=self.items[0])
            
    def entries(self):
        # pylint: disable-msg=E1101
        return dict(startDateTime=self._startDateTimeEntry, 
                    dueDateTime=self._dueDateTimeEntry,
                    completionDateTime=self._completionDateTimeEntry, 
                    timeLeft=self._dueDateTimeEntry, 
                    reminder=self._reminderDateTimeEntry, 
                    recurrence=self._recurrenceEntry)
    
    def onRecurrencePeriodEdited(self, event):
        recurrenceOn = event.String != _('None')
        self._maxRecurrenceCheckBox.Enable(recurrenceOn)
        self._recurrenceFrequencyEntry.Enable(recurrenceOn)
        self._maxRecurrenceCountEntry.Enable(recurrenceOn and \
            self._maxRecurrenceCheckBox.IsChecked())
        self.updateRecurrenceLabel()
        self.onRecurrenceEdited(event)

    def onMaxRecurrenceChecked(self, event):
        maxRecurrenceOn = event.IsChecked()
        self._maxRecurrenceCountEntry.Enable(maxRecurrenceOn)
        self.onRecurrenceEdited(event)
        
    def onRecurrenceEdited(self, event):
        event.Skip()
        newRecurrence = self.getRecurrence()
        if newRecurrence != self._currentRecurrence:
            command.EditRecurrenceCommand(None, self.items, recurrence=newRecurrence).do()
            self._currentRecurrence = newRecurrence
            
    def onRecurrenceChanged(self, event):
        newRecurrence = event.value()
        if newRecurrence != self._currentRecurrence:
            self._currentRecurrence = newRecurrence
            self.setRecurrence(newRecurrence)
            
    def getRecurrence(self):
        recurrenceDict = {0: '', 1: 'daily', 2: 'weekly', 3: 'monthly', 4: 'yearly'}
        kwargs = dict(unit=recurrenceDict[self._recurrenceEntry.Selection])
        if self._maxRecurrenceCheckBox.IsChecked():
            kwargs['max'] = self._maxRecurrenceCountEntry.Value
        kwargs['amount'] = self._recurrenceFrequencyEntry.Value
        kwargs['sameWeekday'] = self._recurrenceSameWeekdayCheckBox.IsChecked()
        return date.Recurrence(**kwargs) # pylint: disable-msg=W0142
    
    def onStartDateTimeEdited(self, event):
        # pylint: disable-msg=E1101,E0203,W0201
        event.Skip()
        newStartDateTime = self._startDateTimeEntry.get()
        if newStartDateTime != self._currentStartDateTime:
            command.EditStartDateTimeCommand(None, self.items, datetime=newStartDateTime).do()
            self._currentStartDateTime = newStartDateTime
            self.onDateTimeEdited()
            
    def onStartDateTimeChanged(self, event):
        newStartDateTime = event.value()
        if newStartDateTime != self._currentStartDateTime:
            self._currentStartDateTime = newStartDateTime
            self._startDateTimeEntry.set(newStartDateTime) # pylint: disable-msg=E1101
                    
    def onDueDateTimeEdited(self, event):
        # pylint: disable-msg=E1101,E0203,W0201
        event.Skip()
        newDueDateTime = self._dueDateTimeEntry.get()
        if newDueDateTime != self._currentDueDateTime:
            command.EditDueDateTimeCommand(None, self.items, datetime=newDueDateTime).do()
            self._currentDueDateTime = newDueDateTime
            self.onDateTimeEdited()

    def onDueDateTimeChanged(self, event):
        newDueDateTime = event.value()
        if newDueDateTime != self._currentDueDateTime:
            self._currentDueDateTime = newDueDateTime
            self._dueDateTimeEntry.set(newDueDateTime) # pylint: disable-msg=E1101

    def onCompletionDateTimeEdited(self, event):
        # pylint: disable-msg=E1101,E0203,W0201
        event.Skip()
        newCompletionDateTime = self._completionDateTimeEntry.get()
        if newCompletionDateTime != self._currentCompletionDateTime:
            command.EditCompletionDateTimeCommand(None, self.items, datetime=newCompletionDateTime).do()
            self._currentCompletionDateTime = newCompletionDateTime
            self.onDateTimeEdited()

    def onCompletionDateTimeChanged(self, event):
        newCompletionDateTime = event.value()
        if newCompletionDateTime != self._currentCompletionDateTime:
            self._currentCompletionDateTime = newCompletionDateTime
            self._completionDateTimeEntry.set(newCompletionDateTime) # pylint: disable-msg=E1101

    def onDateTimeEdited(self):
        ''' Called when one of the DateTimeEntries is changed by the user. 
            Update the suggested reminder if no reminder was set by the user. '''
        # Make sure the reminderDateTimeEntry has been created:
        if hasattr(self, '_reminderDateTimeEntry') and \
            self._reminderDateTimeEntry.get() == date.DateTime():
            self.suggestReminder()
            
    def onReminderEdited(self, event):
        event.Skip()
        newReminderDatetime = self._reminderDateTimeEntry.get()
        if newReminderDatetime != self._currentReminderDateTime:
            command.EditReminderDateTimeCommand(None, self.items, datetime=newReminderDatetime).do()
            self._currentReminderDateTime = newReminderDatetime
            
    def onReminderChanged(self, event):
        newReminderDateTime = event.value()
        if newReminderDateTime != self._currentReminderDateTime:
            self._currentReminderDateTime = newReminderDateTime
            self.setReminder(newReminderDateTime)
        
    def setReminder(self, reminder):
        self._reminderDateTimeEntry.set(reminder)

    def setRecurrence(self, recurrence):
        index = {'': 0, 'daily': 1, 'weekly': 2, 'monthly': 3, 'yearly': 4}[recurrence.unit]
        self._recurrenceEntry.Selection = index
        self._maxRecurrenceCheckBox.Enable(bool(recurrence))
        self._maxRecurrenceCheckBox.SetValue(recurrence.max > 0)
        self._maxRecurrenceCountEntry.Enable(recurrence.max > 0)
        if recurrence.max > 0:
            self._maxRecurrenceCountEntry.Value = recurrence.max
        self._recurrenceFrequencyEntry.Enable(bool(recurrence))
        if recurrence.amount > 1:
            self._recurrenceFrequencyEntry.Value = recurrence.amount
        if recurrence.unit in ('monthly', 'yearly'):
            self._recurrenceSameWeekdayCheckBox.Value = recurrence.sameWeekday
        else:
            # If recurrence is not monthly or yearly, set same week day to False
            self._recurrenceSameWeekdayCheckBox.Value = False
        self.updateRecurrenceLabel()

    def updateRecurrenceLabel(self):
        recurrenceDict = {0: _('period,'), 1: _('day(s),'), 2: _('week(s),'),
                          3: _('month(s),'), 4: _('year(s),')}
        recurrenceLabel = recurrenceDict[self._recurrenceEntry.Selection]
        self._recurrenceStaticText.SetLabel(recurrenceLabel)
        self._recurrenceSameWeekdayCheckBox.Enable(self._recurrenceEntry.Selection in (3,4))
        self._recurrenceSizer.Layout()

    def suggestReminder(self):
        ''' suggestReminder populates the reminder entry with a reasonable
            suggestion for a reminder date and time, but does not enable the
            reminder entry. '''
        # The suggested date for the reminder is the first date from the
        # list of candidates that is a real date:
        # pylint: disable-msg=E1101
        candidates = [self._dueDateTimeEntry.get(), self._startDateTimeEntry.get(),
                      date.Now() + date.oneDay]
        suggestedDateTime = [candidate for candidate in candidates \
                            if date.Now() <= candidate < date.DateTime()][0]
        # Now, make sure the suggested date time is set in the control
        self.setReminder(suggestedDateTime)
        # And then disable the control (because the SetValue in the
        # previous statement enables the control)
        self.setReminder(None)
        # Now, when the user clicks the check box to enable the
        # control it will show the suggested date time
        

class ProgressPage(Page):
    pageName = 'progress'
    pageTitle = _('Progress')
    pageIcon = 'progress'
    
    def addEntries(self):
        self.addProgressEntry()
        self.addBehaviorEntry()
        
    def addProgressEntry(self):
        # pylint: disable-msg=W0201
        self._currentPercentageComplete = self.items[0].percentageComplete() if len(self.items) == 1 else self.averagePercentageComplete(self.items)
        self._percentageCompleteEntry = entry.PercentageEntry(self, 
            self._currentPercentageComplete, 
            callback=self.onPercentageCompleteEdited)
        self.addEntry(_('Percentage complete'), self._percentageCompleteEntry)
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onPercentageCompleteChanged, 
                                                  eventType=self.items[0].percentageCompleteChangedEventType(), 
                                                  eventSource=self.items[0])
            
    def averagePercentageComplete(self, items):
        return sum([item.percentageComplete() for item in items]) \
                    / float(len(items)) if items else 0

    def onPercentageCompleteEdited(self):
        newPercentageComplete = self._percentageCompleteEntry.get()
        if newPercentageComplete != self._currentPercentageComplete:
            command.EditPercentageCompleteCommand(None, self.items, 
                                                  percentage=newPercentageComplete).do()
            self._currentPercentageComplete = newPercentageComplete
            
    def onPercentageCompleteChanged(self, event):
        newPercentageComplete = event.value()
        if newPercentageComplete != self._currentPercentageComplete:
            self._currentPercentageComplete = newPercentageComplete
            self._percentageCompleteEntry.set(newPercentageComplete)
        
    def addBehaviorEntry(self):
        # pylint: disable-msg=W0201
        self._markTaskCompletedEntry = choice = wx.Choice(self)
        self._markTaskCompletedEntry.Bind(wx.EVT_CHOICE, self.onShouldMarkCompletedEdited)
        self._currentShouldMarkCompleted = self.items[0].shouldMarkCompletedWhenAllChildrenCompleted() if len(self.items) == 1 else None
        for choiceValue, choiceText in \
                [(None, _('Use application-wide setting')),
                 (False, _('No')), (True, _('Yes'))]:
            choice.Append(choiceText, choiceValue)
            if choiceValue == self._currentShouldMarkCompleted:
                choice.SetSelection(choice.GetCount()-1)
        if choice.GetSelection() == wx.NOT_FOUND:
            # Force a selection if necessary:
            choice.SetSelection(0)
        self.addEntry(_('Mark task completed when all children are completed?'), 
                      choice, flags=[None, wx.ALL])
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onShouldMarkCompletedChanged,
                                                  eventType='task.setting.shouldMarkCompletedWhenAllChildrenCompleted', 
                                                  eventSource=self.items[0])
        
    def onShouldMarkCompletedEdited(self, event):
        event.Skip()
        newShouldMarkCompleted = self._markTaskCompletedEntry.GetClientData( \
            self._markTaskCompletedEntry.GetSelection())
        if newShouldMarkCompleted != self._currentShouldMarkCompleted:
            command.EditShouldMarkCompletedCommand(None, self.items, 
                                                   shouldMarkCompleted=newShouldMarkCompleted).do()
            self._currentShouldMarkCompleted = newShouldMarkCompleted
            
    def onShouldMarkCompletedChanged(self, event):
        newShouldMarkCompleted = event.value()
        if newShouldMarkCompleted != self._currentShouldMarkCompleted:
            self._currentShouldMarkCompleted = newShouldMarkCompleted
            index = [None, False, True].index(newShouldMarkCompleted)
            self._markTaskCompletedEntry.SetSelection(index)
        
    def entries(self):
        return dict(percentageComplete=self._percentageCompleteEntry)
        

class BudgetPage(Page):
    pageName = 'budget'
    pageTitle = _('Budget')
    pageIcon = 'calculator_icon'
    
    def addEntries(self):
        self.addBudgetEntries()
        self.addLine()
        self.addRevenueEntries()
        self.observeTracking()
        
    def addBudgetEntries(self):
        self.addBudgetEntry()
        if len(self.items) == 1:
            self.addTimeSpentEntry()
            self.addBudgetLeftEntry()
            
    def addBudgetEntry(self):
        # pylint: disable-msg=W0201
        self._currentBudget = self.items[0].budget() if len(self.items) == 1 else date.TimeDelta()
        self._budgetEntry = entry.TimeDeltaEntry(self, self._currentBudget)
        self._budgetEntry.Bind(wx.EVT_KILL_FOCUS, self.onBudgetEdited)
        self.addEntry(_('Budget'), self._budgetEntry, flags=[None, wx.ALL])
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onBudgetChanged, 
                                                  eventType='task.budget', 
                                                  eventSource=self.items[0])
        
    def onBudgetEdited(self, event):
        event.Skip()
        newBudget = self._budgetEntry.get()
        if newBudget != self._currentBudget:
            self._currentBudget = newBudget
            command.EditBudgetCommand(None, self.items, budget=newBudget).do()
            
    def onBudgetChanged(self, event):
        newBudget = event.value()
        if newBudget != self._currentBudget:
            self._currentBudget = newBudget
            self._budgetEntry.set(newBudget)
            
    def addTimeSpentEntry(self):
        assert len(self.items) == 1
        # pylint: disable-msg=W0201 
        self._timeSpentEntry = entry.TimeDeltaEntry(self, 
                                                    self.items[0].timeSpent(), 
                                                    readonly=True)
        self.addEntry(_('Time spent'), self._timeSpentEntry, 
                      flags=[None, wx.ALL])
        patterns.Publisher().registerObserver(self.onTimeSpentChanged, 
                                              eventType='task.timeSpent', 
                                              eventSource=self.items[0])
        
    def onTimeSpentChanged(self, event): # pylint: disable-msg=W0613
        newTimeSpent = self.items[0].timeSpent()
        if newTimeSpent != self._timeSpentEntry.get():
            self._timeSpentEntry.set(newTimeSpent)
            
    def addBudgetLeftEntry(self):
        assert len(self.items) == 1
        # pylint: disable-msg=W0201
        self._budgetLeftEntry = entry.TimeDeltaEntry(self, 
                                                     self.items[0].budgetLeft(), 
                                                     readonly=True)
        self.addEntry(_('Budget left'), self._budgetLeftEntry, 
                      flags=[None, wx.ALL])
        patterns.Publisher().registerObserver(self.onBudgetLeftChanged,
                                              eventType='task.budgetLeft',
                                              eventSource=self.items[0])
        
    def onBudgetLeftChanged(self, event): # pylint: disable-msg=W0613
        newBudgetLeft = self.items[0].budgetLeft()
        if newBudgetLeft != self._budgetLeftEntry.get():
            self._budgetLeftEntry.set(newBudgetLeft)
            
    def addRevenueEntries(self):
        self.addHourlyFeeEntry()
        self.addFixedFeeEntry()
        if len(self.items) == 1:
            self.addRevenueEntry()
            
    def addHourlyFeeEntry(self):
        # pylint: disable-msg=W0201
        self._currentHourlyFee = self.items[0].hourlyFee() if len(self.items) == 1 else 0
        self._hourlyFeeEntry = entry.AmountEntry(self, self._currentHourlyFee)
        self._hourlyFeeEntry.Bind(wx.EVT_KILL_FOCUS, self.onHourlyFeeEdited)
        self.addEntry(_('Hourly fee'), self._hourlyFeeEntry, flags=[None, wx.ALL])
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onHourlyFeeChanged, 
                                                  eventType=self.items[0].hourlyFeeChangedEventType(), 
                                                  eventSource=self.items[0])
            
    def onHourlyFeeEdited(self, event):
        event.Skip()
        newHourlyFee = self._hourlyFeeEntry.get()
        if newHourlyFee != self._currentHourlyFee:
            self._currentHourlyFee = newHourlyFee
            command.EditHourlyFeeCommand(None, self.items, hourlyFee=newHourlyFee).do()
            
    def onHourlyFeeChanged(self, event):
        newHourlyFee = event.value()
        if newHourlyFee != self._currentHourlyFee:
            self._currentHourlyFee = newHourlyFee
            self._hourlyFeeEntry.set(newHourlyFee)
        
    def addFixedFeeEntry(self):
        # pylint: disable-msg=W0201
        self._currentFixedFee = self.items[0].fixedFee() if len(self.items) == 1 else 0
        self._fixedFeeEntry = entry.AmountEntry(self, self._currentFixedFee)
        self._fixedFeeEntry.Bind(wx.EVT_KILL_FOCUS, self.onFixedFeeEdited)
        self.addEntry(_('Fixed fee'), self._fixedFeeEntry, flags=[None, wx.ALL])
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onFixedFeeChanged, 
                                                  eventType='task.fixedFee', 
                                                  eventSource=self.items[0])

    def onFixedFeeEdited(self, event):
        event.Skip()
        newFixedFee = self._fixedFeeEntry.get()
        if newFixedFee != self._currentFixedFee:
            self._currentFixedFee = newFixedFee
            command.EditFixedFeeCommand(None, self.items, fixedFee=newFixedFee).do()
            
    def onFixedFeeChanged(self, event):
        newFixedFee = event.value()
        if newFixedFee != self._currentFixedFee:
            self._currentFixedFee = newFixedFee
            self._fixedFeeEntry.set(newFixedFee)
        
    def addRevenueEntry(self):
        assert len(self.items) == 1
        revenue = self.items[0].revenue()
        self._revenueEntry = entry.AmountEntry(self, revenue, readonly=True) # pylint: disable-msg=W0201
        self.addEntry(_('Revenue'), self._revenueEntry, flags=[None, wx.ALL])
        patterns.Publisher().registerObserver(self.onRevenueChanged,
                                              eventType='task.revenue',
                                              eventSource=self.items[0])

    def onRevenueChanged(self, event): # pylint: disable-msg=W0613
        newRevenue = self.items[0].revenue()
        if newRevenue != self._revenueEntry.get():
            self._revenueEntry.set(newRevenue)
            
    def observeTracking(self):
        if len(self.items) != 1:
            return
        registerObserver = patterns.Publisher().registerObserver
        item = self.items[0]
        registerObserver(self.onStartTracking, 
                         eventType=item.trackStartEventType(), 
                         eventSource=item)
        registerObserver(self.onStopTracking, 
                         eventType=item.trackStopEventType(), 
                         eventSource=item)
        if item.isBeingTracked():
            self.onStartTracking(None)
        
    def onStartTracking(self, event): # pylint: disable-msg=W0613
        # We might already be observing the clock if the user is tracking this
        # task with multiple effort records simultaneously
        if self.onEverySecond not in patterns.Publisher().observers('clock.second'):
            patterns.Publisher().registerObserver(self.onEverySecond, eventType='clock.second')
        
    def onStopTracking(self, event): # pylint: disable-msg=W0613
        # We might need to keep tracking the clock if the user was tracking this
        # task with multiple effort records simultaneously
        if not self.items[0].isBeingTracked():
            patterns.Publisher().removeObserver(self.onEverySecond, eventType='clock.second')
    
    def onEverySecond(self, event):
        self.onTimeSpentChanged(event)
        self.onBudgetLeftChanged(event)
        self.onRevenueChanged(event)
        
    def entries(self):
        return dict(budget=self._budgetEntry, 
                    budgetLeft=self._budgetEntry,  
                    hourlyFee=self._hourlyFeeEntry, 
                    fixedFee=self._fixedFeeEntry,  
                    revenue=self._hourlyFeeEntry)

    # XXXFIXME: ok() was removed from Trunk but modified in release-1.x. There's
    # probably something to do :)

    ## @patterns.eventSource    
    ## def ok(self, event=None): # pylint: disable-msg=W0221
    ##     for item in self.items:
    ##         if len(self.items) == 1 or self._budgetLabel.IsChecked():
    ##             item.setBudget(self._budgetEntry.get(), event=event)
    ##         if len(self.items) == 1 or self._hourlyFeeLabel.IsChecked():
    ##             item.setHourlyFee(self._hourlyFeeEntry.get(), event=event)
    ##         if len(self.items) == 1 or self._fixedFeeLabel.IsChecked():
    ##             item.setFixedFee(self._fixedFeeEntry.get(), event=event)


class PageWithViewer(Page):
    columns = 1
    
    def __init__(self, items, parent, taskFile, settings, settingsSection, *args, **kwargs):
        self.__taskFile = taskFile
        self.__settings = settings
        self.__settingsSection = settingsSection
        super(PageWithViewer, self).__init__(items, parent, *args, **kwargs)
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)
        
    def addEntries(self):
        # pylint: disable-msg=W0201
        self.viewer = self.createViewer(self.__taskFile, self.__settings,
                                        self.__settingsSection) 
        self.addEntry(self.viewer, growable=True)
        
    def createViewer(self, taskFile, settings, settingsSection):
        raise NotImplementedError
        
    def onClose(self, event):
        # Don't notify the viewer about any changes anymore, it's about
        # to be deleted, but don't delete it soo soon.
        wx.CallAfter(self.detachAndDeleteViewer)
        event.Skip()        
        
    def detachAndDeleteViewer(self):
        if hasattr(self, 'viewer'):
            self.viewer.detach()
            del self.viewer


class EffortPage(PageWithViewer):
    pageName = 'effort'
    pageTitle = _('Effort')
    pageIcon = 'clock_icon'
            
    def createViewer(self, taskFile, settings, settingsSection):
        return viewer.EffortViewer(self, taskFile, settings, 
            settingsSection=settingsSection,
            tasksToShowEffortFor=task.TaskList(self.items))

    def entries(self):
        return dict(timeSpent=self.viewer)
        

class LocalCategoryViewer(viewer.BaseCategoryViewer):
    def __init__(self, items, *args, **kwargs):
        self.__items = items
        super(LocalCategoryViewer, self).__init__(*args, **kwargs)
        for item in self.domainObjectsToView():
            item.expand(context=self.settingsSection())

    def getIsItemChecked(self, category):
        for item in self.__items:
            if category in item.categories():
                return True
        return False

    def onCheck(self, event):
        ''' Here we keep track of the items checked by the user so that these 
            items remain checked when refreshing the viewer. ''' 
        category = self.widget.GetItemPyData(event.GetItem())
        command.ToggleCategoryCommand(None, self.__items, category=category).do()

    def createCategoryPopupMenu(self): # pylint: disable-msg=W0221
        return super(LocalCategoryViewer, self).createCategoryPopupMenu(True)            


class CategoriesPage(PageWithViewer):
    pageName = 'categories'
    pageTitle = _('Categories')
    pageIcon = 'folder_blue_arrow_icon'
    
    def createViewer(self, taskFile, settings, settingsSection):
        return LocalCategoryViewer(self.items, self, taskFile, settings,
                                   settingsSection=settingsSection)
        
    def entries(self):
        return dict(categories=self.viewer) 


class LocalAttachmentViewer(viewer.AttachmentViewer):
    def __init__(self, *args, **kwargs):
        self.attachmentOwner = kwargs.pop('owner')
        attachments = attachment.AttachmentList(self.attachmentOwner.attachments())
        super(LocalAttachmentViewer, self).__init__(attachmentsToShow=attachments, *args, **kwargs)
        patterns.Publisher().registerObserver(self.onOriginalAttachmentsChanged, 
            eventType=self.attachmentOwner.attachmentsChangedEventType(), 
            eventSource=self.attachmentOwner)

    def onOriginalAttachmentsChanged(self, event): # pylint: disable-msg=W0613
        self.domainObjectsToView().clear()
        self.domainObjectsToView().extend(self.attachmentOwner.attachments())
        
    def newItemCommand(self, *args, **kwargs):
        return command.AddAttachmentCommand(None, [self.attachmentOwner])
    
    def deleteItemCommand(self):
        return command.RemoveAttachmentCommand(None, [self.attachmentOwner], attachments=self.curselection())


class AttachmentsPage(PageWithViewer):
    pageName = 'attachments'
    pageTitle = _('Attachments')
    pageIcon = 'paperclip_icon'
    
    def createViewer(self, taskFile, settings, settingsSection):
        return LocalAttachmentViewer(self, taskFile, settings,
            settingsSection=settingsSection, owner=self.items[0])
        
    def entries(self):
        return dict(attachments=self.viewer)


class LocalNoteViewer(viewer.BaseNoteViewer):
    def __init__(self, *args, **kwargs):
        self.noteOwner = kwargs.pop('owner')
        notes = note.NoteContainer(self.noteOwner.notes())
        super(LocalNoteViewer, self).__init__(notesToShow=notes, *args, **kwargs)
        patterns.Publisher().registerObserver(self.onOriginalNotesChanged,
            eventType=self.noteOwner.notesChangedEventType(),
            eventSource=self.noteOwner)
        
    def onOriginalNotesChanged(self, event): # pylint: disable-msg=W0613
        self.domainObjectsToView().clear()
        self.domainObjectsToView().extend(self.noteOwner.notes())
        
    def newItemCommand(self, *args, **kwargs):
        return command.AddNoteCommand(None, [self.noteOwner])
    
    def newSubItemCommand(self):
        return command.AddSubNoteCommand(None, self.curselection(), owner=self.noteOwner)
    
    def deleteItemCommand(self):
        return command.RemoveNoteCommand(None, [self.noteOwner], notes=self.curselection())


class NotesPage(PageWithViewer):
    pageName = 'notes'
    pageTitle = _('Notes')
    pageIcon = 'note_icon'
    
    def createViewer(self, taskFile, settings, settingsSection):
        return LocalNoteViewer(self, taskFile, settings, 
                                     settingsSection=settingsSection,
                                     owner=self.items[0])

    def entries(self):
        return dict(notes=self.viewer)
    

class LocalPrerequisiteViewer(viewer.CheckableTaskViewer):
    def __init__(self, items, *args, **kwargs):
        self.__items = items
        super(LocalPrerequisiteViewer, self).__init__(*args, **kwargs)
        for item in self.domainObjectsToView():
            item.expand(context=self.settingsSection())

    def getIsItemChecked(self, item):
        return item in self.__items[0].prerequisites()

    def getIsItemCheckable(self, item):
        return item not in self.__items
    
    def onCheck(self, event):
        item = self.widget.GetItemPyData(event.GetItem())
        isChecked = event.GetItem().IsChecked()
        if isChecked != self.getIsItemChecked(item):
            command.TogglePrerequisiteCommand(None, self.__items, checkedPrerequisites=[item],
                                              uncheckedPrerequisites=[]).do()
    
    
class PrerequisitesPage(PageWithViewer):
    pageName = 'prerequisites'
    pageTitle = _('Prerequisites')
    pageIcon = 'trafficlight_icon'
    
    def createViewer(self, taskFile, settings, settingsSection):
        return LocalPrerequisiteViewer(self.items, self, taskFile, settings,
                                       settingsSection=settingsSection)
    
    def entries(self):
        return dict(prerequisites=self.viewer, dependencies=self.viewer)


class EditBook(widgets.Notebook):
    allPageNames = ['subclass responsibility']
    object = 'subclass responsibility'
    
    def __init__(self, parent, items, taskFile, settings):
        self.items = items
        self.settings = settings
        super(EditBook, self).__init__(parent)
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)
        self.addPages(taskFile)
        
    def addPages(self, taskFile):
        for pageName in self.allPageNamesInUserOrder():
            if self.shouldCreatePage(pageName):
                page = self.createPage(pageName, taskFile)
                self.AddPage(page, page.pageTitle, page.pageIcon)

    def allPageNamesInUserOrder(self):
        ''' Return all pages names in the order stored in the settings. The
            settings may not contain all pages (e.g. because a feature was
            turned off by the user) so we add the missing pages if necessary. '''
        pageNamesInUserOrder = self.settings.getlist('editor', '%spages'%self.object)
        remainingPageNames = self.allPageNames[:]
        for pageName in pageNamesInUserOrder:
            remainingPageNames.remove(pageName)
        return pageNamesInUserOrder + remainingPageNames
                    
    def shouldCreatePage(self, pageName):
        if self.pageFeatureDisabled(pageName):
            return False
        return self.pageSupportsMassEditing(pageName) if len(self.items) > 1 else True

    def pageFeatureDisabled(self, pageName):
        if pageName in ('budget', 'effort', 'notes'):
            feature = 'effort' if pageName == 'budget' else pageName
            return not self.settings.getboolean('feature', feature)
        else:
            return False
        
    def pageSupportsMassEditing(self, pageName):
        return pageName in ('subject', 'dates', 'progress', 'budget', 'appearance')

    def createPage(self, pageName, taskFile):
        if pageName == 'subject':
            return self.createSubjectPage()
        elif pageName == 'dates':
            return DatesPage(self.items, self, self.settings) 
        elif pageName == 'prerequisites':
            return PrerequisitesPage(self.items, self, taskFile, self.settings, 
                                     settingsSection='prerequisiteviewerin%seditor'%self.object)
        elif pageName == 'progress':    
            return ProgressPage(self.items, self)
        elif pageName == 'categories':
            return CategoriesPage(self.items, self, taskFile, self.settings, 
                                  settingsSection='categoryviewerin%seditor'%self.object)
        elif pageName == 'budget':                 
            return BudgetPage(self.items, self)
        elif pageName == 'effort':        
            return EffortPage(self.items, self, taskFile, self.settings,
                              settingsSection='effortviewerin%seditor'%self.object)
        elif pageName == 'notes':
            return NotesPage(self.items, self, taskFile, self.settings,
                             settingsSection='noteviewerin%seditor'%self.object)
        elif pageName == 'attachments':
            return AttachmentsPage(self.items, self, taskFile, self.settings, 
                                   settingsSection='attachmentviewerin%seditor'%self.object)
        elif pageName == 'appearance':
            return AppearancePage(self.items, self)
        
    def createSubjectPage(self):
        return SubjectPage(self.items, self)
    
    def setFocus(self, columnName):
        ''' Select the correct page of the editor and correct control on a page
            based on the column that the user double clicked. '''
        page = 0
        for pageIndex in range(self.GetPageCount()):
            if columnName in self[pageIndex].entries():
                page = pageIndex
                break
        self.SetSelection(page)
        self[page].setFocusOnEntry(columnName)

    def isDisplayingItemOrChildOfItem(self, targetItem):
        ancestors = []
        for item in self.items:
            ancestors.extend(item.ancestors())
        return targetItem in self.items + ancestors
    
    def onClose(self, event):
        event.Skip()
        removeInstance = patterns.Publisher().removeInstance
        for page in self:
            removeInstance(page)
        pageNames = [self[index].pageName for index in range(self.GetPageCount())]
        self.settings.setlist('editor', '%spages'%self.object, pageNames)


class TaskEditBook(EditBook):
    allPageNames = ['subject', 'dates', 'prerequisites', 'progress', 
                    'categories', 'budget', 'effort', 'notes', 'attachments', 
                    'appearance']
    object = 'task'

    def createSubjectPage(self):    
        return TaskSubjectPage(self.items, self)


class CategoryEditBook(EditBook):
    allPageNames = ['subject', 'notes', 'attachments', 'appearance']
    object = 'category'

    def createSubjectPage(self):
        return CategorySubjectPage(self.items, self)


class NoteEditBook(EditBook):
    allPageNames = ['subject', 'categories', 'attachments', 'appearance']
    object = 'note'
    

class AttachmentEditBook(EditBook):
    allPageNames = ['subject', 'notes', 'appearance']
    object = 'attachment'
            
    def createSubjectPage(self):
        return AttachmentSubjectPage(self.items, self,
                                     self.settings.get('file', 'attachmentbase'))
    
    def isDisplayingItemOrChildOfItem(self, targetItem):
        return targetItem in self.items
    
        
class EffortEditBook(Page):
    columns = 3
    
    def __init__(self, parent, efforts, taskFile, settings, *args, **kwargs):
        self._effortList = taskFile.efforts()
        taskList = taskFile.tasks()
        self._taskList = task.TaskList(taskList)
        self._taskList.extend([effort.task() for effort in efforts if effort.task() not in taskList])
        self._settings = settings
        super(EffortEditBook, self).__init__(efforts, parent, *args, **kwargs)
        
    def addEntries(self):
        self.addTaskEntry()
        self.addStartAndStopEntries()
        self.addDescriptionEntry()

    def addTaskEntry(self):
        ''' Add an entry for changing the task that this effort record
            belongs to. '''
        # pylint: disable-msg=W0201
        self._originalTask = self.items[0].task()
        self._taskEntry = entry.TaskComboTreeBox(self,
            rootTasks=self._taskList.rootItems(),
            selectedTask=self._originalTask)
        self._taskEntry._comboTreeBox.Bind(wx.EVT_COMBOBOX, self.onTaskChanged)
        self.addEntry(_('Task'), self._taskEntry, flags=[None, wx.ALL|wx.EXPAND])
        
    def onTaskChanged(self, event): # pylint: disable-msg=W0613
        event.Skip()
        newTask = self._taskEntry.GetSelection()
        if newTask != self._originalTask:
            command.ChangeTaskCommand(None, self.items, task=newTask).do()
            self._originalTask = newTask

    def addStartAndStopEntries(self):
        # pylint: disable-msg=W0201,W0142
        dateTimeEntryKwArgs = dict(showSeconds=True)
        self._originalStartDateTime = self.items[0].getStart() 
        self._startDateTimeEntry = entry.DateTimeEntry(self, self._settings,
            self._originalStartDateTime, noneAllowed=False, 
            callback=self.onStartDateTimeChanged, **dateTimeEntryKwArgs)
        startFromLastEffortButton = wx.Button(self,
            label=_('Start tracking from last stop time'))
        self.Bind(wx.EVT_BUTTON, self.onStartFromLastEffort,
            startFromLastEffortButton)
        if self._effortList.maxDateTime() is None:
            startFromLastEffortButton.Disable()

        self._originalStopDateTime = self.items[0].getStop()
        self._stopDateTimeEntry = entry.DateTimeEntry(self, self._settings, 
            self._originalStopDateTime, noneAllowed=True, 
            callback=self.onStopDateTimeChanged, **dateTimeEntryKwArgs)
        self.invalidPeriodMessage = wx.StaticText(self, label='')
        font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.FONTWEIGHT_BOLD )
        self.invalidPeriodMessage.SetFont(font)
        
        flags = [None, wx.ALIGN_RIGHT|wx.ALL, wx.ALIGN_LEFT|wx.ALL, None]
        self.addEntry(_('Start'), self._startDateTimeEntry,
            startFromLastEffortButton, flags=flags)
        self.addEntry(_('Stop'), self._stopDateTimeEntry, self.invalidPeriodMessage, flags=flags)

    def onStartDateTimeChanged(self, *args, **kwargs):
        currentStartDateTime = self._startDateTimeEntry.get()
        if currentStartDateTime != self._originalStartDateTime and self.validPeriod():
            command.ChangeEffortStartDateTimeCommand(None, self.items, datetime=currentStartDateTime).do()
            self._originalStartDateTime = currentStartDateTime
        self.updateInvalidPeriodMessage()
        
    def onStopDateTimeChanged(self, *args, **kwargs): 
        currentStopDateTime = self._stopDateTimeEntry.get()
        if currentStopDateTime != self._originalStopDateTime and self.validPeriod():
            command.ChangeEffortStopDateTimeCommand(None, self.items, datetime=currentStopDateTime).do()
            self._originalStopDateTime = currentStopDateTime
        self.updateInvalidPeriodMessage()
        
    def updateInvalidPeriodMessage(self):
        self.invalidPeriodMessage.SetLabel('' if self.validPeriod() else _('Warning: start must be earlier than stop'))
                
    def onStartFromLastEffort(self, event): # pylint: disable-msg=W0613
        self._startDateTimeEntry.set(self._effortList.maxDateTime())
        
    def validPeriod(self):
        if not hasattr(self, '_stopDateTimeEntry'):
            return True
        else:
            return self._startDateTimeEntry.get() < self._stopDateTimeEntry.get()
        
    def addDescriptionEntry(self):
        # pylint: disable-msg=W0201
        self._currentDescription = self.items[0].description() if len(self.items) == 1 else _('Edit to change all descriptions')
        self._descriptionEntry = widgets.MultiLineTextCtrl(self, self._currentDescription)
        self._descriptionEntry.Bind(wx.EVT_KILL_FOCUS, self.onLeavingDescriptionEntry)
        self._descriptionEntry.SetSizeHints(300, 150)
        self.addEntry(_('Description'), self._descriptionEntry, growable=True)
        
    def onLeavingDescriptionEntry(self, event):
        event.Skip()
        newDescription = self._descriptionEntry.GetValue()
        if newDescription != self._currentDescription:
            command.EditDescriptionCommand(None, self.items, description=newDescription).do()
            self._currentDescription = newDescription

    def setFocus(self, columnName):
        self.setFocusOnEntry(columnName)
        
    def isDisplayingItemOrChildOfItem(self, item):
        if hasattr(item, 'setTask'):
            return self.items[0] == item # Regular effort
        else:
            return item.mayContain(self.items[0]) # Composite effort
    
    def entries(self):
        return dict(period=self._stopDateTimeEntry, task=self._taskEntry,
                    firstEntry=self._taskEntry,
                    description=self._descriptionEntry,
                    timeSpent=self._stopDateTimeEntry,
                    revenue=self._taskEntry)
    
    
class Editor(widgets.ButtonLessDialog):
    EditBookClass = lambda: 'Subclass responsibility'
    singular_title = _('Edit %s')
    plural_title = _('Edit multiple items')
    
    def __init__(self, parent, items, settings, container, taskFile, *args, **kwargs):
        self._items = items
        self._settings = settings
        self._taskFile = taskFile
        title = self.plural_title if len(items) > 1 else self.singular_title%items[0].subject()
        super(Editor, self).__init__(parent, title, *args, **kwargs)
        columnName = kwargs.get('columnName', '')
        self._interior.setFocus(columnName)
        patterns.Publisher().registerObserver(self.onItemRemoved, 
            eventType=container.removeItemEventType(), eventSource=container)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        if '__WXMAC__' in wx.PlatformInfo:
            # The window manager does this automatically on other
            # platforms but on Mac OS X it opens by default in the
            # top-left corner of the first display. This gets annoying
            # on a 2560x1440 27" + 1920x1200 24" dual screen...
            self.CentreOnParent()
                
    def createInterior(self):
        return self.EditBookClass(self._panel, self._items, 
                                  self._taskFile, self._settings)

    def onClose(self, event):
        event.Skip()
        patterns.Publisher().removeInstance(self)
                        
    def onItemRemoved(self, event):
        ''' The item we're editing or one of its ancestors has been removed or 
            is hidden by a filter. If the item is really removed, close the tab 
            of the item involved and close the whole editor if there are no 
            tabs left. '''
        if not self:
            return # Prevent _wxPyDeadObject TypeError
        for item in event.values():
            if self._interior.isDisplayingItemOrChildOfItem(item) and not item in self._taskFile:
                self.Close()
                break            


class TaskEditor(Editor):
    plural_title = _('Edit multiple tasks')
    EditBookClass = TaskEditBook


class CategoryEditor(Editor):
    plural_title = _('Edit multiple categories')
    EditBookClass = CategoryEditBook


class NoteEditor(Editor):
    plural_title = _('Edit multiple notes')
    EditBookClass = NoteEditBook


class AttachmentEditor(Editor):
    plural_title = _('Edit multiple attachmentss')
    EditBookClass = AttachmentEditBook


class EffortEditor(Editor):
    plural_title = _('Edit multiple efforts')
    EditBookClass = EffortEditBook
