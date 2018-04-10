import pygame, sys
from pygame.locals import *
import math
import random
import Queue

import map as omap

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

class Planner(object):
    '''
    Prototype for route planners using Map objects.
    '''
    def __init__(self, _map):
        self._map = _map
        self.startPosition = (10,10)
        self.endPosition = (10,10)
        self.route = []

    def reset(self):
        pass
    
    def setStart(self, position):
        self.startPosition = position

    def setEnd(self, position):
        self.endPosition = position

    def _availableNeighbours(self, n, useMap = None):
        '''
        For a cell n, return a list of cells that neighbour it orthagonally.
        '''
        if useMap==None:
            useMap = self._map
        result = []
        x = n[0]
        y = n[1]
        mapX, mapY = self._map.getMapSize()
        threshold = 0.75
        if x>0 and y>0 and useMap.getValue((x-1, y-1))<threshold:
            result.append((x-1,y-1))
        if y>0 and useMap.getValue((x, y-1))<threshold:
            result.append((x,y-1))
        if y>0 and x<mapX and useMap.getValue((x+1, y-1))<threshold:
            result.append((x+1,y-1))

        if x>0 and useMap.getValue((x-1, y))<threshold:
            result.append((x-1,y))
        if x<mapX and useMap.getValue((x+1, y))<threshold:
            result.append((x+1,y))

        if x>0 and y<mapY and useMap.getValue((x-1, y+1))<threshold:
            result.append((x-1,y+1))
        if y<mapY and useMap.getValue((x, y+1))<threshold:
            result.append((x,y+1))
        if x<mapX and y<mapY and useMap.getValue((x+1, y+1))<threshold:
            result.append((x+1,y+1))
        return result

    def view(self):
        '''
        return surface showing map + other bits.
        '''
        result = self._map.getMap().copy()
        pygame.draw.rect(result, RED, [self.startPosition[0]-1, self.startPosition[1]-1, 2,2])
        pygame.draw.rect(result, GREEN, [self.endPosition[0]-1, self.endPosition[1]-1, 2,2])
        for position in self.route:
            result.set_at(position,MAGENTA)
        return result

    def calculateRoute(self):
        '''
        Do the clever stuff.
        '''
        return self.route

    def getRoute(self):
        '''
        route as list of way-point cells.
        '''
        return self.route

#=======================================================================================
# Specific planner strageties
#=======================================================================================

class BroadPlanner(Planner):

    def __init__(self, _map):
        super(BroadPlanner, self).__init__(_map)    # parents __init__.
        '''
        add hash containing which cell the frontier 'came from' in getting to any other.
        '''
        self.came_from = {}

    def _calculateCameFrom(self):
        '''
        From the start position iteratively visit each neightbour, recording the last step of 
        the journey ('came from') for each cell. Finding the route from any point to the 
        start position is then a case of following the 'came from' trail.
        '''
        start = self.startPosition
        frontier = Queue.Queue()        # Queue - FIFO
        frontier.put(start)             # first cell to consider
        self.came_from = {}             # each cell visited has an entry in here telling us where it was visited from
        self.came_from[start] = None    # .. apart from the origin of the search

        useMap = self._mapWithBumper()  # draws 'safe distance' around all obstacles.

        while not frontier.empty():     # cells to check?
            current = frontier.get()
            if current==self.endPosition:   # are we there yet? optimization
                break
            #print current, self._availableNeighbours(current, useMap)
            for next in self._availableNeighbours(current, useMap):
                if next not in self.came_from:
                    frontier.put(next)
                    self.came_from[next] = current

    def calculateRoute(self):
        '''
        From the target position, follow the 'came from' trail until we arrive at the start location.
        '''
        self.route = []
        self._calculateCameFrom()
        if self.endPosition in self.came_from:
            position = self.came_from[self.endPosition]
        else:
            position = None
        if position == None:
            return None
        while position != self.startPosition:
            self.route.append(position)
            position = self.came_from[position]
        return self.route

    def _mapWithBumper(self, r=6):
        '''
        draw an avoidance circle (r=in-place turning radius of robot) about any cells deemed 
        to be obstacles.
        Returns a map of result.
        '''
        return omap.OccupancyMap(self._map.getMapSize(), _map=self._viewBumper())

    def _viewBumper(self, r=6):
        '''
        draw an avoidance circle (r=in-place turning radius of robot) about any cells deemed to be obsticles.
        '''
        result = pygame.Surface(self._map.getMapSize())
        sx, sy = self._map.getMapSize()
        threshold = 0.75
        for x in range(0,sx-1):
            for y in range(0,sy-1):
                if self._map.getValue((x,y))>threshold:
                    pygame.draw.circle(result, WHITE, (x, y), r)
        return result

    def _viewVisited(self):
        '''
        return surface showing map + visited cells.
        '''
        result = pygame.Surface(self._map.getMapSize())
        for n in self.came_from.keys():     # NATIVE coords
            x = n[0]
            y = n[1]
            result.set_at((x,y),BLUE)
        return result

    def _viewCameFrom(self):     # return surface showing map + other bits.
        '''
        Show came-from info for each visited cell.
        RED - West, BLUE - East, GREEN - North, YELLOW - South.
        '''
        result = pygame.Surface(self._map.getMapSize())
        for n in self.came_from.keys():     # NATIVE coords
            x = n[0]
            y = n[1]
            if self.came_from[n]:
                nx = self.came_from[n][0]
                ny = self.came_from[n][1]
                if x<nx:
                    result.set_at((x,y),RED)
                if x>nx:
                    result.set_at((x,y),BLUE)
                if y<ny:
                    result.set_at((x,y),GREEN)
                if y>ny:
                    result.set_at((x,y),YELLOW)
        return result

