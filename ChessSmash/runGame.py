#note to self -- the height for each pawn in the background overlay is 73 pixels
#important -- credit zapsplat
"""
    To Do:
    platforms [x]
    particles [x]
    sound effects [x]
    queens [x]
    kings [x]
    knights [x]
    damage [x]
    file handling [x]
    menu screen [] [] []
    CLEAN UP CODE []
    gameplay loop []
    online gameplay []
    touch up physics []
    camera zoom {}
    
    messy functions:
    -gameCycle
    -Turn (INCURABLY BAD)
    -render
    
"""
import physics
import time
import pygame
import math
import random
WINDOWSIZE = [1000, 700]
class sprite:
    def __init__(self, pos, length, height, sprite, surface = None):
        self.pos = pos
        self.length = length
        self.height = height
        if isinstance(self, particle):
            ""
        if not surface:
            self.loadImage(f"images/{sprite}")
        else:
            self.sprite = surface
    def loadImage(self, directory, customAspectRatio = False):
        try:
            self.sprite = pygame.image.load(directory)
        except:
            self.sprite = pygame.image.load("images/default.png").convert()
        if customAspectRatio:
            base = self.length
            ratio = customAspectRatio[1] / customAspectRatio[0]
            height = base * ratio
            self.sprite = pygame.transform.scale((self.sprite), (base, height))
        else:
            self.sprite = pygame.transform.scale((self.sprite), (self.length, self.height))
            
class particle(sprite):
    def __init__(self, pos, length, height, sprite, expiry, speed, surface = None):
        super().__init__(pos, length, height, sprite, surface)
        self.expiry = expiry
        self.speed = speed
    def simulateParticle(self):
        self.pos = [self.speed[0]+self.pos[0], self.speed[1]+self.pos[1]]
        self.expiry -= 1
        if self.expiry <= 0:
            return True
        
