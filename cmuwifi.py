""""
  __________    ___        ___   __          __
||__________|   ||\\      //||   ||          ||
||              || \\    // ||   ||          ||
||              ||  \\  //  ||   ||          ||
||              ||   \\//   ||   ||          ||
||              ||          ||   ||          ||
||              ||          ||   ||          ||
||              ||          ||   ||          ||
||__________    ||          ||   ||__________||
||__________|   ||          ||   \\__________//

                              ____
       \        /     o       |     o
        \  /\  /      |  --   |===  |
         \/  \/       |       |     |


              15-112 Term Project
                   Fall 2013
                Robert Maratos
            rmaratos@andrew.cmu.edu
"""

import wx
import cmu
import os


class Main(wx.Frame):
    """Main Frame containing everything"""
    def __init__(self,parent, title, campus):
        """Create the Main Frame"""
        size = (1000, 700)
        super(Main, self).__init__(parent, title=title, size=size)
        self.campus = campus
        self.view = 'campus'
        self.image = None
        self.InitUI()
        self.SetMenuBar(MyMenuBar())
        self.CreateStatusBar()
        self.Centre()
        self.Show()

    def InitUI(self):
        """Initialize the User Interface"""
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        bottomSizer = wx.BoxSizer(wx.HORIZONTAL) #sidebar and canvas
        self.toolbar = ToolBar(self)
        self.canvas = MyCanvas(self)
        self.sidebar = SideBar(self)
        mainSizer.Add(self.toolbar, 0, wx.EXPAND)
        bottomSizer.Add(self.sidebar, 0,wx.EXPAND)
        bottomSizer.Add(self.canvas, 1, wx.EXPAND)
        mainSizer.Add(bottomSizer, 1,wx.EXPAND)
        self.SetSizer(mainSizer)
        self.canvas.campusView()

    def itemChosen(self, item):
        """Redirect chosen item event."""
        self.selected = item
        if self.view == 'campus':
            self.buildingChosen()
        elif self.view == 'building':
            self.floorChosen()

    def selectFloorFromCanvas(self, floor):
        """Calls sidebar when floor is chosen on canvas."""
        self.sidebar.selectFloor(floor)

    def selectFloorFromSidebar(self, floor):
        """Calls canvas when floor is chosen from sidebar."""
        self.canvas.showFloor(floor)

    def unselectBuilding(self):
        """Unselects building."""
        self.sidebar.tree.UnselectAll()
        self.selected = None
        self.toolbar.campusView()

    def buildingChosen(self):
        """Ask to confirm chosen building."""
        self.toolbar.buildingChosen()

    def floorChosen(self):
        """Ask to confirm chosen floor"""
        self.toolbar.floorChosen()

    def confirmButton(self):
        """Redirect confirm button event."""
        if self.view == 'campus':
            self.buildingConfirmed()
        elif self.view == 'building':
            self.floorConfirmed()

    def backButton(self):
        """Redirect back button event."""
        if self.view == 'building':
            self.buildingUndo()
        elif self.view == 'floor':
            self.floorUndo()

    def buildingConfirmed(self):
        """Change modes once building is confirmed."""
        self.view = 'building'
        self.currentBuilding = self.selected
        self.toolbar.buildingConfirmed()
        self.sidebar.buildingView()
        self.canvas.buildingView()

    def floorConfirmed(self):
        """Change modes once floor is confirmed."""
        self.view = 'floor'
        floor = self.currentBuilding.getFloor(self.sidebar.selected)
        self.currentFloor = floor
        size = (700, 500)
        self.currentFloor.initEnvironment(size)
        self.toolbar.floorConfirmed()
        self.sidebar.floorView()
        self.canvas.floorView()

    def buildingUndo(self):
        """Undo building selection."""
        self.view = 'campus'
        self.sidebar.campusView()
        self.toolbar.campusView()
        self.canvas.buildingUndo()

    def floorUndo(self):
        """Undo floor selection."""
        self.view = 'building'
        self.sidebar.buildingView()
        self.toolbar.buildingConfirmed()
        self.canvas.enable = True
        self.canvas.buildingView()

    def scan(self):
        """Update sidebar wifi information."""
        self.sidebar.listDisplay()

