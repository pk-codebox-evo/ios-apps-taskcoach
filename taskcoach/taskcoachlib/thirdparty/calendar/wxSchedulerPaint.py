#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wxSchedule import wxSchedule
from wxDrawer import wxBaseDrawer, wxFancyDrawer
from wxSchedulerCore import *
import calendar
import string
import sys
import wx
import wxScheduleUtils as utils

if sys.version.startswith( "2.3" ):
	from sets import Set as set


# Events 
wxEVT_COMMAND_SCHEDULE_ACTIVATED = wx.NewEventType()
EVT_SCHEDULE_ACTIVATED = wx.PyEventBinder( wxEVT_COMMAND_SCHEDULE_ACTIVATED )

wxEVT_COMMAND_SCHEDULE_RIGHT_CLICK = wx.NewEventType()
EVT_SCHEDULE_RIGHT_CLICK = wx.PyEventBinder( wxEVT_COMMAND_SCHEDULE_RIGHT_CLICK )

wxEVT_COMMAND_SCHEDULE_DCLICK = wx.NewEventType()
EVT_SCHEDULE_DCLICK = wx.PyEventBinder( wxEVT_COMMAND_SCHEDULE_DCLICK )


class DummyDC(object):
	"""
	This fakes  a DC/GraphicsContext  except for the  methods that
	allow to compute text extent.
	"""

	def __init__(self, dc):
		self._dc = dc

	def GetFont(self):
		return self._dc.GetFont()

	def SetFont(self, font, *args):
		self._dc.SetFont(font, *args)

	def GetTextExtent(self, text):
		return self._dc.GetTextExtent(text)

	def __getattr__(self, name):
		return lambda *args, **kwargs: None


class wxSchedulerSizer(wx.PySizer):
	def __init__(self, minSizeCallback):
		super(wxSchedulerSizer, self).__init__()

		self._minSizeCallback = minSizeCallback

	def CalcMin(self):
		return self._minSizeCallback()


