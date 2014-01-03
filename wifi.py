import subprocess
from time import time

class FullScan(object):
    """Current information and full broadcast scan."""
    def __init__(self, location):
        self.path = "/System/Library/PrivateFrameworks/" + \
                    "Apple80211.framework/Versions/Current/Resources/airport"
        self.scans = []
        self.location = location
        self.macInfo()
        self.macScan()

    def macInfo(self):
        """Current connection information."""
        call = self.path + " -I"
        info = subprocess.Popen(call, stdout=subprocess.PIPE, shell=True)
        (rawData, error) = info.communicate()
        if error:
            print error
            assert False
        splitData = rawData.splitlines()
        rawNoise = splitData[2]
        rawRSSI = splitData[0]
        macColon = rawNoise.index(':')
        noise = rawNoise[macColon + 2:]
        macColon = rawRSSI.index(':')
        rssi = rawRSSI[macColon + 2:]
        self.noise = int(noise)
        self.rssi = int(rssi)
        self.snr = self.rssi - self.noise

    def macScan(self):
        """Full broadcast scan."""
        call = self.path + " -s"
        scan = subprocess.Popen(call, stdout=subprocess.PIPE, shell=True)
        (rawData,error) = scan.communicate()
        if error:
            print error
            assert False
        splitData = rawData.splitlines()
        end = len(splitData)
        if '' in splitData:
            end = splitData.index('')
        splitData = splitData[1:end]
        self.data = splitData
        self.addScans()

    def addScans(self):
        """Add scans to list of scans."""
        for row in self.data:
            self.scans.append(Scan(self.location, self.noise, row))

    def results(self):
        """Print scan results."""
        print "Scan Results:"
        for scan in self.scans:
            print scan.info()

class Scan(object):
    """Data of single router from scan."""
    def __init__(self, location, noise, rawdata):
        """Initialize scan."""
        self.location = location
        self.rawdata = rawdata
        self.noise = int(noise)
        self.data = rawdata
        self.processData()

    def processData(self):
        """Process the raw string data."""
        macColon = self.data.index(':')
        self.network = self.data[:macColon-3].strip()
        self.data = self.data[macColon-2:].split()
        self.mac = self.data[0]
        self.rssi = int(self.data[1])
        self.snr = self.rssi - self.noise
        self.channel = self.data[2]
        self.ht = self.data[3]
        self.cc = self.data[4]
        self.security = self.data[5]

    def info(self):
        """Wifi information."""
        return self.network, self.mac, self.rssi, self.channel

# From 15-112 notes on 2d lists.
# Helper function for print2dList.
# This finds the maximum length of the string
# representation of any item in the 2d list
def maxItemLength(a):
    """Returns maximum of items in 2d list."""
    maxLen = 0
    rows = len(a)
    cols = len(a[0])
    for row in xrange(rows):
        for col in xrange(cols):
            maxLen = max(maxLen, len(str(a[row][col])))
    return maxLen

# Because Python prints 2d lists on one row,
# we might want to write our own function
# that prints 2d lists a bit nicer.
def print2dList(a):
    """Print a 2d list."""
    if (a == []):
        # So we don't crash accessing a[0]
        print []
        return
    rows = len(a)
    cols = len(a[0])
    fieldWidth = maxItemLength(a)
    print "[ ",
    for row in xrange(rows):
        if (row > 0): print "\n  ",
        print "[ ",
        for col in xrange(cols):
            if (col > 0): print ",",
            # The next 2 lines print a[row][col] with the given fieldWidth
            format = "%" + str(fieldWidth) + "s"
            print format % str(a[row][col]),
        print "]",
    print "]"

