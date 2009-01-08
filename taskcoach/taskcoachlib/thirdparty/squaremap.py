#! /usr/bin/env python
import wx, sys, os
import  wx
import  wx.lib.newevent

SquareHighlightEvent, EVT_SQUARE_HIGHLIGHTED = wx.lib.newevent.NewEvent()
SquareSelectionEvent, EVT_SQUARE_SELECTED = wx.lib.newevent.NewEvent()

class SquareMap( wx.Panel ):
    """Construct a nested-box trees structure view"""
    highlighted = None
    selected = None
    
    BackgroundColor = wx.Color( 128,128,128 )
    
    def __init__( 
        self,  parent=None, id=-1, pos=wx.DefaultPosition, 
        size=wx.DefaultSize, style=wx.TAB_TRAVERSAL|wx.NO_BORDER|wx.FULL_REPAINT_ON_RESIZE, 
        name='SquareMap', model = None,
        adapter = None,
        padding = 2, # amount to reduce the children's box from the parent's box
    ):
        super( SquareMap, self ).__init__(
            parent, id, pos, size, style, name
        )
        self.model = model
        self.padding = padding
        self.Bind( wx.EVT_PAINT, self.OnDraw )
        self.Bind( wx.EVT_MOTION, self.OnMouse )
        self.hot_map = []
        self.adapter = adapter or DefaultAdapter()
#		self.Bind( wx.EVT_SIZE, self.OnResize )

    def OnMouse( self, event ):
        """Handle mouse-move event by selecting a given element"""
        node = self.NodeFromPosition( event.GetPosition() )
        self.SetHighlight( node, event.GetPosition() )
    
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
        
    def SetSelected( self, node, point=None ):
        """Set the given node selected in the square-map"""
        previous = self.selected
        self.selected = node 
        if node != previous:
            self.Refresh()
        if node:
            wx.PostEvent( self, SquareSelectionEvent( node=node, point=point, map=self ) )
    def SetHighlight( self, node, point=None ):
        """Set the currently-highlighted node"""
        previous = self.highlighted
        self.highlighted = node 
        if node != previous:
            self.Refresh()
        if node:
            wx.PostEvent( self, SquareHighlightEvent( node=node, point=point, map=self ) )
    def SetModel( self, model ):
        """Set our model object (root of the tree)"""
        self.model = model
        self.Refresh()
    
    def OnDraw( self, event ):
        """Event handler to draw our node-map into the device context"""
        dc = wx.PaintDC( self )
        if self.model:
            self.hot_map = []
            # draw the root box...
            brush = wx.Brush( self.BackgroundColor  )
            dc.SetBackground( brush )
            dc.Clear()
            dc.SetFont(wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT))
            w, h = dc.GetSize()
            self.DrawBox( dc, self.model, 0,0,w,h, hot_map = self.hot_map )
    
    def DrawBox( self, dc, node, x,y,w,h, hot_map, depth=0 ):
        """Draw a model-node's box and all children nodes"""
        if node is self.highlighted:
            color = wx.Color( (depth * 5)%255, (255-(depth * 5))%255, 0 )
        else:
            color = wx.Color( (depth * 10)%255, (255-(depth * 10))%255, 255 )
        brush = wx.Brush( color  )
        dc.SetBrush( brush )
        dc.DrawRectangle( x,y,w,h )
        brush = wx.Brush(self.BackgroundColor)
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
            oldh = h
            h = h * (1.0-empty)
            y -= h - oldh 
        
        if w >1 and h> 1:
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
