'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

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

from taskcoachlib import patterns
from taskcoachlib.domain import base 
from taskcoachlib.domain.attribute import font, color


class CategorizableCompositeObject(base.CompositeObject):
    ''' CategorizableCompositeObjects are composite objects that can be
        categorized by adding them to one or more categories. Examples of
        categorizable composite objects are tasks and notes. '''
        
    def __init__(self, *args, **kwargs):
        self.__categories = base.SetAttribute(kwargs.pop('categories', set()),
                                              self, 
                                              self.addCategoryEvent, 
                                              self.removeCategoryEvent)
        super(CategorizableCompositeObject, self).__init__(*args, **kwargs)
        
    def __getstate__(self):
        state = super(CategorizableCompositeObject, self).__getstate__()
        state.update(dict(categories=self.categories()))
        return state

    @patterns.eventSource
    def __setstate__(self, state, event=None):
        super(CategorizableCompositeObject, self).__setstate__(state, event=event)
        self.setCategories(state['categories'], event=event)

    def __getcopystate__(self):
        state = super(CategorizableCompositeObject, self).__getcopystate__()
        state.update(dict(categories=self.categories()))
        return state
        
    def categories(self, recursive=False, upwards=False):
        result = self.__categories.get()
        if recursive and upwards and self.parent() is not None:
            result |= self.parent().categories(recursive=True, upwards=True)
        elif recursive and not upwards:
            for child in self.children(recursive=True):
                result |= child.categories()
        return result


    @classmethod
    def categoriesChangedEventType(class_): # called categories to match with sort key
        return 'categorizable.categories'
        
    @classmethod
    def categoryAddedEventType(class_):
        return 'categorizable.category.add'

    def addCategory(self, *categories, **kwargs):
        self.__categories.add(set(categories), event=kwargs.pop('event', None))
            
    def addCategoryEvent(self, event, *categories):
        event.addSource(self, self.categories(), type=self.categoriesChangedEventType())
        event.addSource(self, *categories, **dict(type=self.categoryAddedEventType()))
        for child in self.children(recursive=True):
            event.addSource(child, *categories, 
                            **dict(type=child.categoryAddedEventType()))
        if not self.foregroundColor(recursive=False) and any(category.foregroundColor(recursive=True) for category in categories):
            self.foregroundColorChangedEvent(event)
        if not self.backgroundColor(recursive=False) and any(category.backgroundColor(recursive=True) for category in categories):
            self.backgroundColorChangedEvent(event)
        if not self.font(recursive=False) and any(category.font(recursive=True) for category in categories):
            self.fontChangedEvent(event)
        if not self.icon(recursive=False) and any(category.icon(recursive=True) for category in categories):
            self.iconChangedEvent(event)

    @classmethod
    def categoryRemovedEventType(class_):
        return 'categorizable.category.remove'
    
    def removeCategory(self, *categories, **kwargs):
        self.__categories.remove(set(categories), event=kwargs.pop('event', None))
            
    def removeCategoryEvent(self, event, *categories):
        event.addSource(self, self.categories(), type=self.categoriesChangedEventType())
        event.addSource(self, *categories, **dict(type=self.categoryRemovedEventType()))
        for child in self.children(recursive=True):
            event.addSource(child, *categories, 
                            **dict(type=child.categoryRemovedEventType()))
        if not self.foregroundColor(recursive=False) and any(category.foregroundColor(recursive=True) for category in categories):
            self.foregroundColorChangedEvent(event)
        if not self.backgroundColor(recursive=False) and any(category.backgroundColor(recursive=True) for category in categories):
            self.backgroundColorChangedEvent(event)
        if not self.font(recursive=False) and any(category.font(recursive=True) for category in categories):
            self.fontChangedEvent(event)
        if not self.icon(recursive=False) and any(category.icon(recursive=True) for category in categories):
            self.iconChangedEvent(event)
            
    def setCategories(self, categories, event=None):
        self.__categories.set(set(categories), event=event)

    @staticmethod
    def categoriesSortFunction(**kwargs):
        ''' Return a sort key for sorting by categories. Since a categorizable
            can have multiple categories we first sort the categories by their
            subjects. If the sorter is in tree mode, we also take the categories
            of the children of the categorizable into account, after the 
            categories of the categorizable itself. '''
        def sortKeyFunction(categorizable):
            def sortedSubjects(items):
                return sorted([item.subject(recursive=True) for item in items])
            categories = categorizable.categories()
            sortedCategorySubjects = sortedSubjects(categories)
            if kwargs.get('treeMode', False):
                childCategories = categorizable.categories(recursive=True) - categories
                sortedCategorySubjects.extend(sortedSubjects(childCategories)) 
            return sortedCategorySubjects
        return sortKeyFunction

    def foregroundColor(self, recursive=True):
        myOwnFgColor = super(CategorizableCompositeObject, self).foregroundColor(False)
        if myOwnFgColor or not recursive:
            return myOwnFgColor
        categoryBasedFgColor = self._categoryForegroundColor()
        if categoryBasedFgColor:
            return categoryBasedFgColor
        else:
            return super(CategorizableCompositeObject, self).foregroundColor(True)
                
    def backgroundColor(self, recursive=True):
        myOwnBgColor = super(CategorizableCompositeObject, self).backgroundColor(False)
        if myOwnBgColor or not recursive:
            return myOwnBgColor
        categoryBasedBgColor = self._categoryBackgroundColor()
        if categoryBasedBgColor:
            return categoryBasedBgColor
        else:
            return super(CategorizableCompositeObject, self).backgroundColor(True)

    def _categoryForegroundColor(self):
        ''' If a categorizable object belongs to a category that has a 
            foreground color associated with it, the categorizable object is 
            colored accordingly. When a categorizable object belongs to 
            multiple categories, the color is mixed. If a categorizable 
            composite object has no foreground color of its own, it uses its 
            parent's foreground color. '''
        colors = [category.foregroundColor() for category in self.categories()]
        return color.ColorMixer.mix(colors)

    def _categoryBackgroundColor(self):
        ''' If a categorizable object belongs to a category that has a 
            background color associated with it, the categorizable object is 
            colored accordingly. When a categorizable object belongs to 
            multiple categories, the color is mixed. If a categorizable 
            composite object has no background color of its own, it uses its 
            parent's background color. '''
        colors = [category.backgroundColor() for category in self.categories()]
        return color.ColorMixer.mix(colors)
    
    def font(self, recursive=False):
        myFont = super(CategorizableCompositeObject, self).font(recursive=False)
        if myFont or not recursive:
            return myFont
        categoryBasedFont = self._categoryFont()
        if categoryBasedFont:
            return categoryBasedFont
        else:
            return super(CategorizableCompositeObject, self).font(recursive=True)

    def _categoryFont(self):
        ''' If a categorizable object belongs to a category that has a 
            font associated with it, the categorizable object uses that font. 
            When a categorizable object belongs to multiple categories, the 
            font is mixed. If a categorizable composite object has no font of 
            its own, it uses its parent's font. '''
        fonts = [category.font(recursive=True) for category in self.categories()]
        return font.FontMixer.mix(*fonts)

    def icon(self, recursive=False):
        icon = super(CategorizableCompositeObject, self).icon(recursive=False)
        if not icon and recursive:
            icon = self.categoryIcon() or super(CategorizableCompositeObject, self).icon(recursive=True)
        return icon

    def categoryIcon(self):
        for category in self.categories():
            icon = category.icon(recursive=True)
            if icon:
                return icon
        return ''

    def selectedIcon(self, recursive=False):
        icon = super(CategorizableCompositeObject, self).selectedIcon(recursive=False)
        if not icon and recursive:
            icon = self.categorySelectedIcon() or super(CategorizableCompositeObject, self).selectedIcon(recursive=True)
        return icon

    def categorySelectedIcon(self):
        for category in self.categories():
            icon = category.selectedIcon(recursive=True)
            if icon:
                return icon
        return ''
        
    @classmethod
    def categorySubjectChangedEventType(class_):
        return 'categorizable.category.subject'
    
    def categorySubjectChangedEvent(self, event, subject):
        for categorizable in [self] + self.children(recursive=True):
            event.addSource(categorizable, subject,
                            type=categorizable.categorySubjectChangedEventType())
                    
    @classmethod
    def modificationEventTypes(class_):
        eventTypes = super(CategorizableCompositeObject, class_).modificationEventTypes()
        return eventTypes + [class_.categoryAddedEventType(),
                             class_.categoryRemovedEventType()]
