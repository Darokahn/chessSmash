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
    menu screen [x] [] []
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

def initiateScreen():
    pygame.init()
    screen = pygame.display.set_mode(WINDOWSIZE)
    screen.fill((255, 255, 255))
    return screen

def gameCycle(screen, all_objects, framesLeft):
    knightPositions = { # initiate a dictionary for knight positions to be stored in
        "white": [],
        "black": []
        }
    global SOUNDS
    
    particles = [] #initiate a list for particle objects to be stored in
    
    physicsObjects = all_objects["objects"] #sets the physics objects in the dictionary of all object types to a variable for easier and more legible acces
    white = all_objects["white"] #sets a list of objects to be processed as white pieces
    black = all_objects["black"] #does the same for black pieces
    visualObjects = all_objects["visual"] #sets objects to be rendered

    collisions = [] # initiates a list of collisions
    for i in physicsObjects: #messy FOR loop. assigns the "opposite team" value to every instance of physics objects, but also applies gravity. knight and platform exceptions feel unnecessary; how can I make data flow better so that these do not inherently need to be exception?
        if not isinstance(i, platform):
            oppositeTeam = "black" if i.team == "white" else "white"
        if not isinstance(i, knight):
            i.doGravity(0.1)
        else:
            knightPositions[i.team].append(i.pos) #adds knight positions to a list so that values can be appended
        collisions.append(i.getCollisions(all_objects[oppositeTeam]))
    collisions = physics.sort(collisions) #cleans up collisions so no objects collide with themselves and so that no collisions are registered twice
    newParticles, didCollide = physics.doCollisions(collisions) #gets a list of new particles and a boolean whether any collisions happened. This is bad; instead, a list of colliding objects should be returned and particles should be handled outside the physics module.
    if didCollide:
        pygame.mixer.Sound.play(SOUNDS["hit1"]) #plays a sound if there were any collisions.
    particles += newParticles #adds the new particles to the list defined at the beginning. These are not particle objects yet; they are tuples containing the arguments required to create particle objects.
    for i in particles:
        all_objects["particles"] += [particle(*i)] #particles are now created as objects and added to the master object list.
    remove = [] #initializes a list of particles to be removed, since they have expired. If they are removed inside the FOR loop, the size of the loop will change as it runs and cause issues. I think it might throw an exception, but I don't remember.
    for i in all_objects["particles"]: 
        if i.simulateParticle() == "remove":
            remove.append(i)
    for i in remove: #removes the list of particles.
        all_objects["particles"].remove(i)
    for i in physicsObjects: #checks each object in physicsobjects to see if it is inside one of its team's knight auras, and then applies speed.
        resistence = 0.99 #sets air resistence to its default value
        if not isinstance(i, platform): #another bad exception case. How can data flow so that platforms are inherently not included?
            for knightPos in knightPositions[i.team]:
                if math.sqrt((i.pos[0]-knightPos[0])**2 + ((i.pos[1]-knightPos[1])**2)) <= (125/2)*3:
                    resistence = 0.95
        i.applySpeed(resistence)
    render(screen, all_objects) #places all objects on the screen
    framesLeft -= 1
    return framesLeft

