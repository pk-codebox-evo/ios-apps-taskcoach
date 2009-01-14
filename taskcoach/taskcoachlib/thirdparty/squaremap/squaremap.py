#! /usr/bin/env python
import wx, sys, os
import wx.lib.newevent

SquareHighlightEvent, EVT_SQUARE_HIGHLIGHTED = wx.lib.newevent.NewEvent()
SquareSelectionEvent, EVT_SQUARE_SELECTED = wx.lib.newevent.NewEvent()
SquareActivationEvent, EVT_SQUARE_ACTIVATED = wx.lib.newevent.NewEvent()

class SquareMap( wx.Panel ):
    """Construct a nested-box trees structure view"""
    highlighted = None
    selected = None
    
    BackgroundColor = wx.Color( 128,128,128 )
    
    def __init__( 
        self,  parent=None, id=-1, pos=wx.DefaultPosition, 
        size=wx.DefaultSize, 
        style=wx.TAB_TRAVERSAL|wx.NO_BORDER|wx.FULL_REPAINT_ON_RESIZE, 
        name='SquareMap', model = None,
        adapter = None,
        labels = True, # set to True to draw textual labels within the boxes
        highlight = True, # set to False to turn of highlighting
        padding = 2, # amount to reduce the children's box from the parent's box
    ):
        super( SquareMap, self ).__init__(
            parent, id, pos, size, style, name
        )
        self.model = model
        self.padding = padding
        self.labels = labels
        self.highlight = highlight
        self.selected = None
        self.Bind( wx.EVT_PAINT, self.OnPaint)
        self.Bind( wx.EVT_SIZE, self.OnSize )
        if highlight:
            self.Bind( wx.EVT_MOTION, self.OnMouse )
        self.Bind( wx.EVT_LEFT_UP, self.OnClickRelease )
        self.Bind( wx.EVT_LEFT_DCLICK, self.OnDoubleClick )
        self.Bind( wx.EVT_KEY_UP, self.OnKeyUp )
        self.hot_map = []
        self.adapter = adapter or DefaultAdapter()
        self.DEFAULT_PEN = wx.Pen( wx.BLACK, 1, wx.SOLID )
        self.SELECTED_PEN = wx.Pen( wx.WHITE, 2, wx.SOLID )
        self.OnSize(None)
        
    def OnMouse( self, event ):
        """Handle mouse-move event by selecting a given element"""
        node = self.NodeFromPosition( event.GetPosition() )
        self.SetHighlight( node, event.GetPosition() )

    def OnClickRelease( self, event ):
        """Release over a given square in the map"""
        node = self.NodeFromPosition( event.GetPosition() )
        self.SetSelected( node, event.GetPosition() )
        
    def OnDoubleClick(self, event):
        """Double click on a given square in the map"""
        node = self.NodeFromPosition(event.GetPosition())
        if node:
            wx.PostEvent( self, SquareActivationEvent( node=node, point=event.GetPosition(), map=self ) )
    
    def OnKeyUp(self, event):
        event.Skip()
        if not self.selected or not self.hot_map:
            return
        
        index, hot_map = self.FindSelectedHotmap(self.hot_map)
        if event.KeyCode == wx.WXK_HOME:
            self.SetSelected(self.hot_map[0][1])
        elif event.KeyCode == wx.WXK_END:
            self.SetSelected(self.lastChild(self.hot_map))
        elif event.KeyCode == wx.WXK_RIGHT:
            self.SetSelected(self.firstChild(hot_map))
        elif event.KeyCode == wx.WXK_DOWN:
            self.SetSelected(self.nextChild(hot_map, index))
        elif event.KeyCode == wx.WXK_UP:
            self.SetSelected(self.previousChild(hot_map, index))
        elif event.KeyCode == wx.WXK_LEFT:
            parent = self.parent(self.hot_map, self.selected)
            if parent:
                self.SetSelected(parent)
        elif event.KeyCode == wx.WXK_RETURN:
            wx.PostEvent(self, SquareActivationEvent(node=self.selected,
                                                     map=self))
            
    def FindSelectedHotmap(self, hot_map):
        if not hot_map:
            return None
        for index, (rect, node, children) in enumerate(hot_map):
            if node == self.selected:
                return index, hot_map
            else:
                result = self.FindSelectedHotmap(children)
                if result:
                    return result
                else:
                    continue
        return None
            
    def lastChild(self, hot_map):
        children = hot_map[-1][2]
        if children:
            return self.lastChild(children)
        else:
            return hot_map[-1][1]
        
    def firstChild(self, hot_map):
        children = hot_map[0][2]
        if children:
            return children[0][1]
        else:
            return hot_map[0][1] # Unchanged
        
    def nextChild(self, hotmap, index):
        if index >= len(hotmap) - 1:
            return hotmap[-1][1] # Already at last node
        else:
            return hotmap[index+1][1]
    
    def previousChild(self, hotmap, index):
        if index <= 0:
            return hotmap[0][1] # Already at first node
        else:
            return hotmap[index-1][1]
        
    def parent(self, hotmap, node):
        for rect, parent, children in hotmap:
            for rect, child, grandchildren in children:
                if child == node:
                    return parent
            result = self.parent(children, node)
            if result:
                return result
            else:
                continue
        return None
        
    def NodeFromPosition( self, position, hot_map=None ):
        """Retrieve the node at the given position"""
        if hot_map is None:
            hot_map = self.hot_map
        for rect,node,children in hot_map:
            if rect.Contains( position ):
                child = self.NodeFromPosition( position, children )
                if child:
                    return child 
                return node
        return None

    def GetSelected(self):
        return self.selected
            
    def SetSelected( self, node, point=None, propagate=True ):
        """Set the given node selected in the square-map"""
        previous = self.selected
        self.selected = node 
        if node != previous:
            self.Refresh()
        if node:
            wx.PostEvent( self, SquareSelectionEvent( node=node, point=point, map=self ) )

    def SetHighlight( self, node, point=None, propagate=True ):
        """Set the currently-highlighted node"""
        previous = self.highlighted
        self.highlighted = node 
        if node != previous:
            self.Refresh()
        if node and propagate:
            wx.PostEvent( self, SquareHighlightEvent( node=node, point=point, map=self ) )

    def SetModel( self, model, adapter=None ):
        """Set our model object (root of the tree)"""
        self.model = model
        if adapter is not None:
            self.adapter = adapter
        self.Refresh()
        
    def Refresh(self):
        self.UpdateDrawing()
    
    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self._Buffer)

    def OnSize(self, event):
        # The Buffer is initialized in OnSize, so that the buffer is always
        # the same size as the Window.
        self.Width, self.Height = self.GetClientSizeTuple()
        # Make new off screen bitmap: this bitmap will always have the
        # current drawing in it, so it can be used to save the image to
        # a file, or whatever.
        self._Buffer = wx.EmptyBitmap(self.Width, self.Height)
        self.UpdateDrawing()

    def UpdateDrawing(self):
        dc = wx.BufferedDC(wx.ClientDC(self), self._Buffer)
        self.Draw(dc)
        
    def Draw(self, dc):
        if self.model:
            self.hot_map = []
            dc.BeginDrawing()
            brush = wx.Brush( self.BackgroundColor  )
            dc.SetBackground( brush )
            dc.Clear()
            dc.SetFont(wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT))
            w, h = dc.GetSize()
            self.DrawBox( dc, self.model, 0,0,w,h, hot_map = self.hot_map )
            dc.EndDrawing()
   
    def BrushForNode( self, node, depth=0 ):
        """Create brush to use to display the given node"""
        if node is self.selected:
            color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        elif node is self.highlighted:
            color = wx.Color( red=0, green=255, blue=0 )
        else:
            color = self.adapter.background_color(node, depth)
            if not color:
                red = (depth * 10)%255
                green = 255-((depth * 10)%255)
                blue = 200
                color = wx.Color( red, green, blue )
        return wx.Brush( color  )
    
    def PenForNode( self, node, depth=0 ):
        """Determine the pen to use to display the given node"""
        if node is self.selected:
            return self.SELECTED_PEN
        return self.DEFAULT_PEN

    def TextForegroundForNode(self, node, depth=0):
        """Determine the text foreground color to use to display the label of
           the given node"""
        if node is self.selected:
	    fg_color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
        else:
            fg_color = self.adapter.foreground_color(node, depth)
            if not fg_color:
	        fg_color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOWTEXT)
        return fg_color
    
    def DrawBox( self, dc, node, x,y,w,h, hot_map, depth=0 ):
        """Draw a model-node's box and all children nodes"""
        dc.SetBrush( self.BrushForNode( node, depth ) )
        dc.SetPen( self.PenForNode( node, depth ) )
        dc.DrawRoundedRectangle( x,y,w,h, self.padding *3 )
        if self.labels:
            # TODO: only draw if we have enough room (otherwise turns into 
            # a huge mess if you have lots of heavily nested boxes.
            dc.SetTextForeground(self.TextForegroundForNode(node, depth))
            dc.DrawText(self.adapter.label(node), x+2, y)
        children_hot_map = []
        hot_map.append( (wx.Rect( int(x),int(y),int(w),int(h)), node, children_hot_map ) )
        x += self.padding
        y += self.padding
        w -= self.padding*2
        h -= self.padding*2
        
        empty = self.adapter.empty( node )
        if empty:
            # is a fraction of the space which is empty...
            new_h = h * (1.0-empty)
            y += (h-new_h)
            h = new_h
        
        if w >self.padding*2 and h> self.padding*2:
            children = self.adapter.children( node )
            if children:
                self.LayoutChildren( dc, children, node, x,y,w,h, children_hot_map, depth+1 )

    def LayoutChildren( self, dc, children, parent, x,y,w,h, hot_map, depth=0 ):
        """Layout the set of children in the given rectangle"""
        nodes = [ (self.adapter.value(node,parent),node) for node in children ]
        nodes.sort()
        total = self.adapter.children_sum( children,parent )
        if total:
            (firstSize,firstNode) = nodes[-1]
            rest = [node for (size,node) in nodes[:-1]]
            fraction = firstSize/float(total)
            if w >= h:
                new_w = int(w*fraction)
                if new_w:
                    self.DrawBox( dc, firstNode, x,y, new_w, h, hot_map, depth+1 )
                w = w-new_w
                x += new_w 
            else:
                new_h = int(h*fraction)
                if new_h:
                    self.DrawBox( dc, firstNode, x,y, w, new_h, hot_map, depth + 1 )
                h = h-new_h
                y += new_h 
            if rest:
                self.LayoutChildren( dc, rest, parent, x,y,w,h, hot_map, depth )