# Main class
class wxSchedulerPaint( object ):
	
	def __init__( self, *args, **kwds ):
		super( wxSchedulerPaint, self ).__init__( *args, **kwds )
		
		# If possible, enable autobuffered dc
		self._autoBufferedDC = hasattr( self, 'SetBackgroundStyle' )

		if self._autoBufferedDC:
			self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )

		self._resizable		= False
		self._style = wxSCHEDULER_VERTICAL

		self._drawerClass = wxBaseDrawer
		#self._drawerClass = wxFancyDrawer

		if isinstance(self, wx.ScrolledWindow):
			self.SetSizer(wxSchedulerSizer(self.CalcMinSize))

	def _doClickControl( self, point ):
		self._processEvt( wxEVT_COMMAND_SCHEDULE_ACTIVATED, point )

	def _doRightClickControl( self, point ):
		self._processEvt( wxEVT_COMMAND_SCHEDULE_RIGHT_CLICK, point )
		
	def _doDClickControl( self, point ):
		self._processEvt( wxEVT_COMMAND_SCHEDULE_DCLICK, point )

	def _findSchedule( self, point ):
		"""
		Check if the point is on a schedule and return the schedule
		"""
		for schedule, pointMin, pointMax in self._schedulesCoords:
			inX = ( pointMin.x <= point.x ) & ( point.x <= pointMax.x )
			inY = ( pointMin.y <= point.y ) & ( point.y <= pointMax.y )
			
			if inX & inY:
				return schedule.GetClientData()

		for dt, pointMin, pointMax in self._datetimeCoords:
			inX = ( pointMin.x <= point.x ) & ( point.x <= pointMax.x )
			inY = ( pointMin.y <= point.y ) & ( point.y <= pointMax.y )
			
			if inX & inY:
				return dt


	def _getSchedInPeriod( schedules, start, end):
		"""
		Returns a list of copied schedules that intersect with
		the  period  defined by	 'start'  and 'end'.  Schedule
		start and end are trimmed so as to lie between 'start'
		and 'end'.
		"""
		results = []

		for schedule in schedules:
			if schedule.start.IsLaterThan(end):
				continue
                        if start.IsLaterThan(schedule.end):
				continue

			newSchedule = schedule.Clone()
			# This is used to find the original schedule object in _findSchedule.
			newSchedule.clientdata	= schedule

			if start.IsLaterThan(schedule.start):
				newSchedule.start = utils.copyDateTime(start)
			if schedule.end.IsLaterThan(end):
				newSchedule.end = utils.copyDateTime(end)

                        results.append(newSchedule)

		return results

	_getSchedInPeriod = staticmethod(_getSchedInPeriod)

	def _splitSchedules( self, schedules ):
		"""
		Returns	 a list	 of lists  of schedules.  Schedules in
		each list are guaranteed not to collide.
		"""
		results = []
		current = []

		schedules = schedules[:] # Don't alter original list
		def compare(a, b):
			if a.start.IsEqualTo(b.start):
				return 0
			if a.start.IsEarlierThan(b.start):
				return -1
			return 1
		schedules.sort(compare)

		def findNext(schedule):
			# Among schedules that start after this one ends, find the "nearest".
			candidateSchedule = None
			minDelta = None
			for sched in schedules:
				if sched.start.IsLaterThan(schedule.end):
					delta = sched.start.Subtract(schedule.end)
					if minDelta is None or minDelta > delta:
						minDelta = delta
						candidateSchedule = sched
			return candidateSchedule

		while schedules:
			schedule = schedules[0]
			while schedule:
				current.append(schedule)
				schedules.remove(schedule)
				schedule = findNext(schedule)
			results.append(current)
			current = []

		return results

	def _paintPeriod(self, drawer, start, daysCount, x, y, width, height):
		end = utils.copyDateTime(start)
		end.AddDS(wx.DateSpan(days=daysCount))

		blocks = self._splitSchedules(self._getSchedInPeriod(self._schedules, start, end))
		offsetY = 0

		if blocks:
			dayWidth = width / len(blocks)

			if self._showOnlyWorkHour:
				workingHours = [(self._startingHour, self._startingPauseHour),
						(self._endingPauseHour, self._endingHour)]
			else:
				workingHours = [(self._startingHour, self._endingHour)]

			for idx, block in enumerate(blocks):
				maxDY = 0

				for schedule in block:
					if self._style == wxSCHEDULER_VERTICAL:
						xx, yy, w, h = drawer.DrawScheduleVertical(schedule, start, workingHours,
											   x + dayWidth * idx, y,
											   dayWidth, height)
					elif self._style == wxSCHEDULER_HORIZONTAL:
						xx, yy, w, h = drawer.DrawScheduleHorizontal(schedule, start, daysCount, workingHours,
											     x, y + offsetY, width, height)
						maxDY = max(maxDY, h)

					self._schedulesCoords.append((schedule, wx.Point(xx, yy), wx.Point(xx + w, yy + h)))

				offsetY += maxDY

		for dayN in xrange(daysCount):
			theDay = utils.copyDateTime(start)
			theDay.AddDS(wx.DateSpan(days=dayN))
			theDay.SetSecond(0)

			nbHours = len(self._lstDisplayedHours)

			for idx, hour in enumerate(self._lstDisplayedHours):
				theDay.SetHour(hour.GetHour())
				theDay.SetMinute(hour.GetMinute())

				if self._style == wxSCHEDULER_VERTICAL:
					self._datetimeCoords.append((utils.copyDateTime(theDay),
								     wx.Point(x + 1.0 * width * dayN / daysCount,
									      y + 1.0 * height * idx / nbHours),
								     wx.Point(x + 1.0 * width * (dayN + 1) / daysCount,
									      y + 1.0 * height * (idx + 1) / nbHours)))
				else:
					self._datetimeCoords.append((utils.copyDateTime(theDay),
								     wx.Point(x + 1.0 * width * (nbHours * dayN + idx) / (nbHours * daysCount),
									      y),
								     wx.Point(x + 1.0 * width * (nbHours * dayN + idx + 1) / (nbHours * daysCount),
									      y + height)))

		if self._style == wxSCHEDULER_VERTICAL:
			return max(width, DAY_SIZE_MIN.width), max(height, DAY_SIZE_MIN.height)
		else:
			return max(width, DAY_SIZE_MIN.width), offsetY

	def _paintDay( self, drawer, day, x, y, width, height ):
		"""
		Draw column schedules
		"""

		start = utils.copyDateTime(day)
		start.SetHour(0)
		start.SetMinute(0)
		start.SetSecond(0)

		return self._paintPeriod(drawer, start, 1, x, y, width, height)

	def _paintDaily( self, drawer, day, x, y, width, height ):
		"""
		Display day schedules
		"""

		minWidth = minHeight = 0

		if self._style == wxSCHEDULER_VERTICAL:
			x += LEFT_COLUMN_SIZE
			width -= LEFT_COLUMN_SIZE

		w, h = drawer.DrawDayHeader(day, x, y, width, height)
		minHeight += h
		y += h
		height -= h

		if self._style == wxSCHEDULER_VERTICAL:
			x -= LEFT_COLUMN_SIZE
			width += LEFT_COLUMN_SIZE

		w, h = drawer.DrawHours(x, y, width, height, self._style)

		if self._style == wxSCHEDULER_VERTICAL:
			minWidth += w
			x += w
			width -= w
		else:
			minHeight += h
			y += h
			height -= h

		w, h = self._paintDay( drawer, day, x, y, width, height )

		minWidth += w
		minHeight += h

		return minWidth, minHeight

	def _paintWeekly( self, drawer, day, x, y, width, height ):
		"""
		Display weekly schedule
		"""

		firstDay = utils.setToWeekDayInSameWeek( day, 0, self._weekstart )
		firstDay.SetHour(0)
		firstDay.SetMinute(0)
		firstDay.SetSecond(0)

		minWidth = minHeight = 0

		if self._style == wxSCHEDULER_VERTICAL:
			x += LEFT_COLUMN_SIZE
			width -= LEFT_COLUMN_SIZE

		maxDY = 0
		for weekday in xrange(7):
			theDay = utils.setToWeekDayInSameWeek(utils.copyDateTime(firstDay), weekday, self._weekstart)
			w, h = drawer.DrawDayHeader(theDay, x + weekday * 1.0 * width / 7, y, 1.0 * width / 7, height,
						    highlight=theDay.IsSameDate(wx.DateTime.Now()))
			maxDY = max(maxDY, h)

		if self._style == wxSCHEDULER_VERTICAL:
			x -= LEFT_COLUMN_SIZE
			width += LEFT_COLUMN_SIZE

		minHeight += maxDY
		y += maxDY
		height -= maxDY

		if self._style == wxSCHEDULER_VERTICAL:
			w, h = drawer.DrawHours(x, y, width, height, self._style)

			minWidth += w
			x += w
			width -= w

			for weekday in xrange(7):
				theDay = utils.setToWeekDayInSameWeek(utils.copyDateTime(firstDay), weekday, self._weekstart)
				self._paintDay(drawer, theDay, x + weekday * 1.0 * width / 7, y, 1.0 * width / 7, height)

			return max(WEEK_SIZE_MIN.width, width), max(WEEK_SIZE_MIN.height, height)
		else:
			w, h = self._paintPeriod(drawer, firstDay, 7, x, y, width, height)

			minWidth += w
			minHeight += h

			return max(WEEK_SIZE_MIN.width, minWidth), minHeight

	def _paintMonthly( self, drawer, day, x, y, width, height):
		"""
		Draw month's calendar using calendar module functions
		"""

		w, h = drawer.DrawMonthHeader(day, x, y, width, height)
		y += h
		height -= h

		if self._style == wxSCHEDULER_VERTICAL:
			month = calendar.monthcalendar( day.GetYear(), day.GetMonth() + 1 )

			for w, monthWeek in enumerate( month ):
				for d, monthDay in enumerate( monthWeek ):
					cellW, cellH = 1.0 * width / 7, 1.0 * height / len(month)

					if monthDay == 0:
						theDay = None
						schedules = []
					else:
						theDay = day
						theDay.SetDay(monthDay)
						theDay.SetHour(0)
						theDay.SetMinute(0)
						theDay.SetSecond(0)

						end = utils.copyDateTime(theDay)
						end.AddDS(wx.DateSpan(days=1))

						schedules = self._getSchedInPeriod(self._schedules, theDay, end)

						self._datetimeCoords.append((utils.copyDateTime(theDay),
									     wx.Point(d * cellW, w * cellH),
									     wx.Point(d * cellW + cellW, w * cellH + cellH)))

					self._schedulesCoords.extend(drawer.DrawSchedulesCompact(theDay, schedules, d * cellW, w * cellH, cellW, cellH))

			return (max(MONTH_CELL_SIZE_MIN.width * 7, width),
				max(MONTH_CELL_SIZE_MIN.height * (w + 1), height))
		else:
			day.SetDay(1)
			day.SetHour(0)
			day.SetMinute(0)
			day.SetSecond(0)

			minHeight = h

			end = utils.copyDateTime(day)
			end.AddDS(wx.DateSpan(months=1))

			daysCount = end.Subtract(day).GetDays()

			maxDY = 0
			for idx in xrange(daysCount):
				theDay = utils.copyDateTime(day)
				theDay.AddDS(wx.DateSpan(days=idx))
				w, h = drawer.DrawSimpleDayHeader(theDay, x + 1.0 * idx * width / daysCount,
								  y, 1.0 * width / daysCount, height,
								  theDay.IsSameDate(wx.DateTime.Now()))
				maxDY = max(maxDY, h)

			y += maxDY
			height -= maxDY
			minHeight += maxDY

			w, h = self._paintPeriod(drawer, day, end.Subtract(day).GetDays(), x, y, width, height)
			minHeight += h

			return w, minHeight

	def _processEvt( self, commandEvent, point ):
		""" 
		Process the command event passed at the given point
		"""
		evt = wx.PyCommandEvent( commandEvent )
		sch = self._findSchedule( point )
		if isinstance( sch, wxSchedule ):
			mySch = sch
			myDate = None
		else:
			mySch = None
			myDate = sch
		
		evt.schedule = mySch
		evt.date = myDate
		evt.SetEventObject( self )
		self.ProcessEvent( evt ) 

	def DoPaint(self, drawer, x, y, width, height):
		self._schedulesCoords = list()
		self._datetimeCoords = list()

		day = utils.copyDate(self.GetDate())

		if self._viewType == wxSCHEDULER_DAILY:
			return self._paintDaily(drawer, day, x, y, width, height)
		elif self._viewType == wxSCHEDULER_WEEKLY:
			return self._paintWeekly(drawer, day, x, y, width, height)
		elif self._viewType == wxSCHEDULER_MONTHLY:
			return self._paintMonthly(drawer, day, x, y, width, height)

	def GetViewSize(self):
		# Used by wxSchedulerReport

		size = self.GetSize()
		minSize = self.CalcMinSize()

		return wx.Size(max(size.width, minSize.width), max(size.height, minSize.height))

	def CalcMinSize(self):
		if self._viewType == wxSCHEDULER_DAILY:
			minW, minH = DAY_SIZE_MIN.width, DAY_SIZE_MIN.height
		elif self._viewType == wxSCHEDULER_WEEKLY:
			minW, minH = WEEK_SIZE_MIN.width, WEEK_SIZE_MIN.height
		elif self._viewType == wxSCHEDULER_MONTHLY:
			minW, minH = MONTH_CELL_SIZE_MIN.width * 7, 0 # will be computed

		if self._viewType == wxSCHEDULER_MONTHLY or self._style == wxSCHEDULER_HORIZONTAL:
			memDC = wx.MemoryDC()
			bmp = wx.EmptyBitmap(1, 1)
			memDC.SelectObject(bmp)
			try:
				if self._drawerClass.use_gc:
					context = wx.GraphicsContext.Create(memDC)
					context.SetFont(wx.NORMAL_FONT, wx.BLACK)
				else:
					context = memDC

				if isinstance(self, wx.ScrolledWindow):
					size = self.GetVirtualSize()
				else:
					size = self.GetSize()

				# Actually, only the min height may vary...
				_, minH = self.DoPaint(self._drawerClass(context, self._lstDisplayedHours),
						       0, 0, size.GetWidth(), 0)
			finally:
				memDC.SelectObject(wx.NullBitmap)

		return wx.Size(minW, minH)

	def OnPaint( self, evt = None ):
		# Do the draw

		if isinstance(self, wx.ScrolledWindow):
			size = self.GetVirtualSize()
		else:
			size = self.GetSize()

		if self._dc is None:
			if self._drawerClass.use_gc or not self._autoBufferedDC:
				dc = wx.PaintDC(self)
			else:
				dc = wx.AutoBufferedPaintDC(self)

			self.PrepareDC( dc )
		else:
			# We  can't assume that  the underlying  DC is
			# supported by  GraphicsContext, so draw first
			# into a bitmap

			bitmap = wx.EmptyBitmap(size.GetWidth(), size.GetHeight())
			dc = wx.MemoryDC()
			dc.SelectObject(bitmap)

		dc.BeginDrawing()

		try:
			dc.SetBackground( wx.Brush( SCHEDULER_BACKGROUND_BRUSH ) )
			dc.SetPen( FOREGROUND_PEN )
			dc.Clear()
			dc.SetFont(wx.NORMAL_FONT)

			if self._drawerClass.use_gc:
				context = wx.GraphicsContext.Create(dc)
				#scrollX, scrollY = self.CalcUnscrolledPosition(0, 0)
				#context.Translate(-scrollX, -scrollY)
			else:
				context = dc

			self.DoPaint(self._drawerClass(context, self._lstDisplayedHours), 0, 0, size.GetWidth(), size.GetHeight())

			if self._dc is not None:
				dc.SelectObject(wx.NullBitmap)
				self._dc.DrawBitmap(bitmap, 0, 0, True)
		finally:
			dc.EndDrawing()

	def SetResizable( self, value ):
		"""
		Draw proportionally of actual space but not down on minimun sizes
		The actual sze is retrieved by GetSize() method of derived object
		"""
		self._resizable = bool( value )

	def SetStyle(self, style):
		"""
		Sets  the drawing  style.  Values  for 'style'	may be
		wxSCHEDULER_VERTICAL	   (the	      default)	    or
		wxSCHEDULER_HORIZONTAL.
		"""
		self._style = style
		self.Refresh()

	def GetStyle( self ):
		"""
		Returns the current drawing style.
		"""
		return self._style

	def SetDrawer(self, drawerClass):
		"""
		Sets the drawer class.
		"""
		self._drawerClass = drawerClass
		self.Refresh()

	def GetDrawer(self):
		return self._drawerClass