def turn(screen, objects):
    for team in [objects["white"], objects["black"]]: #iterates over both teams and nets iteration over each piece per team
        for piece in team:
            if not isinstance(piece, platform): #executes only if the piece is not a platform. This should be unnecessary, as there should be no reason for a platform to be in either white or black.
                gradient_scale = 0 #initializes a variable to be used much later, which will provide a point on a scale from red to gray for the knight function.
                playerInput = False
                while not playerInput: #initiates a while loop that waits for a player input.
                    if not isinstance(piece, knight): #an exception that handles the fact that knights move differently to other pieces.
                        vector, magnitude = piece.getMagnitude() #a function that calculates a piece's potential velocity based on the mouse's direction and their "highpoints". Returns both a rectangular vector and a raw magnitude. This is sub-optimal but may end up being ignored.
                        for event in pygame.event.get(): #potential actions the player can take. Space skips their turn, and left clicking causes their potential velocity to be actuated. It breaks the loop by setting playerInput to be true, and plays a sound effect.
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_SPACE:
                                    playerInput = True
                            if pygame.mouse.get_pressed()[0]:
                                piece.move([vector[0]*piece.strength, vector[1]*piece.strength])
                                playerInput = True
                                pygame.mixer.Sound.play(SOUNDS["hit2"])
                        magnitude = -(1/10)*(magnitude - 10)**2 + 10 #adjusts magnitude to a curve so that lower values raise the magnitude faster. Appears to come slightly too late in the code, since it does not affect color in this position.
                        try: #defines a shake factor for the indicator dot, based once again on magnitude. Higher magnitudes make a higher vibration amplitude.
                            shake = [random.randrange(0, round(magnitude)*10), random.randrange(0, round(magnitude)*10)]
                            shake = [shake[0]/50, shake[1]/50]
                            verticalShake = random.randrange(-round(magnitude)*10, round(magnitude)*10)
                            verticalShake /= 20
                        except:
                            shake = [0, 0]
                            verticalShake = 0
                        color = to_color(red_green_balance(magnitude)) #turns the (255, 255, 255) color format returned by red_green_balance() into a useable '#ffffff' color format
                        vector = physics.get_vector_shrunk(piece.pos, pygame.mouse.get_pos(), piece.height+verticalShake) #defines a vector for the dot to be placed at from the current player.
                        render(screen, objects, f"""pygame.draw.circle(screen, "#000000", {[piece.pos[0]+vector[0]+shake[0], piece.pos[1]+vector[1]+shake[1]]}, 14, 0); pygame.draw.circle(screen, '{color}', {[piece.pos[0]+vector[0]+shake[0], piece.pos[1]+vector[1]+shake[1]]}, 10, 0)""")
                        #^^ renders the screen, with an additional argument that is just two lines of code that will be handled by the render() function to add in the circles without any unnecessary complication since the dot does not need to be an object.
                    elif isinstance(piece, knight): #handles the exception that a knight is being used by using a completely different ruleset.
                        mousePos = mouse_position() #sets a mouse position for easier access and to reduce repetitive calling of the mouse_position() function in the future.
                        vectorPosition = [piece.pos[0] - mousePos[0], piece.pos[1] - mousePos[1]] #defines a vector from the knight's position to the mouse.
                        angle = physics.vector_to_angle(vectorPosition) #derives an angle from that vector.
                        angle = angle - 180 #the angle needs to be adjusted... for some reason. I'm pretty sure the function should just work, but this adjustment is necessary for it to behave as intended.
                        if angle < 0:
                            angle = 360 + angle #corrects the angle to reside in the range of 0-360 after subtracting 180.
                        teleport = closest(angle, piece.highPoints) #finds the closest high point, and snaps the knight's potential teleport destination directly there.
                        teleport = polar_to_rect(teleport, 200)
                        if gradient_scale > 0: #subtracts from a gradient scale that determines a point on a gradient from red to gray. This means that after setting the color to gray, it will quickly return back to red.
                            gradient_scale -= 1
                        color1 = (255, 0, 0) #uses a percent value to return a color between color1 and color2. Very useful; should be its own function for both code readability and implementation elsewhere.
                        red, green, blue = color1
                        color2 = (128, 128, 128)
                        percent = (gradient_scale * 2)/100
                        differenceRed = percent*(color2[0] - color1[0])
                        differenceGreen = percent*(color2[1] - color1[1])
                        differenceBlue = percent*(color2[2] - color1[2])
                        red += differenceRed
                        green += differenceGreen
                        blue += differenceBlue
                        
                        for event in pygame.event.get(): #if the mouse is pressed, spawns an invisible, collisionless knight object to test whether the knight will collide with an enemy at that position. If not, it instantly teleports the knight. If so, it sets gradient_scale to 50 so that the indicator dot shakes and turns gray for about half a second.
                            if pygame.mouse.get_pressed()[0]:
                                test = knight([piece.pos[0]+teleport[0], piece.pos[1]+teleport[1]], piece.team)
                                oppositeTeam = "black" if test.team == "white" else "white"
                                if not test.getCollisions(objects[oppositeTeam]):
                                    pygame.mixer.Sound.play(SOUNDS["warp"])
                                    piece.pos = [piece.pos[0]+teleport[0], piece.pos[1]+teleport[1]]
                                    playerInput = True
                                else:
                                    gradient_scale = 50
                                del test
                                
                        
                        shake = [0,0]
                        color = to_color([red, green, blue])
                        try:
                            shake = [random.randrange(0, round(gradient_scale)*10), random.randrange(0, round(gradient_scale)*10)]
                            shake = [shake[0]/50, shake[1]/50]
                        except ValueError:
                            shake = [0, 0]
                        
                        render(screen, objects, f"""pygame.draw.circle(screen, "#000000", {[piece.pos[0]+teleport[0]+shake[0], piece.pos[1]+teleport[1]+shake[1]]}, 14, 0); pygame.draw.circle(screen, '{color}', {[piece.pos[0]+teleport[0]+shake[0], piece.pos[1]+teleport[1]+shake[1]]}, 10, 0)""")
                    
def polar_to_rect(angle, magnitude):
    x = math.cos(radian(angle))
    y = math.sin(radian(angle))
    x *= magnitude
    y *= magnitude
    return [x, y]
                    
def addToLists(obj, lists):
    for i in lists:
        i.append(obj)
            
def loadObjects(filename = None):
    background = []
    objects = []
    white = []
    black = []
    visual = []
    buttons = []
    if filename:
        file = open(filename, "r")
        dictionary = {"physicsObjects": objects,
                      "white": white,
                      "black": black,
                      "visual": visual,
                      "camera": camera(),
                      "background": [background],
                      "particles": [],
                      "gravityObjects": [],
                      "movingObjects": [],
                      "platforms": [],
                      "buttons": []
                      }
        for line in file.read().split("\n"):
            eval(line)
        return dictionary
    else:
        #here, I can directly modify which objects the game starts with by modifying code.
        background = sprite([500, 350], 1000, 700, "chess-garden.png")
        addToLists(background, [visual])
        addToLists(knight([300, 250], "white"), [objects, visual, white])
        addToLists(queen([100, 100], "white"), [objects, visual, white])
        addToLists(pawn([700, 100], "white"), [objects, visual, white])
            
        addToLists(platform([500, 350], 300, 100), [objects, visual])
        dictionary = {"physicsObjects": objects,
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
                      }
        return dictionary
    
def start():
    global menuLoad
    menuLoad = False
    
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
            
def main(fps):
    screen = initiate()
    objects = loadObjects("saves/menu.py")
    framesLeft = 0
    global menuLoad
    menuLoad = True
    is_in_button = 0
    while menuLoad == True:
        menu(screen, objects)
    objects = loadObjects("saves/level.py")
    while RUNNING == True:
        while framesLeft > 0:
            last_cycle = time.time()
            if time.time() - last_cycle < 1/fps:
                time.sleep(0.5/fps)
            framesLeft = gameCycle(screen, objects, framesLeft)
            
        framesLeft = 300
        for i in objects["objects"]:
            i.energy = [0, 0]
        turn(screen, objects)

if __name__ == "__main__":
    c1 = control("saves/level.py")
    c1.main()
