#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wxSchedulerCore import *
import wx.lib.scrolledpanel as scrolled


class wxScheduler( wxSchedulerCore, scrolled.ScrolledPanel ):

	def __init__( self, *args, **kwds ):
		kwds[ "style" ] = wx.TAB_TRAVERSAL|wx.FULL_REPAINT_ON_RESIZE

		super( wxScheduler, self ).__init__( *args, **kwds )

		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_LEFT_DOWN, self.OnClick )
		self.Bind( wx.EVT_RIGHT_DOWN, self.OnRightClick )
		self.Bind( wx.EVT_LEFT_DCLICK, self.OnDClick )

		self.SetScrollRate(10, 10)

	# Events
	def OnClick( self, evt ):
		self._doClickControl( self._getEventCoordinates( evt ) )

	def OnRightClick( self, evt ):
		self._doRightClickControl( self._getEventCoordinates( evt ) )

	def OnDClick( self, evt ):
		self._doDClickControl( self._getEventCoordinates( evt ) )

	def Add( self, *args, **kwds ):
		wxSchedulerCore.Add( self, *args, **kwds )
		self._controlBindSchedules()
		
	def Refresh(self):
		super(wxScheduler, self).Refresh()
		self.GetSizer().FitInside(self)

	def SetResizable( self, value ):
		"""
		Call derived method and force wxDC refresh
		"""
		super(wxScheduler, self).SetResizable(value)
		self.Refresh()

		#self._calcScrollBar()
		
	def _controlBindSchedules( self ):
		"""
		Control if all the schedules into self._schedules
		have its EVT_SCHEDULE_CHANGE binded
		"""
		currentSc = set( self._schedules )
		bindSc = set( self._schBind )
		
		for sc in ( currentSc - bindSc ):
			sc.Bind( EVT_SCHEDULE_CHANGE, lambda x: wx.CallAfter( self.Refresh ) )
			self._schBind.append( sc )

	def _getEventCoordinates( self, event ):
		""" 
		Return the coordinates associated with the given mouse event.

		The coordinates have to be adjusted to allow for the current scroll
		position.
		"""
		originX, originY = self.GetViewStart()
		unitX, unitY = self.GetScrollPixelsPerUnit()
		
		coords = wx.Point( 
			event.GetX() + ( originX * unitX ),
			event.GetY() + ( originY * unitY ) 
				)
		
		return coords

	def SetViewType( self, view=None ):
		super(wxScheduler, self).SetViewType(view)
		self.Refresh()