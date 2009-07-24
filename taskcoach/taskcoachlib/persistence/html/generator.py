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

import wx, cgi
from taskcoachlib.gui import color


def viewer2html(viewer, settings, cssFilename=None, selectionOnly=False):
    converter = Viewer2HTMLConverter(viewer, settings)
    return converter(cssFilename, selectionOnly) 


class Viewer2HTMLConverter(object):
    ''' Class to convert the visible contents of a viewer into HTML.'''
    
    docType = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'
    metaTag = '<meta http-equiv="Content-Type" content="text/html;charset=utf-8">'
    cssLink = '<link href="%s" rel="stylesheet" type="text/css" media="screen">'

    def __init__(self, viewer, settings):
        super(Viewer2HTMLConverter, self).__init__()
        self.viewer = viewer
        self.settings = settings
        
    def __call__(self, cssFilename, selectionOnly):
        ''' Create an HTML document. '''
        lines = [self.docType] + self.html(cssFilename, selectionOnly) + ['']
        return '\n'.join(lines), self.count
    
    def html(self, cssFilename, selectionOnly, level=0):
        ''' Returns all HTML, consisting of header and body. '''
        htmlContent = self.htmlHeader(cssFilename, level+1) + \
                      self.htmlBody(selectionOnly, level+1)
        return self.wrap(htmlContent, 'html', level)
    
    def htmlHeader(self, cssFilename, level):
        ''' Return the HTML header <head>. '''
        htmlHeaderContent = self.htmlHeaderContent(cssFilename, level+1)
        return self.wrap(htmlHeaderContent, 'head', level)
        
    def htmlHeaderContent(self, cssFilename, level):
        ''' Returns the HTML header section, containing meta tag, title, and
            optional link to a CSS stylesheet. '''
        htmlHeaderContent = [self.indent(self.metaTag, level), 
                             self.wrap(self.viewer.title(), 'title', level, oneLine=True)] + \
                            self.style(level)
        if cssFilename:
            htmlHeaderContent.append(self.indent(self.cssLink%cssFilename, level))
        return htmlHeaderContent
    
    def style(self, level):
        ''' Add a style section that contains the alignment for the columns. '''
        visibleColumns = self.viewer.visibleColumns()
        columnAlignments = [{wx.LIST_FORMAT_LEFT: 'left',
                             wx.LIST_FORMAT_CENTRE: 'center',
                             wx.LIST_FORMAT_RIGHT: 'right'}[column.alignment()]
                             for column in visibleColumns]
        styleContent = []
        for column, alignment in zip(visibleColumns, columnAlignments):
            columnStyle = self.indent('.%s {text-align: %s}'%(column.name(), alignment), level+1)
            styleContent.append(columnStyle)
        if self.viewer.isShowingTasks():
            for status in 'completed', 'duetoday', 'overdue', 'inactive', 'active':
                statusColor = color.taskColorForStatus(status, self.settings)
                statusColor = self.cssColorSyntax(statusColor)
                statusStyle = '.%s {color: %s}'%(status, statusColor)
                styleContent.append(self.indent(statusStyle, level+1))
        return self.wrap(styleContent, 'style', level, type='text/css')
    
    def htmlBody(self, selectionOnly, level):
        ''' Returns the HTML body section, containing one table with all 
            visible data. '''
        htmlBodyContent = self.table(selectionOnly, level+1)
        return self.wrap(htmlBodyContent, 'body', level)
    
    def table(self, selectionOnly, level):
        ''' Returns the table, consisting of caption, table header and table 
            body. '''
        visibleColumns = self.viewer.visibleColumns()
        tableContent = [self.tableCaption(level+1)] + \
                       self.tableHeader(visibleColumns, level+1) + \
                       self.tableBody(visibleColumns, selectionOnly, level+1)
        return self.wrap(tableContent, 'table', level, id='table')
                
    def tableCaption(self, level):
        ''' Returns the table caption, based on the viewer title. '''
        return self.wrap(self.viewer.title(), 'caption', level, oneLine=True)
    
    def tableHeader(self, visibleColumns, level):
        ''' Returns the table header section <thead> containing the header
            row with the column headers. '''
        tableHeaderContent = self.headerRow(visibleColumns, level+1)
        return self.wrap(tableHeaderContent, 'thead', level)
        
    def headerRow(self, visibleColumns, level):
        ''' Returns the header row <tr> for the table. '''
        headerRowContent = []
        for column in visibleColumns:
            headerRowContent.append(self.headerCell(column, level+1))
        return self.wrap(headerRowContent, 'tr', level, **{'class': 'header'})
        
    def headerCell(self, column, level):
        ''' Returns a table header <th> for the specific column. '''
        header = column.header() or '&nbsp;'
        name = column.name()
        attributes = {'scope': 'col', 'class': name}
        if self.viewer.isSortable() and self.viewer.isSortedBy(name):
            attributes['id'] = 'sorted'
        return self.wrap(header, 'th', level, oneLine=True, **attributes)
    
    def tableBody(self, visibleColumns, selectionOnly, level):
        ''' Returns the table body <tbody>. ''' 
        tree = self.viewer.isTreeViewer()
        self.count = 0
        tableBodyContent = []
        for item in self.viewer.visibleItems():
            if selectionOnly and not self.viewer.isselected(item):
                continue
            self.count += 1
            tableBodyContent.extend(self.bodyRow(item, visibleColumns, tree, level+1))
        return self.wrap(tableBodyContent, 'tbody', level)
    
    def bodyRow(self, item, visibleColumns, tree, level):
        ''' Returns a <tr> containing the values of item for the 
            visibleColumns. '''
        bodyRowContent = []
        for column in visibleColumns:
            renderedItem = self.render(item, column, indent=not bodyRowContent and tree)
            bodyRowContent.append(self.bodyCell(renderedItem, column, level+1))
        style = self.bodyRowStyleAttribute(item)
        attributes = dict(style=style) if style else dict()
        if self.viewer.isShowingTasks(): 
            if item.completed():
                attributes['class'] = 'completed'
            elif item.overdue():
                attributes['class'] = 'overdue'
            elif item.dueToday():
                attributes['class'] = 'duetoday'
            elif item.inactive():
                attributes['class'] = 'inactive'
            else:
                attributes['class'] = 'active'
        return self.wrap(bodyRowContent, 'tr', level, **attributes)
    
    def bodyRowStyleAttribute(self, item):
        ''' Determine the style attribute for item. Returns a CSS style
            specification: 'background: <color>'. '''
        bgColor = self.viewer.getBackgroundColor(item)
        style = 'background: %s'%self.cssColorSyntax(bgColor) if bgColor else ''
        return style
    
    def bodyCell(self, item, column, level):
        ''' Return a <td> for the item/column combination, using the specified
            aligment (one of 'left', 'center', 'right'). '''
        attributes = {'class': column.name()}
        return self.wrap(item, 'td', level, oneLine=True, **attributes)
    
    @classmethod
    def wrap(class_, lines, tagName, level, oneLine=False, **attributes):
        ''' Wrap one or more lines with <tagName [optional attributes]> and 
            </tagName>. '''
        if attributes:
            attributes = ' ' + ' '.join(sorted('%s="%s"'%(key, value) for key, value in attributes.iteritems()))
        else:
            attributes = ''
        openTag = '<%s%s>'%(tagName, attributes)
        closeTag = '</%s>'%tagName
        if oneLine:
            return class_.indent(openTag + lines + closeTag, level)
        else:
            return [class_.indent(openTag, level)] + \
                   lines + \
                   [class_.indent(closeTag, level)]
    
    @staticmethod
    def indent(htmlText, level=0):
        ''' Indent the htmlText with spaces according to the level, so that
            the resulting HTML looks nicely indented. '''
        return '  ' * level + htmlText
    
    @classmethod
    def cssColorSyntax(class_, color):
        ''' Translate the wx-color, either a wx.Color instance or a tuple, 
            into CSS syntax. ''' 
        try:
            return color.GetAsString(wx.C2S_HTML_SYNTAX)
        except AttributeError: # color is a tuple
            return class_.cssColorSyntax(wx.Color(*color))
        
    @staticmethod
    def render(item, column, indent=False):
        ''' Render the item based on the column, escape HTML and indent if 
            the item with non-breaking spaces, if indent == True. '''
        # Escape the rendered item and then replace newlines with <br>. 
        renderedItem = cgi.escape(column.render(item)).replace('\n', '<br>')
        if indent:
            # Indent the subject with whitespace
            renderedItem = '&nbsp;' * len(item.ancestors()) * 3 + renderedItem
        if not renderedItem:
            # Make sure the empty cell is drawn
            renderedItem = '&nbsp;'
        return renderedItem
        