class Environment(object):
    """Wifi environment object."""
    def __init__(self, name, size):
        """Initialize environment."""
        self.networks = {}
        self.scans = []
        self.name = name
        self.hmap = None
        self.heatmap = None
        self.locations = []
        self.dimensions = size
        self.res = 10

    def scanData(self):
        """Add data from scan."""
        self.data = {}
        for scan in self.scans:
            self.data[scan.location] = scan.snr
        heatmap = Heatmap(self.dimensions, self.data, self.res)
        self.heatmap = heatmap
        self.hmap = heatmap.hmap

    def scan(self, location):
        """Perform scan at location."""
        newScan = FullScan(location)
        self.scans.append(newScan)
        self.locations.append(location)
        for scan in newScan.scans:
            self.addNetwork(scan)
        self.scanData()

    def addNetwork(self, scan):
        """Add network to list of networks."""
        network = scan.network
        if network in self.networks:
            self.networks[network].addRouter(scan)
        else:
            self.networks[network] = Network(scan)

    def reset(self):
        """Reset all networks."""
        self.networks = {}
        for fullScan in self.scans:
            for scan in fullScan.scans:
                self.addNetwork(scan)

    def undo(self):
        """Undo scan."""
        if self.scans:
            self.scans.pop(len(self.scans)-1)
            self.locations.pop(len(self.locations)-1)
            self.reset()

    def printEnv(self):
        """Print environment."""
        print self.name, "Environment:"
        for network in self.networks:
            self.networks[network].printNet()

class Network(object):
    """Network object."""
    def __init__(self, scan):
        """Initialize network."""
        self.name = scan.network
        self.routers = {}
        self.addRouter(scan)

    def addRouter(self, scan):
        router = scan.mac
        if router in self.routers:
            self.routers[router].addScan(scan)
        else:
            self.routers[router] = Router(scan)

    def printNet(self):
        print self.name, "Network:"
        for router in self.routers:
            self.routers[router].printRouter()

    def __repr__(self):
        """Network name."""
        return self.name

    def __eq__(self,other):
        """Network equality."""
        return self.name == self.other

class Heatmap(object):
    """Heatmap object."""
    def __init__(self, dimensions, data, res):
        """Intialize heatmap from data, dimensions, and resolution."""
        self.width, self.height = dimensions
        self.res = res
        self.data = data
        self.low = self.high = None
        self.rows, self.cols = int(self.width/res), int(self.height/res)
        self.hmap = [[0]*self.cols for _ in xrange(self.rows)]
        self.makemap()

    def makemap(self):
        """Create heatmap."""
        for row in xrange(self.rows):
            for col in xrange(self.cols):
                x, y = row*self.res, col*self.res
                val = self.value((x, y))
                if self.low == None:
                    self.low = val
                self.low = min(self.low, val)
                self.high = max(self.high, val)
                self.hmap[row][col] = val

    def value(self, p1):
        """Calculate value at the point."""
        total = 0
        totalWeight = self.findTotalWeight(p1)
        for location in self.data:
            weight = self.findWeight(p1, location)
            total += self.data[location]*weight/totalWeight
        return total

    def findTotalWeight(self, p1):
        """Find total weight at a point."""
        total = 0
        for location in self.data:
            total += self.findWeight(p1, location)
        return total

    def distance(self, p1, p2):
        """Distance formula."""
        x1, y1 = p1
        x2, y2 = p2
        return ((x2-x1)**2 + (y2-y1)**2)**0.5

    def findWeight(self, p1, p2):
        """Find weight between 2 points."""
        p = 2
        distance = self.distance(p1, p2)
        if distance == 0: return 1
        weight = 1 / (distance**p)
        return weight

class Router(object):
    """Router object."""
    def __init__(self, scan):
        """Initialize routers."""
        self.mac = scan.mac
        self.scans = {}
        self.maxLocation = self.maxSNR = 0
        self.channel = scan.channel
        self.addScan(scan)

    def addScan(self, scan):
        """Add scan to router."""
        self.scans.update({scan.location:scan})
        self.updateStrongest()

    def printRouter(self):
        """Print router representation."""
        print self.mac, self.channel, self.rssi, self.maxLocation, self.maxSNR

    def updateStrongest(self):
        """Update the strongest router."""
        for location in self.scans:
            scan = self.scans[location]
            if scan.snr > self.maxSNR:
                self.maxSNR = scan.snr
                self.maxLocation = location

    def __repr__(self):
        """Router name."""
        return self.mac