class DefaultAdapter( object ):
    """Default adapter class for adapting node-trees to SquareMap API"""
    def children( self, node ):
        """Retrieve the set of nodes which are children of this node"""
        return node.children
    def value( self, node, parent=None ):
        """Return value used to compare size of this node"""
        return node.size
    def label( self, node ):
        """Return textual description of this node"""
        return node.path
    def overall( self, node ):
        """Calculate overall size of the node including children and empty space"""
        return sum( [self.value(value,node) for value in self.children(node)] )
    def children_sum( self, children,node ):
        """Calculate children's total sum"""
        return sum( [self.value(value,node) for value in children] )
    def empty( self, node ):
        """Calculate empty space as a fraction of total space"""
        overall = self.overall( node )
        if overall:
            return (overall - self.children_sum( self.children(node), node))/float(overall)
        return 0
    def background_color(self, node, depth):
        return None
    def foreground_color(self, node, depth):
        return None


class TestApp(wx.App):
    """Basic application for holding the viewing Frame"""
    def OnInit(self):
        """Initialise the application"""
        wx.InitAllImageHandlers()
        self.frame = frame = wx.Frame( None,
        )
        frame.CreateStatusBar()
        
        model = model = self.get_model( sys.argv[1]) 
        self.sq = SquareMap( frame, model=model)
        EVT_SQUARE_HIGHLIGHTED( self.sq, self.OnSquareSelected )
        frame.Show(True)
        self.SetTopWindow(frame)
        return True
    def get_model( self, path ):
        nodes = []
        for f in os.listdir( path ):
            full = os.path.join( path,f )
            if not os.path.islink( full ):
                if os.path.isfile( full ):
                    nodes.append( Node( full, os.stat( full ).st_size, () ) )
                elif os.path.isdir( full ):
                    nodes.append( self.get_model( full ))
        return Node( path, sum([x.size for x in nodes]), nodes )
    def OnSquareSelected( self, event ):
        self.frame.SetStatusText( self.sq.adapter.label( event.node ) )

class Node( object ):
    """Really dumb file-system node object"""
    def __init__( self, path, size, children ):
        self.path = path
        self.size = size
        self.children = children 
    def __repr__( self ):
        return '%s( %r, %r, %r )'%( self.__class__.__name__, self.path, self.size, self.children )
        

usage = 'squaremap.py somedirectory'
        
def main():
    """Mainloop for the application"""
    if not sys.argv[1:]:
        print usage
    else:
        app = TestApp(0)
        app.MainLoop()

if __name__ == "__main__":
    main()
