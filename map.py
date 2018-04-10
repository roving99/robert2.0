import pygame, sys
from pygame.locals import *
import math
import random
import Queue

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARKGRAY = (64, 64, 64)
GRAY = (128, 128, 128)

def asColour(f):
    '''
    flaot 0-1.0 to 8 bit gray scale colour.
    '''
    return (int(f*255), int(f*255), int(f*255))

def asValue(colour):
    '''
    8 bit grayscale colour to value 0-1.0
    '''
    return float(colour[0]/255.0)

def degreesToRadians(deg):
    '''
    Derr!
    '''
    return deg/180.0 * math.pi

class OccupancyMap():
    '''
    2d map of cells containing probablity of occupation (0.0-1.0) at that position.
    '''
    def __init__(self, size, _map=None):       # scale = size of cells in cm.
        self.x = int(size[0])
        self.y = int(size[1])
        if _map==None:
            self.surface = pygame.Surface((size))    # RGB surface
        else:
            self.surface = _map
        self.robotOutline = pygame.Surface((10,10), pygame.SRCALPHA)    # define DEFAULT robot shape (10x10 square)
        self.robotOutline.fill((0,0,0))

    def setValue(self, position, value):
        '''
        Set value of a cell (0.0-1.0)
        '''
        self.surface.set_at(position, asColour(value))

    def getValue(self, position):
        '''
        Set value of a cell (0.0-1.0)
        '''
        return asValue(self.surface.get_at(position))

    def reset(self, value = 0.5):
        '''
        Reset whole map to flat (0.5).
        '''
        self.surface.fill(asColour(value))

    def getMap(self):
        '''
        get pygame surface copy of map.
        '''
        return self.surface.copy()

    def setMap(self, _map):
        '''
        Set pygame surface map.
        '''
        self._map = _map

    def getMapSize(self):
        '''
        '''
        return (self.x, self.y)

    def stamp(self, position, surface):     # stamp a surface into map CENTERED at x,y
        '''
        Stamp another surface (normally with a transparent layer) onto the map.
        Usually used to mark position occupied by robot as clear of obstructions.
        Will later be used to stamp arcs of sensor data?
        '''
        w, h = surface.get_size()
        self.surface.blit(surface, (position[0]-int(w/2), position[1]-int(h/2)))

    def setRobotShape(self, robotSurface):
        '''
        Set shape used to represent robot when. Should have a key layer!
        '''
        self.robotOutline = robotSurface

    def robotAt(self, position, theta):
        '''
        Set robot position and mark robot shape as being free from obstruction.
        '''
        robotRotated = pygame.transform.rotate(self.robotOutline, 360*theta/(2.0*math.pi))
        self.stamp(position, robotRotated)

    def createTestWorld(self):
        '''
        Create a test world.
        '''
        self.surface.fill((asColour(1.0)))
        pygame.draw.rect(self.surface, BLACK, [5,5, self.x-10, self.y-10])
        for i in range(0,5):
            pygame.draw.circle(self.surface, asColour(random.randint(0,60)/100.0+0.4), [random.randint(0,self.x), random.randint(0,self.y)], random.randint(0,self.x/4))
        for i in range(0,5):
            pygame.draw.rect(self.surface, asColour(random.randint(0,60)/100.0+0.4), [random.randint(0,self.x), random.randint(0,self.y), random.randint(0,self.x/4), random.randint(0,self.x/4)])
        pygame.draw.rect(self.surface, WHITE, [0, 0, 5, self.y])
        pygame.draw.rect(self.surface, WHITE, [0, 0, self.x, 5])
        pygame.draw.rect(self.surface, WHITE, [self.x-5, 0, 5, self.y])
        pygame.draw.rect(self.surface, WHITE, [0, self.y-5, self.x, 5])
    
    def view(self):     # return surface showing map
        '''
        Return surface showing map, robot position, target position.
        '''
        result = self.surface.copy()
        return result

def zoomMap(_map, centre, zoom, size):  
    '''
    pygame surface centred on centre, zoomed and clipped to size.
    '''
    ox, oy = _map.get_size()
    nx, ny = size
    x, y = size
    cx, cy = centre
    if zoom<=(float(nx)/float(ox)):    # if zoom will not fit new size..
        zoom = float(nx)/float(ox)
    result = pygame.Surface([ox*2, oy*2])   # Surface big enough to overhang
    result.fill(RED)
    result.blit(_map, [ox/2, oy/2])       # copy map into middle of big surface
    result = result.subsurface([cx, cy, ox, oy])    # surface same size as original, centred.
    result = pygame.transform.scale(result, [int(ox*zoom), int(oy*zoom)]) # zoom 
    result = result.subsurface([int((ox*zoom-x)/2), int((oy*zoom-y)/2), x, y])
    return result

mainLoop = True

if __name__=="__main__":
    pygame.init()
    print 'pygame started'

    DISPLAY_SURF = pygame.display.set_mode((640, 480))
    
    myMap = OccupancyMap((200, 200))
    print 'map created'
    myMap.reset()
    print 'reset'
    print '[0, 0] returns ', myMap.getValue((0, 0))
    myMap.setValue((0, 0), 0.99)
    print '[0, 0]=0.99'
    print '[0, 0] returns ', myMap.getValue((0, 0))
    print
    print 'R - Reset'
    print 'C - Create world.'
    print 'Q - Quit'

    zoom = 2.0

    while mainLoop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainLoop = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    myMap.reset()
                if event.key == pygame.K_c:
                    myMap.createTestWorld()
                if event.key == pygame.K_q:
                    mainLoop = False
                if event.key == pygame.K_z:
                    zoom = zoom+0.2
                if event.key == pygame.K_a:
                    if zoom>1.0:
                        zoom = zoom-0.2

        DISPLAY_SURF.fill( (0,0,0) )
        DISPLAY_SURF.blit(myMap.view(), [10,10] )
        DISPLAY_SURF.blit(zoomMap(myMap.view(), [0,0], zoom, [350,350]), [250,10] )
        DISPLAY_SURF.blit(zoomMap(myMap.view(), [199,199], zoom, [250,250]), [150,110] )

        pygame.display.update()

