# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007 Jerome Laheurte <fraca7@free.fr>

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

import wx, StringIO # We cannot use CStringIO since unicode strings are used below.
import test
from taskcoachlib import persistence
from taskcoachlib.domain import task, effort, date, category, note, attachment


class XMLWriterTest(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.fd.name = 'testfile.tsk'
        self.writer = persistence.XMLWriter(self.fd)
        self.task = task.Task()
        self.taskList = task.TaskList([self.task])
        self.category = category.Category('Category')
        self.categoryContainer = category.CategoryList([self.category])
        self.noteContainer = note.NoteContainer()
            
    def __writeAndRead(self):
        self.writer.write(self.taskList, self.categoryContainer, 
            self.noteContainer)
        return self.fd.getvalue()
    
    def expectInXML(self, xmlFragment):
        xml = self.__writeAndRead()
        self.failUnless(xmlFragment in xml, '%s not in %s'%(xmlFragment, xml))
    
    def expectNotInXML(self, xmlFragment):
        xml = self.__writeAndRead()
        self.failIf(xmlFragment in xml, '%s in %s'%(xmlFragment, xml))
    
    # tests
        
    def testVersion(self):
        from taskcoachlib import meta
        self.expectInXML('<?taskcoach release="%s"'%meta.data.version)
        
    def testTaskSubject(self):
        self.task.setSubject('Subject')
        self.expectInXML('subject="Subject"')
        
    def testTaskSubjectWithUnicode(self):
        self.task.setSubject(u'ï¬Ÿï­Žï­–')
        self.expectInXML(u'subject="ï¬Ÿï­Žï­–"')
            
    def testTaskDescription(self):
        self.task.setDescription('Description')
        self.expectInXML('<description>Description</description>')
        
    def testEmptyTaskDescriptionIsNotWritten(self):
        self.expectNotInXML('<description>')
        
    def testTaskStartDate(self):
        self.task.setStartDate(date.Date(2004,1,1))
        self.expectInXML('startdate="%s"'%str(self.task.startDate()))
        
    def testNoStartDate(self):
        self.task.setStartDate(date.Date())
        self.expectNotInXML('startdate')
        
    def testTaskDueDate(self):
        self.task.setDueDate(date.Date(2004,1,1))
        self.expectInXML('duedate="%s"'%str(self.task.dueDate()))

    def testNoDueDate(self):
        self.expectNotInXML('duedate')
                
    def testTaskCompletionDate(self):
        self.task.setCompletionDate(date.Date(2004, 1, 1))
        self.expectInXML('completiondate="%s"'%str(self.task.completionDate()))

    def testNoCompletionDate(self):
        self.expectNotInXML('completiondate')
        
    def testChildTask(self):
        self.task.addChild(task.Task(subject='child'))
        self.expectInXML('subject="child"/></task>')

    def testEffort(self):
        taskEffort = effort.Effort(self.task, date.DateTime(2004,1,1),
            date.DateTime(2004,1,2), description='description\nline 2')
        self.task.addEffort(taskEffort)
        self.expectInXML('<effort start="%s" stop="%s"><description>description\nline 2</description></effort>'% \
            (taskEffort.getStart(), taskEffort.getStop()))
        
    def testThatEffortTimesDoNotContainMilliseconds(self):
        self.task.addEffort(effort.Effort(self.task, 
            date.DateTime(2004,1,1,10,0,0,123456), 
            date.DateTime(2004,1,1,10,0,10,654310)))
        self.expectInXML('start="2004-01-01 10:00:00"')
        self.expectInXML('stop="2004-01-01 10:00:10"')
        
    def testThatEffortStartAndStopAreNotEqual(self):
        self.task.addEffort(effort.Effort(self.task, 
            date.DateTime(2004,1,1,10,0,0,123456), 
            date.DateTime(2004,1,1,10,0,0,654310)))
        self.expectInXML('start="2004-01-01 10:00:00"')
        self.expectInXML('stop="2004-01-01 10:00:01"')
            
    def testEmptyEffortDescriptionIsNotWritten(self):
        self.task.addEffort(effort.Effort(self.task, date.DateTime(2004,1,1),
            date.DateTime(2004,1,2)))
        self.expectNotInXML('<description>')
        
    def testActiveEffort(self):
        self.task.addEffort(effort.Effort(self.task, date.DateTime(2004,1,1)))
        self.expectInXML('<effort start="%s"/>'%self.task.efforts()[0].getStart()) 
                
    def testNoEffortByDefault(self):
        self.expectNotInXML('<efforts>')
        
    def testBudget(self):
        self.task.setBudget(date.TimeDelta(hours=1))
        self.expectInXML('budget="%s"'%str(self.task.budget()))
        
    def testNoBudget(self):
        self.expectNotInXML('budget')
        
    def testBudget_MoreThan24Hour(self):
        self.task.setBudget(date.TimeDelta(hours=25))
        self.expectInXML('budget="25:00:00"')
        
    def testOneCategoryWithoutTask(self):
        self.categoryContainer.append(category.Category('test', id="id"))
        self.expectInXML('<category id="id" subject="test"/>')
    
    def testOneCategoryWithOneTask(self):
        self.categoryContainer.append(category.Category('test', [self.task], id='id'))
        self.expectInXML('<category categorizables="%s" id="id" subject="test"/>'%self.task.id())
        
    def testTwoCategoriesWithOneTask(self):
        subjects = ['test', 'another']
        expectedResult = ''
        for subject in subjects:
            self.categoryContainer.append(category.Category(subject, [self.task], id='dummy'))
            expectedResult += '<category categorizables="%s" id="dummy" subject="%s"/>'%(self.task.id(), subject)
        self.expectInXML(expectedResult)
        
    def testOneCategoryWithSubTask(self):
        child = task.Task()
        self.taskList.append(child)
        self.task.addChild(child)
        self.categoryContainer.append(category.Category('test', [child], id='id'))
        self.expectInXML('<category categorizables="%s" id="id" subject="test"/>'%child.id())
        
    def testSubCategoryWithoutTasks(self):
        parentCategory = category.Category('parent')
        childCategory = category.Category('child')
        parentCategory.addChild(childCategory)
        self.categoryContainer.extend([parentCategory, childCategory])
        self.expectInXML('<category id="%s" subject="parent">'
                         '<category id="%s" subject="child"/></category>'%\
                         (parentCategory.id(), childCategory.id()))

    def testSubCategoryWithOneTask(self):
        parentCategory = category.Category('parent')
        childCategory = category.Category('child', categorizables=[self.task])
        parentCategory.addChild(childCategory)
        self.categoryContainer.extend([parentCategory, childCategory])
        self.expectInXML('<category id="%s" subject="parent">'
                         '<category categorizables="%s" id="%s" subject="child"/>'
                         '</category>'%(parentCategory.id(), self.task.id(), 
                                        childCategory.id()))
    
    def testFilteredCategory(self):
        filteredCategory = category.Category('test', filtered=True, id='id')
        self.categoryContainer.extend([filteredCategory])
        self.expectInXML('<category filtered="True" id="id" subject="test"/>')

    def testCategoryWithDescription(self):
        aCategory = category.Category('subject', description='Description', id='id')
        self.categoryContainer.append(aCategory)
        self.expectInXML('<category id="id" subject="subject"><description>Description</description></category>')
        
    def testCategoryWithUnicodeSubject(self):
        unicodeCategory = category.Category(u'ï¬Ÿï­Žï­–', id='id')
        self.categoryContainer.extend([unicodeCategory])
        self.expectInXML(u'<category id="id" subject="ï¬Ÿï­Žï­–"/>')

    def testCategoryWithDeletedTask(self):
        aCategory = category.Category('category', tasks=[self.task], id='id')
        self.categoryContainer.append(aCategory)
        self.taskList.remove(self.task)
        self.expectInXML('<category id="id" subject="category"/>')
 
    def testDefaultPriority(self):
        self.expectNotInXML('priority')
        
    def testPriority(self):
        self.task.setPriority(5)
        self.expectInXML('priority="5"')
        
    def testTaskId(self):
        self.expectInXML('id="%s"'%self.task.id())
        
    def testCategoryId(self):
        aCategory = category.Category('category')
        self.categoryContainer.append(aCategory)
        self.expectInXML('id="%s"'%aCategory.id())

    def testNoteId(self):
        aNote = note.Note('note')
        self.noteContainer.append(aNote)
        self.expectInXML('id="%s"'%aNote.id())

    def testTwoTasks(self):
        self.task.setSubject('task 1')
        task2 = task.Task('task 2')
        self.taskList.append(task2)
        self.expectInXML('subject="task 2"')

    def testDefaultHourlyFee(self):
        self.expectNotInXML('hourlyFee')
        
    def testHourlyFee(self):
        self.task.setHourlyFee(100)
        self.expectInXML('hourlyFee="100"')
        
    def testDefaultFixedFee(self):
        self.expectNotInXML('fixedFee')
        
    def testFixedFee(self):
        self.task.setFixedFee(1000)
        self.expectInXML('fixedFee="1000"')

    def testNoReminder(self):
        self.expectNotInXML('reminder')
        
    def testReminder(self):
        self.task.setReminder(date.DateTime(2005, 5, 7, 13, 15, 10))
        self.expectInXML('reminder="%s"'%str(self.task.reminder()))
        
    def testMarkCompletedWhenAllChildrenAreCompletedSetting_None(self):
        self.expectNotInXML('shouldMarkCompletedWhenAllChildrenCompleted')
            
    def testMarkCompletedWhenAllChildrenAreCompletedSetting_True(self):
        self.task.shouldMarkCompletedWhenAllChildrenCompleted = True
        self.expectInXML('shouldMarkCompletedWhenAllChildrenCompleted="True"')
            
    def testMarkCompletedWhenAllChildrenAreCompletedSetting_False(self):
        self.task.shouldMarkCompletedWhenAllChildrenCompleted = False
        self.expectInXML('shouldMarkCompletedWhenAllChildrenCompleted="False"')
              
    def testNote(self):
        self.noteContainer.append(note.Note(id='id'))
        self.expectInXML('<note id="id"/>')
        
    def testNoteWithSubject(self):
        self.noteContainer.append(note.Note(subject='Note', id='id'))
        self.expectInXML('<note id="id" subject="Note"/>')
        
    def testNoteWithDescription(self):
        self.noteContainer.append(note.Note(description='Description', id='id'))
        self.expectInXML('<note id="id"><description>Description</description></note>')
        
    def testNoteWithChild(self):
        aNote = note.Note(id='parent')
        child = note.Note(id='child')
        aNote.addChild(child)
        self.noteContainer.append(aNote)
        self.expectInXML('<note id="parent"><note id="child"/></note>')
        
    def testNoteWithCategory(self):
        cat = category.Category('cat', id='catId')
        self.categoryContainer.append(cat)
        aNote = note.Note('note', id='noteId', categories=[cat])
        self.noteContainer.append(aNote)
        cat.addCategorizable(aNote)
        self.expectInXML('<category categorizables="noteId" id="catId" subject="cat"/>')

    def testCategoryColor(self):
        self.categoryContainer.append(category.Category('test', color=wx.RED))
        self.expectInXML('color="(255, 0, 0, 255)"')

    def testDontWriteInheritedCategoryColor(self):
        parent = category.Category('test', color=wx.RED)
        child = category.Category(subject='child', id='id')
        parent.addChild(child)
        self.categoryContainer.append(parent)
        self.expectInXML('<category id="id" subject="child"/>')
        
    def testTaskColor(self):
        self.task.setColor(wx.RED)
        self.expectInXML('color="(255, 0, 0, 255)"')
        
    def testDontWriteInheritedTaskColor(self):
        self.task.setColor(wx.RED)
        child = task.Task(subject='child', id='id', startDate=date.Date())
        self.task.addChild(child)
        self.taskList.append(child)
        self.expectInXML('<task id="id" subject="child"/>')

    def testNoteColor(self):
        aNote = note.Note(color=wx.RED)
        self.noteContainer.append(aNote)
        self.expectInXML('color="(255, 0, 0, 255)"')
        
    def testDontWriteInheritedNoteColor(self):
        parent = note.Note(color=wx.RED)
        child = note.Note(subject='child', id='id')
        parent.addChild(child)
        self.noteContainer.append(parent)
        self.expectInXML('<note id="id" subject="child"/>')
        
    def testNoRecurencce(self):
        self.expectNotInXML('recurrence')
        
    def testDailyRecurrence(self):
        self.task.setRecurrence(date.Recurrence('daily'))
        self.expectInXML('<recurrence unit="daily"/>')
        
    def testWeeklyRecurrence(self):
        self.task.setRecurrence(date.Recurrence('weekly'))
        self.expectInXML('<recurrence unit="weekly"/>')

    def testMonthlyRecurrence(self):
        self.task.setRecurrence(date.Recurrence('monthly'))
        self.expectInXML('<recurrence unit="monthly"/>')

    def testYearlyRecurrence(self):
        self.task.setRecurrence(date.Recurrence('yearly'))
        self.expectInXML('<recurrence unit="yearly"/>')
        
    def testRecurrenceCount(self):
        self.task.setRecurrence(date.Recurrence('daily', count=5))
        self.expectInXML('count="5"')

    def testMaxRecurrenceCount(self):
        self.task.setRecurrence(date.Recurrence('daily', max=5))
        self.expectInXML('max="5"')
        
    def testRecurrenceFrequency(self):
        self.task.setRecurrence(date.Recurrence('daily', amount=2))
        self.expectInXML('amount="2"')

    def testNoAttachments(self):
        self.expectNotInXML('attachment')
        
    def testTaskWithOneAttachment(self):
        self.task.addAttachments(attachment.FileAttachment('whatever.txt', id='foo'))
        self.expectInXML('<attachment id="foo" location="whatever.txt" subject="whatever.txt" type="file"/>')

    def testObjectWithAttachmentWithNote(self):
        att = attachment.FileAttachment('whatever.txt', id='foo')
        self.task.addAttachments(att)
        att.addNote(note.Note(subject='attnote', id='spam'))
        self.expectInXML('<attachment id="foo" location="whatever.txt" subject="whatever.txt" type="file"><note')

    def testNoteWithOneAttachment(self):
        aNote = note.Note()
        self.noteContainer.append(aNote)
        aNote.addAttachments(attachment.FileAttachment('whatever.txt', id='foo'))
        self.expectInXML('<attachment id="foo" location="whatever.txt" subject="whatever.txt" type="file"/>')

    def testCategoryWithOneAttachment(self):
        cat = category.Category('cat')
        self.categoryContainer.append(cat)
        cat.addAttachments(attachment.FileAttachment('whatever.txt', id='foo'))
        self.expectInXML('<attachment id="foo" location="whatever.txt" subject="whatever.txt" type="file"/>')
        
    def testTaskWithTwoAttachments(self):
        attachments = [attachment.FileAttachment('whatever.txt'),
                       attachment.FileAttachment('/home/frank/attachment.doc')]
        for a in attachments:
            self.task.addAttachments(a)
        self.expectInXML(''.join(['<attachment id="%s" location="%s" subject="%s" type="file"/>' % (k.id(), k.location(), k.location()) for k in attachments]))
        
    def testTaskWithNote(self):
        aNote = note.Note(subject='Note', id='id')
        self.task.addNote(aNote)
        self.expectInXML('><note id="id" subject="Note"/></task>')

    def testTaskWithNotes(self):
        note1 = note.Note(subject='Note1', id='1')
        note2 = note.Note(subject='Note2', id='2')
        self.task.addNote(note1)
        self.task.addNote(note2)
        self.expectInXML('><note id="1" subject="Note1"/>'
            '<note id="2" subject="Note2"/></task>')
        
    def testTaskWithNestedNotes(self):
        aNote = note.Note(subject='Note', id='1')
        subNote = note.Note(subject='Subnote', id='2')
        aNote.addChild(subNote)
        self.task.addNote(aNote)
        self.expectInXML('><note id="1" subject="Note">'
            '<note id="2" subject="Subnote"/></note></task>')

    def testCategoryWithNote(self):
        aNote = note.Note(subject='Note', id='id')
        self.category.addNote(aNote)
        self.expectInXML('><note id="id" subject="Note"/></category>')

    def testCategoryWithNotes(self):
        note1 = note.Note(subject='Note1', id='1')
        note2 = note.Note(subject='Note2', id='2')
        self.category.addNote(note1)
        self.category.addNote(note2)
        self.expectInXML('><note id="1" subject="Note1"/>'
            '<note id="2" subject="Note2"/></category>')
        
    def testCategoryWithNestedNotes(self):
        aNote = note.Note(subject='Note', id='1')
        subNote = note.Note(subject='Subnote', id='2')
        aNote.addChild(subNote)
        self.category.addNote(aNote)
        self.expectInXML('><note id="1" subject="Note">'
            '<note id="2" subject="Subnote"/></note></category>')

    def testTaskDefaultExpansionState(self):
        # Don't write anything if the task is not expanded: 
        self.expectNotInXML('expandedContexts')

    def testTaskExpansionState(self):
        self.task.expand()
        self.expectInXML('''expandedContexts="('None',)"''')

    def testTaskExpansionState_SpecificContext(self):
        self.task.expand(context='Test')
        self.expectInXML('''expandedContexts="('Test',)"''')

    def testTaskExpansionState_MultipleContexts(self):
        self.task.expand(context='Test')
        self.task.expand(context='Another context')
        self.expectInXML('''expandedContexts="('Another context', 'Test')"''')

    def testCategoryExpansionState(self):
        cat = category.Category('cat')
        self.categoryContainer.append(cat)
        cat.expand()
        self.expectInXML('''expandedContexts="('None',)"''')

    def testNoteExpansionState(self):
        aNote = note.Note()
        self.noteContainer.append(aNote)
        aNote.expand()
        self.expectInXML('''expandedContexts="('None',)"''')