class control:
    
    """
    {"physicsObjects": objects,
      "white": white,
      "black": black,
      "visual": visual,
      "camera": camera(),
      "background": [background],
      "particles": [],
      "gravityObjects": [],
      "movingObjects": [],
      "platforms": [],
      "buttons": [],
      "indicator": None
      }
    """
    
    def __init__(self, filename):
        pygame.mixer.init()
        self.globals = {
            "gravity": 0.1,
            "windowsize": [1000, 700],
            "sounds": {
                "warp": pygame.mixer.Sound("music/warp.mp3"),
                "hit1": pygame.mixer.Sound("music/hit.wav"),
                "hit2": pygame.mixer.Sound("music/hit1.wav"),
                "hit3": pygame.mixer.Sound("music/hit2.wav"),
                },
            "currentPhase": self.simulatePhysics,
            "objects": [],
            "screen": None,
            "currentSelection": None,
            "indicator": None,
            "running": True,
            "fps": 100
            }
        self.initiateScreen()
        self.loadObjects(filename)
    def loadObjects(self, filename):
        objects = []
        white = []
        black = []
        visual = []
        background = None
        file = open(filename, "r")
        dictionary = {"physicsObjects": objects,
                      "white": white,
                      "black": black,
                      "visual": visual,
                      "camera": camera(),
                      "background": background,
                      "particles": [],
                      "gravityObjects": [],
                      "movingObjects": [],
                      "platforms": [],
                      "buttons": []
                      }
        for line in file.read().split("\n"):
            eval(line)
        self.globals["objects"] = dictionary
    def initiateScreen(self):
        windowsize = self.globals["windowsize"]
        pygame.init()
        screen = pygame.display.set_mode(windowsize)
        screen.fill((255, 255, 255))
        self.globals["screen"] = screen
    def render(self, additional_effects = None):
        screen = self.globals["screen"]
        visualObjects = self.globals["objects"]["visual"]
        particles = self.globals["objects"]["particles"]
        screen.fill((255, 255, 255))
        for i in visualObjects:
            screen.blit(i.sprite, [i.pos[0]-(0.5*i.length), i.pos[1]-(0.5*i.height)])
            if isinstance(i, knight):
                screen.blit(i.aura, [i.pos[0]-((i.height*3)/2), i.pos[1]-((i.height*3)/2)])
        for i in particles:
            screen.blit(i.sprite, [i.pos[0]-(0.5*i.length), i.pos[1]-(0.5*i.height)])
        if additional_effects:
            for i in additional_effects.split("; "):
                eval(i)
        pygame.display.flip()
    def changePhase(self, phase):
        self.globals["currentPhase"] = self.phase
    def main(self):
        fps = self.globals["fps"]
        while self.globals["running"] == True:
            last_cycle = time.time()
            if time.time() - last_cycle < 1/fps:
                time.sleep(0.5/fps)
                self.globals["currentPhase"]()
        framesLeft = 300
    def doPlayerTurns(self, online = False):
        if online == True:
            pass
        else:
            for team in ("white", "black"):
                self.awaitInputs(team)
        self.changePhase(simulatePhysics)
    def awaitInputs(self, team):
        team = self.globals["objects"]["team"]
        for piece in team:
            playerInput = False
            while playerInput == False:
                piece.setSelectionPotential()
                piece.setIndicator()
                playerInput = getPlayerAction()
                self.render()
    def getPlayerAction(self, gamePhase):
        gamePhase = self.globals["currentPhase"]
        if gamePhase == doPlayerTurns:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return True
                if pygame.mouse.get_pressed()[0]:
                    self.applyPotential()
                    self.playSound("hit2")
                    return True
        elif gamePhase == simulatePhysics:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.globals["running"] = False
        return False
    def setSelectionPotential(self, selection):
        self.globals["currentSelection"] = {"obj": selection,
                                            "potential": selection.getMagnitude()}
    def applyPotential(self):
        obj = self.globals["currentSelection"]["obj"]
        potential = self.globals["currentSelection"]["obj"][0]
        obj.move(potential)
    def setIndicator(self):
        motherObject = self.globals["currentSelection"]["obj"]
        vector, magnitude = self.globals["currentSelection"]["potential"]
        vector = physics.get_vector_shrunk([0, 0], vector, motherObject.height*1.1)
        color = to_color(red_green_balance(magnitude))
        shake = [random.randint(-round(magnitude)*10, round(magnitude)*10), random.randint(-round(magnitude)*10, round(magnitude*10))]
        shake = [x / 50 for x in shake]
        position = [motherObject.pos[0]+vector[0]+shake[0], motherObject.pos[1]+vector[1]+shake[1]]
        surface = pygame.Surface([36, 36], pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()
        pygame.draw.circle(surface, "#000000", [18, 18], 15)
        pygame.draw.circle(surface, color, [18, 18], 14, 0)
        indicator = particle(position, 36, 36, "", 2, [0, 0], surface)
        self.globals["objects"]["particles"].append(indicator)
        
    def generateParticle(self, length, height, sprite, expiry, speedRange):
        start, stop = speedRange
        start *= 100
        stop *= 100
        if range(start, stop):
            speed = (random.randrange(start, stop)/100, random.randrange(start, stop)/100)
        newParticle = particle(pos, length, height, sprite, expiry, speed)
        self.globals["objects"]["particles"].append(newParticle)
    def playSound(self, sound):
        toPlay = self.globals["sounds"][sound]
        pygame.mixer.Sound.play(toPlay)
    def simulatePhysics(self):
        self.doGravity()
        self.collisionControl()
        self.doSpeedWithKnights()
        self.handleParticles()
        self.render()
        self.globals["framesLeft"] -= 1
        if self.globals["framesLeft"] <= 0:
            self.globals["framesLeft"] = 300
            self.changePhase(doPlayerTurns)
        self.getPlayerAction()
    def handleParticles(self):
        particles = self.globals["objects"]["particles"][:]
        for particle in particles:
            if particle.simulateParticle():
                self.globals["objects"]["particles"].remove(particle)
    def collisionControl(self):
        white = self.globals["objects"]["white"]
        black = self.globals["objects"]["black"]
        platforms = self.globals["objects"]["platforms"]
        collisions = []
        for piece in white:
            collisions.append(piece.getCollisions(black))
            collisions.append(piece.getCollisions(platforms))
        for piece in black:
            collisions.append(piece.getCollisions(white))
            collisions.append(piece.getCollisions(platforms))
        collisions = physics.sort(collisions)
        physics.doCollisions(collisions)
        for collision in collisions:
            vector = physics.get_vector_shrunk(collision[0].pos, collision[1].pos, collision[0].length)
            position = [collision[0].pos+vector[0], collision[1].pos+vector[1]]
            self.generateParticle(40, 40, "dust.png", 40, (-1, 1))
        if collisions:
            self.playSound("hit1")
    def doGravity(self):
        gravityObjects = self.globals["objects"]["gravityObjects"]
        gravity = self.globals["gravity"]
        for obj in gravityObjects:
            obj.move([0, gravity])
    def doSpeedWithKnights(self):
        whiteKnights = []
        blackKnights = []
        white = self.globals["objects"]["white"]
        black = self.globals["objects"]["black"]
        for piece in white:
            if isinstance(piece, knight):
                whiteKnights.append(piece)
        for piece in black:
            if isinstance(piece, knight):
                blackKnights.append(piece)
        for piece in white:
            resistence = 0.99
            for knight in whiteKnights:
                position = piece.pos
                knightPos = knight.pos
                x = knightPos[0] - position[0]
                y = knightPos[1] - position[1]
                distance = math.sqrt((x**2)+(y**2))
                if distance <= knight.range:
                    resistence = 0.95
            piece.applySpeed(resistence)
        for piece in black:
            resistence = 0.99
            for knight in blackKnights:
                position = piece.pos
                knightPos = knight.pos
                x = knightPos[0] - position[0]
                y = knightPos[1] - position[1]
                distance = sqrt((x**2)+(y**2))
                if distance <= knight.range:
                    resistence = 0.95
            piece.applySpeed(resistence)
            
            
class camera: #unused for now. See line 18.
    def __init__(self):
        self.pos = [500, 350]
        self.zoom = 1
    def move(self, vector):
        self.pos[0] += self.vector[0]
        self.pos[1] += self.vector[1]
            
class piece(physics.physicsObject, sprite):
    def __init__(self, pos, length, height, mass, team, highPoints, strength):
        super().__init__([pos[0], pos[1]], length, height, mass)
        self.team = team
        self.highPoints = highPoints
        self.strength = strength
    def getMagnitude(self):
        mousePosition = pygame.mouse.get_pos()
        mousePosition = (mousePosition[0], mousePosition[1])
        slope = [self.pos[0]-mousePosition[0], self.pos[1]-mousePosition[1]]
        angle = physics.vector_to_angle(slope)
        distance = abs(closest(angle, self.highPoints)-angle)
        if distance > 45:
            distance = 45
        curve = (distance-45)**2
        magnitude = 10/2025*(curve)
        if magnitude > 10:
            magnitude = 10
        elif magnitude < 1.5:
            magnitude = 1.5
        if isinstance(self, king):
            magnitude = 2
        return physics.get_vector_shrunk(self.pos, mousePosition, magnitude*self.strength), magnitude #THIS IS BAD. I SHOULD FIX THE DATA STRUCTURE SUCH THAT I DO NOT NEED TO RETURN THE VECTOR AND ITS MAGNITUDE AS A TUPLE, BUT HAVE NOT DONE SO YET.

class queen(piece):
    def __init__(self, pos, team):
        super().__init__(pos, 150, 150, 25, team, range(0, 361, 45), 5)
        if self.team == "black":
            self.loadImage("images/BlackQueen.png", [1, 1])
        elif self.team == "white":
            self.loadImage("images/WhiteQueen.png", [1, 1])
            
class king(piece):
    def __init__(self, pos, team):
        super().__init__(pos, 150, 150, 25, team, range(0, 361, 45), 5)
        if self.team == "black":
            self.loadImage("images/BlackKing.png", [1, 1])
        elif self.team == "white":
            self.loadImage("images/WhiteKing.png", [1, 1])

class rook(piece):
    def __init__(self, pos, team):
        super().__init__(pos, 100, 100, 20, team, [0, 90, 180, 270, 360], 3)
        if self.team == "black":
            self.loadImage("images/BlackRook.png", [1, 1])
        elif self.team == "white":
            self.loadImage("images/WhiteRook.png", [1, 1])

class bishop(piece):
    def __init__(self, pos, team):
        super().__init__(pos, 100, 100, 15, team, [45, 135, 225, 315, 405], 3)
        if self.team == "black":
            self.loadImage("images/BlackBishop.png", [1, 1])
        elif self.team == "white":
            self.loadImage("images/WhiteBishop.png", [1, 1])
            
class knight(piece):
    def __init__(self, pos, team):
        super().__init__(pos, 100, 100, 20, team, [26.56, 63.43, 116.56, 153.43, 206.56, 243.43, 296.56, 333.43, 386.56], 0.8)
        self.aura = load_image("images/aura.png", [self.height*3, self.height*3])
        self.loadImage(f"images/{team.capitalize()}Knight.png", [1, 1])
        self.range = (self.height*3)/2

class pawn(piece):
    def __init__(self, pos, team):
        super().__init__(pos, 75, 75, 10, team, [45, 135], 2)
        if self.team == "black":
            self.loadImage("BlackPawn.png", [1, 1])
        elif self.team == "white":
            self.loadImage("images/WhitePawn.png", [1, 1])
            
class platform(physics.ground, sprite):
    def __init__(self, pos, length, height):
        super().__init__(pos, length, height)
        image = random.choice(["black", "white"])
        self.platformRender()
    def platformRender(self, color = random.choice(["black", "white"])):
        mainPlatform = pygame.image.load(f"images/platformMiddle{color}.png")
        mainPlatform = pygame.transform.scale(mainPlatform, [self.length, self.height])
        platformRight = pygame.image.load(f"images/platformRight{color}.png")
        platformRight = pygame.transform.scale(platformRight, [self.height/8, self.height])
        platformLeft = pygame.image.load(f"images/platformLeft{color}.png")
        platformLeft = pygame.transform.scale(platformLeft, [self.height/8, self.height])
        mainPlatform.blit(platformLeft, [0, 0])
        mainPlatform.blit(platformRight, [self.length - (self.height/9), 0])
        self.sprite = mainPlatform
        
class button(sprite):
    def __init__(self, pos, length, height, sprite, action):
        super().__init__(pos, length, height, sprite)
        self.action = action
        self.minMax()
        self.dark = pygame.Surface.copy(self.sprite)
        s = pygame.Surface([1000, 1000])
        s.set_alpha(30)
        pygame.Surface.fill(s, (0, 0, 0))
        self.dark.blit(s, [0,0])
        self.bright = pygame.Surface.copy(self.sprite)
    def minMax(self):
        vertices = self.vertices()
        self.minX = vertices[1][0]
        self.maxX = vertices[0][0]
        self.minY = vertices[2][1]
        self.maxY = vertices[0][1]
    def vertices(self):
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
    def mouseIn(self):
        mouse = mouse_position()
        if (mouse[0] > self.minX and mouse[0] < self.maxX) and (mouse[1] > self.minY and mouse[1] < self.maxY):
            return True
        else:
            return False
    def darken(self):
        self.sprite = self.dark
    def brighten(self):
        self.sprite = self.bright
        
        
def load_image(directory, customAspectRatio = False):
        try:
            sprite = pygame.image.load(directory)
        except:
            sprite = pygame.image.load("images/default.png").convert()
        if customAspectRatio:
            base, height = customAspectRatio
            sprite = pygame.transform.scale((sprite), (base, height))
        return sprite

def mouse_position():
    return pygame.mouse.get_pos()
            
def render(screen, all_objects, additional_effects = None):
    visualObjects = all_objects["visual"]
    particles = all_objects["particles"]
    global WINDOWSIZE
    screen.fill((255, 255, 255))
    for i in visualObjects:
        screen.blit(i.sprite, [i.pos[0]-(0.5*i.length), i.pos[1]-(0.5*i.height)])
        if isinstance(i, knight):
            screen.blit(i.aura, [i.pos[0]-((i.height*3)/2), i.pos[1]-((i.height*3)/2)])
    for i in particles:
        screen.blit(i.sprite, [i.pos[0]-(0.5*i.length), i.pos[1]-(0.5*i.height)])
    if additional_effects:
        for i in additional_effects.split("; "):
            eval(i)
    pygame.display.flip()
    
def to_color(rgb):
    colorstring = "#"
    for color in rgb:
        color = round(color)
        if color > 255:
            color = 255
        if color < 0:
            color = 0
        color = hex(color)
        color = color.replace("0x", "")
        color = f"0{color}" if len(color) == 1 else color
        colorstring += color
    return colorstring

def get_gradient_color(color1, color2, gradient_scale):
    red, green, blue = color1
    percent = (gradient_scale)/100
    differenceRed = percent*(color2[0] - color1[0])
    differenceGreen = percent*(color2[1] - color1[1])
    differenceBlue = percent*(color2[2] - color1[2])
    red += differenceRed
    green += differenceGreen
    blue += differenceBlue
    return to_color([round(x) for x in (red, green, blue)])

def round(num):
    try:
        carry = str(num).split(".")
        carry = num - int(carry[0])
        if int(carry) < 0.5:
            return int(num-carry)
        else:
            return int(num-carry)+1
    except IndexError:
        return num
    
def red_green_balance(difference):
    red = 0
    green = 255
    blue = 0
    if difference > 5:
        difference -= 5
        difference *= 51
        red = 255
        green -= difference
    else:
        difference *= 51
        red += difference
    return (round(red), round(green), round(blue))
    
def to_rectangular(magnitude, angle):
    point = [math.cos(radian(angle)), math.sin(radian(angle))]
    return physics.get_vector_shrunk([0,0], point, magnitude)

def radian(angle):
    return angle * math.pi/180

def degree(angle):
    return angle * 180/math.pi
    
def closest(number, num_list):
    closest = num_list[0]
    for num in num_list:
        if abs(number-num) < abs(number-closest):
            closest = num
    return closest
 
def polar_to_rect(angle, magnitude):
    x = math.cos(radian(angle))
    y = math.sin(radian(angle))
    x *= magnitude
    y *= magnitude
    return [x, y]
                    
def addToLists(obj, lists):
    for i in lists:
        i.append(obj)
            
def menu(screen, objects):
    global is_in_button
    render(screen, objects)
    for i in objects["buttons"]:
        if i.mouseIn():
            i.darken()
            if is_in_button != i:
                pygame.mixer.Sound.play(SOUNDS["hit2"])
                is_in_button = i
        else:
            i.brighten()
            is_in_button = None
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                playerInput = True
        if pygame.mouse.get_pressed()[0]:
            for i in objects["buttons"]:
                if i.mouseIn():
                    eval(i.action)

if __name__ == "__main__":
    c1 = control("saves/level.py")
    c1.main()