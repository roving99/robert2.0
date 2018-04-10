import math


class Point(object):
    """
       The class Point represents a 2D point
       Class attributes:    points
       Instance attributes: x
                            y
    """
    def __init__(self):
        self.x = 0
        self.y = 0
#        Point.points.append(self)

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
#        Point.points.append(self)

    def __str__(self):
       return '(%g, %g)' % (self.x, self.y)

    # Special names methods. . .
    # With this method defined, we can use + to add two point objects
    # as in p1 + p2 which is equivalent to p1.__add__(p2)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    # With this method defined, two point objects can be compared with >, <, and ==.
    def __cmp__(self, other):
        # compare them using the x values first
        if self.x > other.x: return 1
        if self.x < other.x: return -1
        # x values are the same... check y values
        if self.y > other.y: return 1
        if self.y < other.y: return -1
        # y values are the same too. . . it's a tie
        return 0

    # Other general methods
    def distance_from_origin(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def distance(self, other):
        dx = math.fabs(self.x - other.x)
        dy = math.fabs(self.y - other.y)
        return math.sqrt(dx * dx + dy * dy)
    
    def distance2(self, other):
        dx = math.fabs(self.x - other.x)
        dy = math.fabs(self.y - other.y)
        return (dx * dx + dy * dy)

    def isIn1stQuad(self):
        return (self.x > 0) and (self.y > 0)

    def asPair(self):
        return (self.x, self.y)

class Cloud(object):
    def __init__(self, c=None):
        # ingest 'old style' LIDAR cloud {angle:(x,y), angle:(x,y),...}
        self.set = []
        if c:
            for p in c:
                self.set.append(Point(c[p][0], c[p][1]))

    def __str__(self):
        s = "[ "
        for p in self.set:
#            s = s+"("+str(p.x)+', '+str(p.y)+"), "
            s = s+str(p)+', '
        s = s+"]"
        return str(s)

    def append(self, p):
        self.set.append(p)

    def pointsWithin(self, pos, radius):
        #returns cloud of points within radius of pos.
        result = Cloud()
        centre = Point(pos[0], pos[1])
        d2 = radius*radius # save on a sqrt operation.
        for p in self.set:
            if centre.distance2(p)<d2:
                result.append(p)
        return result

    def xs(self): # list of all x values
        result = []
        for p in self.set:
            result.append(p.x)
        return result


    def ys(self): # list of all y values
        result = []
        for p in self.set:
            result.append(p.y)
        return result        

    def mean(self):
        n = len(self.set)
        if n==0:
            return Point()
        else:
            return Point(x=sum(self.xs())/n, y=sum(self.ys())/n)

    def leastSquare(self):
        '''
        determine line (form y = mx+b) best fitting scatter data x,y
        '''
        n = len(self.set)
        if n==0:
            return None, None
        meanX = sum(self.xs())/n
        meanY = sum(self.ys())/n
        top = 0.0
        bottom = 0.0
        for p in self.set:
            top = top+(p.x-meanX)*(p.y-meanY)
            bottom = bottom + (p.x-meanX)**2
        if abs(bottom)<0.0000001:
            bottom = 0.0000001
        m = top/bottom
        b = meanY - m*meanX
        return m, b

if __name__=="__main__":
    import graph
    import pygame
    import neato

    cloud = [
        Point(3,2),
        Point(2,8),
        Point(7,5),   
    ]

    test= {0: (1167, 256), 1: (1162, 272), 2: (1156, 265), 3: (1152, 268), 4: (1147, 275), 5: (1144, 265), 6: (1141, 261), 7: (1138, 274), 8: (1135, 268), 9: (1132, 267), 10: (1130, 271), 11: (1129, 281), 12: (1128, 274), 13: (1127, 279), 14: (1127, 275), 15: (1128, 275), 16: (1128, 287), 17: (1128, 275), 18: (1129, 277), 19: (1129, 280), 20: (1132, 279), 21: (1135, 267), 22: (1137, 274), 23: (1140, 264), 24: (1142, 271), 25: (1147, 256), 26: (1152, 261), 27: (1156, 257), 28: (1161, 260), 29: (1167, 257), 30: (1171, 261), 31: (1179, 255), 32: (1184, 253), 33: (1191, 257), 34: (1199, 251), 35: (1207, 250), 36: (1214, 243), 37: (1225, 244), 38: (1233, 237), 39: (1244, 236), 40: (1256, 233), 41: (1267, 225), 42: (1278, 222), 43: (1291, 199), 44: (1304, 191), 45: (1318, 198), 46: (1335, 180), 47: (1351, 193), 48: (1368, 193), 49: (1385, 180), 50: (1403, 158), 51: (1422, 143), 52: (1440, 164), 53: (1459, 152), 54: (1484, 153), 55: (1506, 143), 56: (1529, 128), 57: (1556, 145), 58: (1585, 121), 59: (1613, 123), 60: (1641, 111), 61: (1674, 114), 62: (1707, 123), 63: (1727, 117), 64: (1695, 124), 65: (1669, 123), 66: (1646, 133), 67: (1623, 130), 68: (1599, 131), 69: (1582, 156), 70: (1557, 143), 71: (1540, 166), 72: (1522, 175), 73: (1504, 146), 74: (1488, 164), 75: (1471, 156), 76: (1454, 166), 77: (1438, 169), 78: (1461, 63), 79: (1520, 57), 80: (1589, 61), 81: (1659, 49), 82: (1735, 47), 83: (1817, 30), 84: (1915, 16), 85: (1825, 55), 86: (2144, 12), 87: (2263, 8), 90: (2083, 9), 91: (2059, 15), 93: (2246, 13), 95: (4509, 9), 96: (4432, 12), 97: (4470, 12), 105: (4197, 14), 106: (4045, 9), 116: (4707, 8), 133: (4249, 17), 134: (4287, 15), 135: (4388, 11), 136: (4459, 13), 139: (1823, 96), 140: (1813, 111), 141: (1822, 85), 142: (2387, 37), 143: (2316, 36), 144: (2265, 33), 145: (2217, 45), 146: (2173, 62), 147: (2120, 52), 148: (2082, 54), 149: (2045, 61), 150: (2008, 59), 151: (1966, 64), 152: (1935, 85), 153: (1981, 72), 154: (2017, 71), 155: (2076, 67), 156: (2088, 37), 157: (2147, 12), 158: (2196, 13), 159: (2260, 9), 160: (2308, 7), 161: (2403, 12), 162: (2467, 17), 163: (2591, 10), 165: (2786, 27), 166: (2821, 8), 190: (3346, 16), 191: (3344, 19), 218: (4825, 13), 219: (4624, 6), 220: (4351, 17), 221: (4151, 8), 222: (4108, 11), 223: (3965, 12), 224: (3809, 13), 225: (3675, 12), 226: (3602, 19), 227: (3480, 22), 228: (3346, 18), 229: (3250, 24), 230: (3189, 28), 231: (3107, 27), 232: (2990, 33), 233: (2940, 39), 234: (2881, 32), 235: (2818, 43), 236: (2761, 33), 237: (2698, 46), 238: (2633, 47), 239: (2581, 54), 240: (2532, 46), 241: (2502, 55), 242: (2453, 53), 243: (2451, 56), 244: (2514, 63), 245: (2580, 47), 246: (2651, 41), 247: (2707, 35), 248: (2776, 38), 249: (2842, 55), 250: (2830, 53), 251: (2789, 51), 252: (2767, 55), 253: (2741, 67), 254: (2697, 70), 255: (2676, 50), 256: (2645, 76), 257: (2621, 57), 258: (2589, 63), 259: (2584, 77), 260: (2553, 79), 261: (2531, 80), 262: (2503, 65), 263: (2491, 93), 264: (2470, 43), 265: (2456, 88), 266: (2445, 84), 267: (2348, 97), 268: (2344, 92), 269: (2306, 105), 270: (2309, 83), 271: (2312, 92), 272: (2302, 83), 273: (2304, 83), 274: (2270, 97), 275: (2275, 94), 276: (2261, 97), 277: (2241, 113), 278: (2245, 122), 279: (2250, 111), 280: (2245, 99), 281: (2225, 137), 282: (2241, 134), 283: (2242, 107), 284: (2236, 107), 285: (2241, 112), 286: (2244, 97), 287: (2238, 102), 288: (2246, 108), 289: (2251, 120), 290: (2262, 105), 291: (2259, 103), 292: (2261, 106), 293: (2265, 100), 294: (2276, 93), 295: (2286, 93), 296: (2299, 99), 297: (2303, 104), 298: (2320, 92), 299: (2328, 78), 300: (2340, 91), 301: (2353, 92), 302: (2373, 83), 303: (2381, 81), 304: (2397, 75), 305: (2411, 81), 306: (2438, 72), 307: (2454, 76), 308: (2481, 77), 309: (2495, 75), 310: (2521, 77), 311: (2530, 74), 312: (2580, 60), 313: (2602, 67), 314: (2610, 56), 315: (4380, 17), 316: (4187, 20), 317: (4301, 16), 318: (4245, 16), 319: (4242, 15), 320: (4214, 21), 321: (4102, 23), 322: (3983, 12), 323: (4086, 27), 324: (4157, 16), 325: (4161, 17), 326: (1726, 58), 327: (1688, 119), 328: (1654, 113), 329: (1624, 126), 330: (1597, 136), 331: (1568, 127), 332: (1543, 140), 333: (1521, 146), 334: (1498, 149), 335: (1472, 157), 336: (1451, 158), 337: (1433, 163), 338: (1412, 167), 339: (1397, 168), 340: (1377, 204), 341: (1362, 174), 343: (711, 66), 344: (693, 179), 345: (683, 212), 346: (674, 201), 347: (670, 278), 348: (666, 334), 349: (667, 337), 350: (669, 289), 351: (676, 220), 352: (687, 154), 353: (698, 79), 354: (719, 64), 355: (738, 19), 356: (1191, 249), 357: (1186, 238), 358: (1180, 263), 359: (1172, 257)}
    testCloud = neato.toCloud(neato.prune(test))

    for pt in cloud:
        print pt

    print cloud[0], ' +', cloud[1], ' =', cloud[0]+cloud[1]
    print cloud[0], ' ==', cloud[1], ' ?', cloud[0]==cloud[1]
    print cloud[0], ' >', cloud[1], ' ?', cloud[0]>cloud[1]
    print cloud[0], ' <', cloud[1], ' ?', cloud[0]<cloud[1]
    print cloud[2], ' ==', cloud[2], ' ?', cloud[2]==cloud[2]
    print 'length of', cloud[0], ' =', cloud[0].distance_from_origin()
    print 'length of', cloud[1], ' =', cloud[1].distance_from_origin()
    
    myCloud = Cloud(testCloud)
    print 'TEST--------------------------'
    print test
    print 'CLOUD-------------------------'
    print myCloud
    print graph.WHITE
    selection = Cloud() # points selected using mouse.

    pygame.init()
 
    size = (800,800)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Points')
    done = False
    clock = pygame.time.Clock()
    m, b = None, None

    displayZoom = 0.1
    myGraph = graph.Graph((800,800), origin=(400,400), scale=displayZoom)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    done = True 
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                print myGraph.mouseToGraph(pos)
                selection = myCloud.pointsWithin(myGraph.mouseToGraph(pos), 500)
                m,b = selection.leastSquare()
        
        screen.fill(graph.RED)
        myGraph.draw()
        for p in myCloud.set:
            myGraph.draw_circle(graph.WHITE, p.asPair(), 1)
        for p in selection.set:
            myGraph.draw_circle(graph.RED, p.asPair(), 1)

        myGraph.draw_circle(graph.PURPLE, selection.mean().asPair(), 2)
        if m:
            myGraph.draw_line_mb(graph.GREEN, m, b, 1)
        screen.blit(myGraph.surface, (0,0))
        pygame.display.flip()

        clock.tick(10)  # limit to 10 fps (plenty fast enough)

    pygame.quit()
