import math
import random
AIR_RESISTENCE = 0.99 #make it lower to increase air resistence
def get_vector_shrunk(point1, point2, magnitude):
    distanceX = point2[0] - point1[0]
    distanceY = point2[1] - point1[1]
    vector = [distanceX, distanceY]
    hypotenuse = math.sqrt((distanceX**2) + distanceY**2)
    try:
        shrinkFactor = magnitude/hypotenuse
        vector = [vector[0]*shrinkFactor, vector[1]*shrinkFactor]
        return vector
    except:
        return [0, magnitude]

def subtract_magnitude(vector, magnitude):
    newMagnitude = math.sqrt((vector[0]**2)+(vector[1]**2))
    
    newMagnitude -= magnitude
    
    return get_vector_shrunk([0,0], vector, newMagnitude)

def vector_to_angle(vector):
    try:
        slope = vector[1]/vector[0]
    except ZeroDivisionError:
        return 90
    subtract = 0
    if abs(vector[0]) != vector[0]:
        subtract = 180
    angle = math.atan(slope)*180/math.pi
    return ((360 + (angle - subtract)) % 360)

def doCollisions(collisions):
    for collision in collisions:
        compression = [0, 0]
        sideHit = collision[1].getSideHit(collision[2])
        if sideHit == "vertical":
            mag1 = collision[0].energy[0]
            mag2 = collision[1].energy[0]
            lesser, greater = (collision[0], collision[1]) if mag2 > mag1 else (collision[1], collision[0])
            if isinstance(collision[0], ground):
                didHit = False
                lesser, greater = (collision[0], collision[1])
            elif isinstance(collision[1], ground):
                didHit = False
                lesser, greater = (collision[1], collision[0])
            newMag = greater.energy[0] - lesser.energy[0]
            if greater.energy[0]*lesser.mass > greater.energy[0]:
                compression[0] = greater.energy[0]
                greater.energy[0] = 0
            else:
                compression[0] = greater.energy[0] - (greater.energy[0]*lesser.mass)
                greater.energy[0] -= greater.energy[0]*lesser.mass
                greater.energy[0] += newMag
            greater.energy[0] -= compression[0]
            lesser.energy[0] = lesser.energy[0]+newMag
        elif sideHit == "horizontal":
            mag1 = collision[0].energy[1]
            mag2 = collision[1].energy[1]
            lesser, greater = (collision[0], collision[1]) if mag2 > mag1 else (collision[1], collision[0])
            if isinstance(collision[0], ground):
                didHit = False
                lesser, greater = (collision[0], collision[1])
            elif isinstance(collision[1], ground):
                didHit = False
                lesser, greater = (collision[1], collision[0])
            newMag = greater.energy[1] - lesser.energy[1]
            if greater.energy[1]*lesser.mass > greater.energy[1]:
                compression[1] = greater.energy[1]
                greater.energy[1] = 0
            else:
                compression[1] = greater.energy[1] - (greater.energy[1]*lesser.mass)
                greater.energy[1] -= greater.energy[1]*lesser.mass
                greater.energy[1] += newMag
            greater.energy[1] -= compression[1]
            lesser.energy[1] = lesser.energy[1]+newMag
        if not isinstance(greater, ground) and not isinstance(lesser, ground):
            greater.mass -= 1/greater.mass
            lesser.mass -= 1/greater.mass
def sort(collisions):
    names = []
    finalList = []
    for collision in collisions:
        if collision:
            if [collision[0], collision[1]] not in names and [collision[1], collision[0]] not in names:
                names.append([collision[0], collision[1]])
                finalList.append(collision)
    return finalList
        

class physicsObject:
    def __init__(self, pos, length, height, mass):
        self.pos = pos
        self.length = length
        self.height = height
        self.mass = mass
        self.energy = [0, 0]
        self.acceleration = []
        self.minMax()
                    
    def doGravity(self, gravity_strength):
        self.move([0, gravity_strength*self.mass])

    def debug(self):
        print(f"Position: {self.pos}\nSpeed: {self.energy}\nVertices: {self.vertices()}\nObject: {self}\nMass: {self.mass}\n---------------")
    
    def debugAnchor(self, name):
        try:
            if self.name == name:
                ""
        except:
            ""
    
    def vertices(self, useSpeed = True):
        if useSpeed:
            x = self.pos[0]+(self.energy[0]/self.mass)
            y = self.pos[1]+(self.energy[1]/self.mass)
        else:
            x = self.pos[0]
            y = self.pos[1]
        distanceX = self.length/2
        distanceY = self.height/2
        list_ = []
        list_.append([x+distanceX, y+distanceY])
        list_.append([x-distanceX, y+distanceY])
        list_.append([x-distanceX, y-distanceY])
        list_.append([x+distanceX, y-distanceY])
        return list_
    def minMax(self):
        vertices = self.vertices()
        self.minX = vertices[1][0]
        self.maxX = vertices[0][0]
        self.minY = vertices[2][1]
        self.maxY = vertices[0][1]
    def getCollisions(self, opponents):
        for opponent in opponents:
            opponent.minMax()
        for vertex in self.vertices():
            for opponent in opponents:
                if opponent != self:
                    if (vertex[0] <= opponent.maxX and vertex[0] >= opponent.minX) and (vertex[1] <= opponent.maxY and vertex[1] >= opponent.minY):
                        return [self, opponent, vertex]
        return []
    def getCollisionsWithoutSpeed(self, opponents):
        for opponent in opponents:
            opponent.minMax()
        for vertex in self.vertices(False):
            for opponent in opponents:
                if opponent != self:
                    if (vertex[0] <= opponent.maxX and vertex[0] >= opponent.minX) and (vertex[1] <= opponent.maxY and vertex[1] >= opponent.minY):
                        return [self, opponent, vertex]
    def getSideHit(self, point):
        slopeToEdge = self.height/self.length
        xDistance = point[0] - self.pos[0]
        yDistance = point[1] - self.pos[1]
        try:
            slopeToPoint = yDistance/xDistance
            if abs(slopeToPoint) > slopeToEdge:
                return "horizontal"
            else:
                return "vertical"
        except:
            return "horizontal"

    def applySpeed(self, resistence = AIR_RESISTENCE):
        if isinstance(self, ground):
            self.energy = [0, 0]
        self.pos = [self.pos[0] + (self.energy[0]/self.mass), self.pos[1] + (self.energy[1]/self.mass)]
        self.energy = [self.energy[0] * resistence, self.energy[1] * resistence]
    def move(self, vector):
        self.energy = [self.energy[0]+vector[0], self.energy[1]+vector[1]]
    def forceMove(self, vector):
        self.pos = [self.pos[0] + vector[0], self.pos[1] + vector[1]]
        
class ground(physicsObject):
    def __init__(self, pos, length, height):
        super().__init__(pos, length, height, 20)
                