#===================================================================================

class BestFirstPlanner(BroadPlanner):

    def __init__(self, _map):
        super(BestFirstPlanner, self).__init__(_map)    # parents __init__.

    def _calculateCameFrom(self):    # works on NATIVE coords.
        '''
        From the start position (robot location), iteratively visit each neightbour, recording the last step of 
        the journey ('came from') for each cell. Finding the route from any point to the start position is then a case of following 
        the 'came from' trail.
        In 'BEST FIRST' we prioritize cells closest to the goal.
        '''
        start = self.startPosition
        frontier = Queue.PriorityQueue()    # some cells are better than others..
        frontier.put((None, start))         # No priority
        self.came_from = {}
        self.came_from[start] = None

        useMap = self._mapWithBumper()

        while not frontier.empty():
            current = frontier.get()[1]     # (priority, location) 
            #print current
            if current==self.endPosition:
                break
            for next in self._availableNeighbours(current, useMap):
                if next not in self.came_from:
                    priority = self.heuristic(next)     # distance from endPosition
                    frontier.put((priority, next))      # (priority, location) 
                    self.came_from[next] = current

    def heuristic(self, position):
        '''
        Manhattan distance to endPosition
        '''
        return abs(self.endPosition[0]-position[0])*abs(self.endPosition[1]-position[1])

def pruneRoute(route):  
    '''
    prune a list of way-points to only way-points requiring a rotation.
    '''
    result = []
    result.append(route[0])     # start position
    lastBearing = (route[1][0]-route[0][0], route[1][1]-route[0][1])

    for i in range(len(route)-1):
        bearing =  (route[i+1][0]-route[i][0], route[i+1][1]-route[i][1])
        if bearing != lastBearing:
            result.append(route[i])
            lastBearing = bearing
    result.append(route[-1])
    return result
        

mainLoop = True

if __name__=="__main__":
    pygame.init()
    print 'pygame started'

    DISPLAY_SURF = pygame.display.set_mode((640, 480))
    
    myMap = omap.OccupancyMap((200, 200))
    print 'map created'
    
    #myPlanner = BroadPlanner(myMap)
    myPlanner = BestFirstPlanner(myMap)

    print 'Planner created'
    myMap.reset()
    myPlanner.reset()
    print 'reset'
    print
    print 'R - Reset'
    print 'C - Create World'
    print 'F - Find route'
    print 'Q - Quit'

    myMap.createTestWorld()

    myPlanner.setStart((20,20))
    myPlanner.setEnd((180,180))

    while mainLoop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainLoop = False
                
            x = pygame.mouse.get_pos()[0]
            y = pygame.mouse.get_pos()[1]
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('mouse : '+str(x)+', '+str(y))
                if ((x>10) & (x<210) & (y>10) & (y<210)):
                    myMap.targetAt(x-110, y-110)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    myMap.createTestWorld()
                if event.key == pygame.K_r:
                    myMap.reset()
                if event.key == pygame.K_q:
                    mainLoop = False
                if event.key == pygame.K_f:
                    myPlanner.calculateRoute()
                    print myPlanner.getRoute()
                    print pruneRoute(myPlanner.getRoute())

        DISPLAY_SURF.fill( (0,0,0) )
        DISPLAY_SURF.blit(myMap.view(), [10,10] )
        DISPLAY_SURF.blit(myPlanner._viewCameFrom(), [220,10] )
        DISPLAY_SURF.blit(myPlanner._viewBumper(), [430,10] )
        DISPLAY_SURF.blit(myPlanner.view(), [10,220] )

        pygame.display.update()

