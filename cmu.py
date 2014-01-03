import os
import wx
import wifi
import pickle

class CMU(object):
    """Object representation of the CMU campus."""
    def __init__(self):
        """Initialize buildings."""
        self.path = 'media/CMU'
        self.mapPath = self.path + '/' + 'map.png'
        self.noImage = 'media/noImage.jpg'
        self.initBuildingNames()
        self.initBuildingLocations()
        self.academicBuildings = {}
        self.residentialBuildings = {}
        self.initBuildings()
        self.initMap()

    def initMap(self):
        """Initialize campus map."""
        self.map = wx.EmptyBitmap(1, 1)
        if os.path.exists(self.mapPath):
            self.map.LoadFile(self.mapPath, wx.BITMAP_TYPE_ANY)
        else:
            self.map.LoadFile(self.noImage, wx.BITMAP_TYPE_ANY)

    def initBuildingNames(self):
        """Initialize building names."""
        self.initAcademicBuildings()
        self.initResidentialBuildings()

    def initBuildingLocations(self):
        """Initialize building locations."""
        self.initAcademicLocations()
        self.initResidentialLocations()

    def initAcademicBuildings(self):
        """Academic building names and floors."""
        self.academicBuildingNames = {
        "Baker - Porter Hall": "CBA1234",
        "College of Fine Arts": "A1M234",
        "Cyert Hall": "BA12",
        "Doherty Hall": "FEDCBA1234",
        "Gates and Hillman Centers": "123456789",
        "Hamburg Hall": "A123",
        "Hamerschlag Hall": "FEDCBA1234",
        "Hunt Library": "A12345",
        "Margaret Morrison Carnegie Hall": "CBA1234",
        "Newell Simon Hall": "BA1234",
        "Posner Center": "1",
        "Purnell Center for the Arts": "A123",
        "Roberts Engineering Hall": "A1234",
        "Scaife Hall": "A12345",
        "Tepper": "A123",
        "University Center": "L123",
        "Warner Hall": "A123456P",
        "Wean Hall": "123456789"
        }

    def initResidentialBuildings(self):
        """Residential buildings."""
        self.residentialBuildingNames = {
        "Boss House": "A123",
        "Donner House": "BA123",
        "Hamerschlag House": "A123",
        "Morewood E-Tower": "A1234567",
        "Morewood Gardens": "BA1234567",
        "Stever House": "B12345",
        "Mudge House": "A123",
        "Resnik House": "A12345",
        "Scobell House": "A123",
        "West Wing": "A123456"
        }

    def initAcademicLocations(self):
        """Academic building names and floors."""
        self.academicBuildingLocations = {
        "Baker - Porter Hall": (0,0),
        "College of Fine Arts": (399, 437),
        "Cyert Hall": (193, 268),
        "Doherty Hall": (256, 429),
        "Gates and Hillman Centers": (198, 357),
        "Hamburg Hall": (92, 330),
        "Hamerschlag Hall": (145, 511),
        "Hunt Library": (370, 500),
        "Margaret Morrison Carnegie Hall": (451, 347),
        "Newell Simon Hall": (150,400),
        "Posner Center": (440, 443),
        "Purnell Center for the Arts": (254, 313),
        "Roberts Engineering Hall": (92, 527),
        "Scaife Hall": (118, 581),
        "Tepper": (461, 457),
        "University Center": (340, 273),
        "Warner Hall": (229, 256),
        "Wean Hall": (179, 449)
        }

    def initResidentialLocations(self):
        """Residential buildings."""
        self.residentialBuildingLocations = {
        "Boss House": (611, 293),
        "Donner House": (555, 298),
        "Hamerschlag House": (656, 301),
        "Morewood E-Tower": (180,195),
        "Morewood Gardens": (174,157),
        "Stever House": (158, 74),
        "Mudge House": (99,45),
        "Resnik House": (520, 250),
        "Scobell House": (604,322),
        "West Wing": (464, 269)
        }

    def initBuildings(self):
        """Create building objects."""
        kind = 'Academic'
        for building in self.academicBuildingNames:
            floors = self.academicBuildingNames[building]
            location = self.academicBuildingLocations[building]
            self.academicBuildings[building] = \
            Building(self, building, floors, kind, location)

        kind = 'Residential'
        for building in self.residentialBuildingNames:
            floors = self.residentialBuildingNames[building]
            location = self.residentialBuildingLocations[building]
            self.residentialBuildings[building] = \
            Building(self, building, floors, kind, location)

    def getBuilding(self, building):
        """Get building object from name."""
        if building in self.academicBuildings:
            return self.academicBuildings[building]
        if building in self.residentialBuildings:
            return self.residentialBuildings[building]
        return None

    #http://www.kosbie.net/cmu/fall-12/15-112/
    #handouts/notes-recursion/removeDsStore.py
    def removeDsStore(self, path):
        """Remove DsStore files."""
        if (os.path.isdir(path) == False):
            if (path.endswith(".DS_Store")):
                print "removing:", path
                os.remove(path)
        else:
            # recursive case: it's a folder
            for filename in os.listdir(path):
                self.removeDsStore(path + "/" + filename)

    def renameImages(self):
        """Rename images in directory structure."""
        residPath = self.path + '/' + 'Residential'
        acadPath = self.path + '/' + 'Academic'
        for buildType in [residPath, acadPath]:
            for building in os.listdir(buildType):
                buildPath = buildType + '/' + building
                for floor in os.listdir(buildPath):
                    floorPath = buildPath + '/' + floor
                    if floor.endswith('.png') and '-' in floor:
                        self.renameImage(floorPath)

    def renameImage(self, path):
        """Rename single image."""
        newPath = path
        baseIndex = path.rfind('/') + 1
        basePath = path[:baseIndex]
        dashIndex = path.rfind('-')
        floorIndex = dashIndex - 1
        newPath = basePath + path[floorIndex] + '.png'
        os.rename(path, newPath)
        print "newPath  %s" % newPath

    def moveImages(self):
        """Move images into their own directory."""
        pdfPath = 'media/CMUPDF'
        self.removeDsStore(pdfPath)
        residPath = pdfPath + '/' + 'Residential'
        acadPath = pdfPath + '/' + 'Academic'
        for buildType in [residPath, acadPath]:
            for building in os.listdir(buildType):
                buildPath = buildType + '/' + building
                for floor in os.listdir(buildPath):
                    floorPath = buildPath + '/' + floor
                    if floor.endswith('.png'):
                        newFloorPath = floorPath[0:3] + floorPath[6:]
                        os.rename(floorPath, newFloorPath)

    def makeDirs(self):
        """Create directory structure for building files."""
        #campusPath = 'media/CMU'
        #self.makeDir(campusPath)
        campusPath = 'data/CMU'
        residPath = campusPath + '/' + 'Residential'
        self.makeDir(residPath)
        acadPath = campusPath + '/' + 'Academic'
        self.makeDir(acadPath)
        for building in self.residentialBuildings:
            self.makeDir(residPath + '/' + building)
        for building in self.academicBuildings:
            self.makeDir(acadPath + '/' + building)

    def makeDir(self, path):
        """Creates a directory if not previously made."""
        if not os.path.exists(path):
            os.makedirs(path)

    def closestBuilding(self, point, tolerance):
        """Return the closest building at a point within a tolerance."""
        for buildingName in self.academicBuildings:
            building = self.academicBuildings[buildingName]
            if self.distance(building.location, point) < tolerance:
                return building
        for buildingName in self.residentialBuildings:
            building = self.residentialBuildings[buildingName]
            if self.distance(building.location, point) < tolerance:
                return building
        return None

    def distance(self, point1, point2):
        """Distance formula."""
        x0, y0 = point1
        x1, y1 = point2
        return ((x1-x0)**2 + (y1-y0)**2)**0.5

    def __repr__(self):
        """Campus name."""
        return self.__class__.__name__