class MyMenuBar(wx.MenuBar):
    """Menu Bar Setup"""
    def __init__(self):
        """Create Menu Bar"""
        wx.MenuBar.__init__(self)
        self.File()

    def File(self):
        """Initialize File Menu"""
        self.filemenu = wx.Menu()
        info = "Information about this program"
        self.menuAbout = self.filemenu.Append(wx.ID_ABOUT, "&About", info)
        self.filemenu.Append(wx.ID_COPY, "Copy")
        self.Append(self.filemenu, "File")
        self.Bind(wx.EVT_MENU, self.OnAbout, self.menuAbout)

    def OnAbout(self, e):
        """ About Dialog """
        description = "A Wi-Fi Strength Visualizer"
        about = "About CMUWifi"
        dlg = wx.MessageDialog(self, description, about, wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

class ToolBar(wx.Panel):
    """Toolbar containing user instruction and controls"""
    def __init__(self, parent):
        """Initialize ToolBar"""
        self.parent = parent
        size = (-1, 50) #fixed height
        wx.Panel.__init__(self, parent, size=size)
        color = (235, 235, 235) #grey
        self.SetBackgroundColour(color)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.makeConfirmButton()
        self.initToolBar()
        self.backButton = None
        if self.parent.view == 'scan':
            self.scanView()
        elif self.parent.view == 'campus':
            self.campusView()

    def initToolBar(self):
        """Initialize toolbar sizer."""
        textSizer = wx.BoxSizer(wx.HORIZONTAL)
        panel = wx.Panel(self)
        size = (300, -1) #fixed width
        label = ''
        style = wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.display = wx.StaticText(panel, -1, size=size,
                                                label=label,
                                                style=style)
        panelSizer.Add(self.display, wx.ALIGN_CENTER)
        panel.SetSizer(panelSizer)
        textSizer.Add(panel, -1,  wx.ALIGN_CENTER)
        self.mainSizer.Add(textSizer, -1, wx.ALIGN_CENTER|wx.EXPAND)
        self.mainSizer.Add(self.buttonSizer, -1, wx.ALIGN_CENTER)
        self.SetSizer(self.mainSizer)

    def campusView(self):
        """Campus mode."""
        label = "Where are you?"
        self.display.SetLabel(label)
        self.confirmButton.Disable()
        if self.backButton:
            self.backButton.Disable()

    def makeConfirmButton(self):
        """Create confirm button."""
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        style = wx.BU_EXACTFIT|wx.ALIGN_CENTER
        self.confirmButton = wx.Button(self, 1, 'Confirm', style=style)
        self.confirmButton.Bind(wx.EVT_BUTTON, self.confirmClick)
        self.confirmButton.Disable()
        self.buttonSizer.Add(self.confirmButton)

    def scanView(self):
        """Scan mode"""
        refresh = wx.Button(self, 0, 'Refresh')
        self.Bind(wx.EVT_BUTTON, self.refresh, id=0)
        undo = wx.Button(self, 1, 'Undo')
        self.Bind(wx.EVT_BUTTON, self.undo, id=1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(refresh)
        hbox.Add(undo)
        self.SetSizer(hbox)

    def buildingChosen(self):
        """Ask to confirm chosen building."""
        label = "Where are you?"
        building = self.parent.selected
        if building:
            label = "%s?" % building
            self.confirmButton.Enable()
        else:
            self.confirmButton.Disable()
        self.display.SetLabel(label)

    def buildingConfirmed(self):
        """Confirm building choice."""
        building = self.parent.currentBuilding
        label = "Which floor in %s?" % building
        self.currentBuilding = building
        self.display.SetLabel(label)
        self.confirmButton.Disable()
        self.makeBackButton()

    def makeBackButton(self):
        """Create back button."""
        if self.backButton:
            self.backButton.Enable()
            return
        style = wx.BU_EXACTFIT|wx.ALIGN_CENTER
        self.backButton = wx.Button(self, 1, 'Back', style = style)
        self.backButton.Bind(wx.EVT_BUTTON, self.backClick)
        self.buttonSizer.Insert(0, self.backButton)
        self.mainSizer.Layout()

    def floorChosen(self):
        """Confirm floor choice."""
        label = "Which floor in %s?" % self.currentBuilding
        floor = self.parent.selected
        if floor:
            label = "Floor %s?" % floor
            self.confirmButton.Enable()
        else:
            self.confirmButton.Disable()
        self.display.SetLabel(label)

    def floorConfirmed(self):
        """Proceed once floor confirmed."""
        floor = self.parent.currentFloor
        label = "Floor %s" % floor
        label = 'Click to scan'
        self.display.SetLabel(label)
        self.confirmButton.Disable()
        self.backButton.Enable()

    def confirmClick(self, event):
        """Confirm button clicked."""
        self.parent.confirmButton()

    def backClick(self, event):
        """Back button clicked."""
        self.parent.backButton()

    def undo(self, event):
        """Send undo message to parent."""
        self.parent.undo()

class SideBar(wx.Panel):
    """Sidebar containing location options or Wi-Fi info"""
    def __init__(self, parent):
        """ Initialize Sidebar """
        size = (300, -1) #fixed width
        wx.Panel.__init__(self, parent, size=size)
        self.parent = parent
        self.SetDoubleBuffered(True)
        self.list = None
        self.mode = None
        self.initList()
        self.initTree()
        self.treeView()
        self.campusView()

    def initTree(self):
        """Initialize tree."""
        if self.mode == 'tree':
            return
        self.treeSizer = wx.BoxSizer(wx.VERTICAL)
        treeId=wx.NewId()
        size = (-1, -1)
        options = wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS|wx.TR_FULL_ROW_HIGHLIGHT
        self.tree = wx.TreeCtrl(self, treeId, wx.DefaultPosition,
                                size, options)
        color = (220,220,220) #greyish
        self.tree.SetBackgroundColour(color)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)
        self.treeSizer.Add(self.tree, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(self.treeSizer)
        self.mode = 'tree'

    def treeView(self):
        """Switch to tree view."""
        if self.list:
            self.list.Hide()
            self.tree.Show()
        self.initTree()

    def listView(self):
        """Switch to list view."""
        if self.tree:
            self.tree.Hide()
            self.list.Show()
        self.initList()

    def initList(self):
        """Initialize list."""
        if self.mode == 'list':
            return
        self.listSizer = wx.BoxSizer(wx.VERTICAL)
        listId =wx.NewId()
        style = wx.LC_REPORT|wx.SUNKEN_BORDER
        size = (300, 625) #fixed height
        self.list = wx.ListCtrl(self,listId,style=style, size = size)
        self.list.Show(True)
        self.defaultHeaders = ['Router', 'Channel', 'Max Location', 'Max SNR']
        for header in enumerate(self.defaultHeaders):
            self.list.InsertColumn(header[0], header[1])
        self.listSizer.Add(self.list, 1, wx.EXPAND | wx.SOUTH)
        self.SetSizer(self.listSizer)
        self.mode == 'list'

    def listDisplay(self):
        """Display information on list."""
        self.list.DeleteAllItems()
        self.environment = self.parent.canvas.currentFloor.environment
        networks = self.environment.networks
        cols = self.list.GetColumnCount()
        #delete old locations
        for i in xrange(cols - 1, len(self.defaultHeaders)-1,-1):
            self.list.DeleteColumn(i)
        locations = self.environment.locations
        columns = {}
        start = len(self.defaultHeaders)
        #add new locations
        for location in enumerate(locations):
            self.list.InsertColumn(start+location[0], str(location[1]))
            columns[location[1]] = (start+location[0])
        network = networks['CMU-SECURE'] #cmu-secure only
        routers = network.routers
        self.wifiInfo(routers, locations, columns)
        self.list.SetColumnWidth(0, -1) #resize columns
        self.list.SetColumnWidth(1, -1)

    def wifiInfo(self, routers, locations, columns):
        """Add wifi information to list."""
        for router in routers:
            router = routers[router]
            scans = router.scans
            pos = self.list.InsertStringItem(0, router.mac)
            self.list.SetStringItem(pos, 1, str(router.channel))
            self.list.SetStringItem(pos, 2, str(router.maxLocation))
            self.list.SetStringItem(pos, 3, str(router.maxSNR))
            for location in locations:
                scan = scans.get(location, "")
                col = columns[location]
                if scan:
                    strength = scan.snr
                    self.list.SetStringItem(pos, col, str(strength))

    def campusView(self):
        """ Campus mode """
        self.treeView()
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot('Campus')
        acad = self.tree.AppendItem(self.root, "Academic Buildings")
        resid = self.tree.AppendItem(self.root, "Residential Buildings")
        acadBuilds = sorted(self.parent.campus.academicBuildings.keys())
        self.buildingIDs = {}
        for building in acadBuilds:
            buildingID = self.tree.AppendItem(acad, building)
            self.buildingIDs[building] = buildingID
        residBuilds = sorted(self.parent.campus.residentialBuildings.keys())
        for building in residBuilds:
            buildingID = self.tree.AppendItem(resid, building)
            self.buildingIDs[building] = buildingID
        self.tree.ExpandAll()

    def buildingView(self):
        """Building mode."""
        self.treeView()
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot('Campus')
        building = self.parent.currentBuilding
        floors = self.tree.AppendItem(self.root, building.name)
        self.floorIDs = []
        for floor in building.floorNames:
            floorID = self.tree.AppendItem(floors, floor)
            self.floorIDs.append(floorID)
        self.tree.ExpandAll()

    def selectFloor(self, floor):
        """Select floor in tree."""
        self.tree.SelectItem(self.floorIDs[floor])

    def selectBuilding(self, building):
        """Select building in tree."""
        self.tree.SelectItem(self.buildingIDs[str(building)])

    def getFloor(self, floorID):
        """Get floor from floorID."""
        return self.floorIDs.index(floorID)

    def floorView(self):
        """Floor mode."""
        self.listView()

    def getBuilding(self, buildingID):
        """Return building from buildingID."""
        for building in self.buildingIDs:
            if self.buildingIDs[building] == buildingID:
                return building

    def OnSelChanged(self, event):
        """New item selected in tree."""
        item = event.GetItem()
        if self.tree.ItemHasChildren(item):
            self.tree.UnselectAll()
            self.selected = None
        else:
            self.selected = self.tree.GetItemText(item)
            if self.parent.view == 'campus':
                self.selected = self.parent.campus.getBuilding(self.selected)
                building = self.getBuilding(item)
            if self.parent.view == 'building':
                self.parent.selectFloorFromSidebar(self.getFloor(item))
        self.parent.itemChosen(self.selected)

class MyCanvas(wx.Window):
    """Canvas containing visual components."""
    def __init__(self, parent):
        """Initialize canvas."""
        self.parent = parent
        wx.Window.__init__(self, parent, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour('WHITE')
        self.pen = wx.Pen(wx.BLACK, 5)
        self.initBuffer()
        self.initColors()
        self.first = True
        self.initBindings()
        self.selected = None
        self.chosen = None
        self.enable = True

    def initColors(self):
        """Initialize color list."""
        self.colors = []
        r = 0
        for g in xrange(0, 255): #blue to green
            b = 255 - g
            self.colors.append((r, g, b))
        b = 0
        for r in xrange(0,255): #green to red
            g = 255 - r
            self.colors.append((r, g, b))

    def initBindings(self):
        """Initialize event bindings."""
        wx.EVT_LEFT_DOWN(self, self.OnButtonClick) #mouse event
        wx.EVT_MOTION(self, self.OnMotion)
        wx.EVT_PAINT(self, self.OnPaint) #refresh event
        wx.EVT_SIZE(self, self.OnSize) #window resize, manages buffer
        wx.EVT_IDLE(self, self.OnIdle) #idle event, manages buffer
        wx.EVT_PAINT(self, self.OnPaint) #refresh event
        wx.EVT_KEY_DOWN(self, self.OnKey)

    def OnKey(self, event):
        """On key press."""
        pass

    def highlightBuilding(self, buildingName):
        """Highlight building from buildingName."""
        building = self.parent.campus.getBuilding(buildingName)
        dc = self.getdc()
        self.campusView()
        self.drawMarker(dc, building.location)

    def initBuffer(self):
        """Initialize the bitmap used for buffering the display."""
        size = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(size.width, size.height)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        self.size = dc.Size
        self.showImage(self.parent.campus.map)
        self.reInitBuffer = False

    def OnSize(self, event):
        """On size event."""
        self.reInitBuffer = True

    def OnPaint(self, event=None):
        """On paint event."""
        dc = wx.BufferedPaintDC(self, self.buffer)

    def OnIdle(self, event):
        """On idle event."""
        if self.reInitBuffer:
            self.initBuffer()
            self.Refresh(False)

    def showImage(self, image):
        """Display image on canvas."""
        dc = self.getdc()
        dc.Clear()
        start = (0, 0)
        size = dc.Size
        self.drawImage(dc, image, start, size)

    def drawImage(self, dc, image, start, size):
        """Draw image with start location and size."""
        width, height = size
        ratio = 1.0*width/height
        imageWidth, imageHeight = image.GetWidth(), image.GetHeight()
        imageRatio = 1.0*imageWidth/imageHeight
        if imageRatio > ratio: #too wide
            scale = 1.0*width/imageWidth
        else: #too tall
            scale = 1.0*height/imageHeight
        w, h = imageWidth*scale, imageHeight*scale
        image.SetWidth(w)
        image.SetHeight(h)
        x, y = start
        dc.DrawBitmap(image, x, y, True)

    def campusView(self):
        """Display campus map."""
        image = self.parent.campus.map
        self.showImage(image)

    def buildingView(self):
        """Display floors in building."""
        building = self.parent.currentBuilding
        images = building.getFloorImages()
        self.chosen = None
        self.images = images
        dc = self.getdc()
        dc.Clear()
        width, height = dc.Size
        scale = 0.75 #amount of overlap
        self.dx = (1-scale)*width/len(images)
        self.dy = (1-scale)*height/len(images)
        self.size = width*scale, height*scale
        self.buildingCoordsDict = {}
        for i in xrange(len(images)):
            self.drawBuilding(dc, i)
        self.buildingCoords = self.buildingCoordsDict.keys()

    def drawBuilding(self, dc, index):
        """Draw building at index."""
        image = self.images[index]
        point = index*self.dx, index*self.dy
        x0, y0 = point
        x1, y1 = x0 + self.size[0], y0 + self.size[1]
        self.buildingCoordsDict[(int(x0),int(y0),int(x1),int(y1))] = index
        dc.DrawRectanglePointSize(point, self.size)
        self.drawImage(dc, image, point, self.size)

    def floorView(self):
        """Display floorplan and heatmap if there is one."""
        self.currentFloor = self.parent.currentFloor
        image = self.currentFloor.getImage()
        self.showImage(image)
        if self.currentFloor.environment.heatmap:
            self.drawHeatmap(self.getdc())
            self.drawLabel(self.getdc())

    def OnButtonClick(self, event):
        """On button click event."""
        point = event.GetPositionTuple()
        if self.parent.view == 'campus':
            if self.selected:
                if self.onMarker(point):
                    self.chosen = self.selected
                    self.parent.itemChosen(self.selected)
                    dc = self.getdc()
                else:
                    self.selected = self.chosen = None
                    self.parent.unselectBuilding()
                    self.campusView()
        if self.parent.view == 'building':
            self.parent.floorConfirmed()
        elif self.parent.view == 'floor':
            self.scan(point)

    def onMarker(self, point):
        """Check if point is on marker."""
        if self.parent.campus.closestBuilding(point, 15) == self.selected:
            return True
        return False

    def scan(self, point):
        """Perform scan at point."""
        self.currentFloor.environment.scan(point)
        self.currentFloor.saveEnvironment()
        self.floorView()
        self.parent.scan()

    def rgbString(self, rgb):
        """Get rgb string from rgb tuple."""
        red, green, blue = rgb
        return "#%02x%02x%02x" % (red, green, blue)

    def mapColor(self, val, low, high):
        """Get color given value and bounds."""
        if abs(high-low)<0.25:
            mid = len(self.colors)/2
            return self.colors[mid]
        index = int(round((val-low)*(len(self.colors)-1)/(high-low)))
        return self.colors[index]

    def drawHeatmap(self, dc):
        """Draw heatmap on dc."""
        heatmap = self.currentFloor.environment.heatmap
        hmap = self.currentFloor.environment.hmap
        if hmap == None:
            return
        low, high = heatmap.low, heatmap.high
        rows, cols = len(hmap), len(hmap[0])
        for row in xrange(rows-1):
            for col in xrange(cols-1):
                location = (row*10, col*10)
                val0 = hmap[row][col]
                r0,g0,b0 = self.mapColor(val0, low, high)
                colour0 = wx.Colour(r0,g0,b0,128)
                val1 = hmap[row+1][col+1]
                r1,g1,b1 = self.mapColor(val1, low, high)
                colour1 = wx.Colour(r1, g1, b1, 128)
                dimensions = (row*10, col*10, 10, 10)
                dc.GradientFillLinear(dimensions, colour0, colour1, 3)

    def drawLabel(self, dc):
        """Draw key at bottom right of dc."""
        divide = 5
        length = len(self.colors)/divide
        width, height = dc.Size
        margin = 10
        labelHeight = 30
        x0 = width - length - margin
        y0 = height - labelHeight
        heatmap = self.currentFloor.environment.heatmap
        low, high = round(heatmap.low, 2), round(heatmap.high, 2)
        dc.DrawText('SNR', x0 + 3.5*margin, height-3*labelHeight)
        dc.DrawText(str(low), x0, height - 2* labelHeight)
        dc.DrawText(str(high), width - 4*margin, height - 2*labelHeight)
        for i in xrange(length):
            r, g, b = self.colors[i*divide]
            penclr   = wx.Colour(r, g, b)
            dc.SetPen(wx.Pen(penclr, 1))
            dc.DrawLine(x0 + i, y0, x0 + i, height)

    def OnMotion(self, event):
        """On motion event."""
        if not self.chosen:
            point = event.GetPositionTuple()
            if self.parent.view == 'campus':
                self.selectBuilding(point)
            if self.parent.view == 'building':
                self.selectFloor(point)

    def selectBuilding(self, point):
        """Chose building at point."""
        closest = self.parent.campus.closestBuilding(point, 15)
        dc = self.getdc()
        if closest:
            if closest != self.selected:
                self.selected = closest
                self.drawMarker(dc, closest.location)
        elif self.selected:
            self.campusView()
            self.selected = None
        else:
            self.selected = None

    def inRect(self, point, coords):
        """Check if in rectangle."""
        x0, y0, x1, y1 = coords
        x, y = point
        if x0 < x < x1 and y0 < y < y1:
            return True
        return False

    def selectFloor(self, point):
        """Choose floor at point."""
        if not self.enable:
            return
        for i, coords in enumerate(self.buildingCoords):
            if self.inRect(point, coords):
                self.buildingCoords = [self.buildingCoords[i]] + \
                                        self.buildingCoords[:i] + \
                                        self.buildingCoords[i+1:]
                index = self.buildingCoordsDict[coords]
                self.parent.selectFloorFromCanvas(index)
                self.drawBuilding(self.getdc(), index)
                break

    def showFloor(self, i):
        """Show floor at index."""
        self.buildingCoords = [self.buildingCoords[i]] + \
                                self.buildingCoords[:i] + \
                                self.buildingCoords[i+1:]
        self.drawBuilding(self.getdc(), i)

    def buildingUndo(self):
        """Undo building choice."""
        self.campusView()
        self.chosen = None

    def drawMarker(self, dc, point):
        """Draw marker at point."""
        brushclr = wx.Colour(0, 255, 0, 128)   # half transparent
        penclr   = wx.Colour(255, 255, 255, 0)
        dc.SetBrush(wx.Brush(brushclr))
        dc.SetPen(wx.Pen(penclr, 10))
        dc.DrawCirclePoint(point, 15)

    def drawPoint(self, dc, point):
        """Draw point at point."""
        dc.BeginDrawing()
        x, y = point
        dc.DrawPoint(x,y)
        dc.EndDrawing()

    def getdc(self):
        """Get buffered dc."""
        return wx.BufferedDC(wx.ClientDC(self), self.buffer)

if __name__ == '__main__':
    app = wx.App(False)
    campus = cmu.CMU()
    Main(None, title='CMUWifi', campus = campus)
    app.MainLoop()