class Building(object):
    """Building object."""
    def __init__(self, parent, name, floorNames, kind, location):
        """Initialize building."""
        self.name = name
        self.location = location
        self.imagePath = 'media/CMU/' + kind + '/' + name
        self.dataPath = 'data/CMU/' + kind + '/' + name
        self.floorNames = floorNames
        self.floors = {}
        self.initFloors()

    def getFloorImages(self):
        """Get list of floor images."""
        images = []
        for floorName in self.floorNames:
            floor = self.floors[floorName]
            image = floor.getImage()
            images.append(image)
        return images

    def initFloors(self):
        """Initialize floors."""
        for floor in self.floorNames:
            self.floors[floor] = Floor(self, floor)

    def getFloor(self, floor):
        """Get floor object from name."""
        if floor in self.floors:
            return self.floors[floor]
        return None

    def __repr__(self):
        """Name of floor."""
        return self.name


class Floor(object):
    """Floor object."""
    def __init__(self, building, floor):
        """Initialize floor."""
        self.building = building
        self.imagePath = building.imagePath + '/' + floor + '.png'
        self.dataPath = building.dataPath + '/' + floor + '.pk'
        self.noImage = 'media/noImage.jpg'
        self.floor = floor
        self.name = building.name + ' ' + floor

    def getImage(self):
        """Get image file."""
        img = wx.EmptyBitmap(1, 1)
        if os.path.exists(self.imagePath):
            img.LoadFile(self.imagePath, wx.BITMAP_TYPE_ANY)
        else:
            img.LoadFile(self.noImage, wx.BITMAP_TYPE_ANY)
        return img

    def initEnvironment(self, size):
        """Initialize wifi environment."""
        if os.path.exists(self.dataPath):
            self.loadEnvironment()
        else:
            self.environment = wifi.Environment(self.name, size)

    def saveEnvironment(self):
        """Save wifi environment."""
        with open(self.dataPath, 'wb') as output:
            pickle.dump(self.environment, output)

    def loadEnvironment(self):
        """Load wifi environment."""
        with open(self.dataPath, 'rb') as input:
            self.environment = pickle.load(input)
        return False

    def __repr__(self):
        """Floor name."""
        return self.name
