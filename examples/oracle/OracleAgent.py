#! python
from spade import *
import os, sys
import pygame
from pygame.locals import *
import time
import math


if not pygame.font:print 'Warning, fonts disabled'
if not pygame.mixer:print 'Warning, sound disabled'

# Reference to the global robot rendering method
renderRobot = None

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print "Cannot load sound: ", message
	return NoneSound()
    return sound

def load_image(name, colorkey=None):
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print "Cannot load image:", name
		raise SystemExit, message
	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image, image.get_rect()
      
class Fist(pygame.sprite.Sprite):
    """moves a clenched fist on the screen, following the mouse"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image("fist.bmp", -1)
        #self.image, self.rect = load_image("foot.jpg", -1)
        self.punching = 0

    def update(self):
        "move the fist based on the mouse position"
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos
        if self.punching:
            self.rect.move_ip(5, 10)

    def punch(self, target):
        "returns true if the fist collides with the target"
        if not self.punching:
            self.punching = 1
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)

    def unpunch(self):
        "called to pull the fist back"
        self.punching = 0

class Robot(pygame.sprite.Sprite):
    """Robot sprite"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
    	self.image, self.rect = load_image("robot.png", -1)
	self.x = 0
	self.y = 0
	
    def setPos(self, x, y):
    	self.x = x
	self.y = y
	self.rect.topleft = x, y

    def getPos(self):
    	return self.x, self.y
    	
	
    #def update(self):
    #	pass

class Target(pygame.sprite.Sprite):
    """Target sprite"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
    	self.image, self.rect = load_image("target.png", -1)
	self.x = 0
	self.y = 0
	
    def setPos(self, x, y):
    	self.x = x
	self.y = y
	self.rect.topleft = x, y

    def getPos(self):
    	return self.x, self.y
    	
	
    #def update(self):
    #	pass

class Chimp(pygame.sprite.Sprite):
    """moves a monkey critter across the screen. it can spin the
       monkey when it is punched."""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image('p2dx.jpg', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 10
        self.move = 9
        self.dizzy = 0

    def update(self):
        "walk or spin, depending on the monkeys state"
        if self.dizzy:
            self._spin()
        else:
            self._walk()

    def _walk(self):
        "move the monkey across the screen, and turn at the ends"
        newpos = self.rect.move((self.move, 0))
        if self.rect.left < self.area.left or \
            self.rect.right > self.area.right:
            self.move = -self.move
            newpos = self.rect.move((self.move, 0))
            self.image = pygame.transform.flip(self.image, 1, 0)
        self.rect = newpos

    def _spin(self):
        "spin the monkey image"
        center = self.rect.center
        self.dizzy = self.dizzy + 12
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect()
        self.rect.center = center

    def punched(self):
        "this will cause the monkey to start spinning"
        if not self.dizzy:
            self.dizzy = 1
            self.original = self.image
 
    
class OracleAgent (Agent.Agent):
  class SubscriberBehaviour(Behaviour.Behaviour):
    """Behaviour that handles the subscription and unsubscription to games"""
    def __init__(self):
	Behaviour.Behaviour.__init__(self)
	print "Subscriber - initialized"

    def _process(self):
	msg = self._receive(True)
        sender = msg.getSender()
        print "Subscriber - arrived: " + str(sender)
	# FD - subscribe protocol
	if sender in self.myAgent.subscribers:
		# Already subscribed - refuse
		msg.setPerformative('refuse')
	else:
		# New subscriber
		self.myAgent.subscribers.append(sender)
		msg.setPerformative('agree')
	
	# Set sender and receiver
        msg.setSender(self.myAgent.getAID())
        msg.removeReceiver(self.myAgent.getAID())
        msg.addReceiver(sender)
	self.myAgent.send(msg)

	time.sleep(1)

  class OracleBehaviour(Behaviour.Behaviour):
    """Behaviour that provides advice to the players"""
    def __init__(self):
	Behaviour.Behaviour.__init__(self)


    def onStart(self):
	self.coords=[]
	x = [-1,0,0,18.5,39.5,52.5,60.5,78,78,60.5,39.5,25.5,18.5,79]
	y = [ 3,7,0,0,   0,   0,   0,   0, 7, 7,   7,   7,   7,   3 ]
	for i in range(0,len(x)):
		self.coords.append((x[i],y[i]))

	del x
	del y
	import random
	self.target = self.coords[random.randint(0,len(self.coords)-1)]
	print "TARGET " + str(self.target)
	x,y = self.myAgent.coords2pygame(self.target[0],self.target[1])
	self.myAgent.renderer.target.setPos(x,y)

    def _process(self):
	global renderRobot

	msg = self._receive(True)
        sender = msg.getSender()
        print "Supplicant - arrived: " + str(sender)
	agreed = False
	# FD - query protocol
	if sender in self.myAgent.subscribers:
		# Subscribed supplicant - agree
		msg.setPerformative('agree')
		agreed = True
		# render position
		cont = msg.getContent()
		cont = cont.split()

		x,y = self.myAgent.coords2pygame(int(cont[0]),int(cont[1]))
		renderRobot(x,y)

		#distancia euclidea
		d1 = math.pow((int(cont[0])-self.target[0]),2)
		d2 = math.pow((int(cont[1])-self.target[1]),2)
		dist = math.sqrt(abs(d1+d2))
	else:
		msg.setPerformative('refuse')

	# Set sender and receiver
	msg.setSender(self.myAgent.getAID())
        msg.removeReceiver(self.myAgent.getAID())
        msg.addReceiver(sender)
	self.myAgent.send(msg)
	
	if agreed:
		msg.setPerformative("inform-result")
		msg.setContent(str(dist))  #  Hard-coded
		self.myAgent.send(msg)

	time.sleep(0.15)



  class RendererBehaviour (Behaviour.PeriodicBehaviour):
    def __init__ (self, period):
    	Behaviour.PeriodicBehaviour.__init__ (self, period)
	self.initialized = False
 
    	#def pygame_setup(self):
	global renderRobot

	# Master switch for the monkey game
	self.monkey_game = False
	pygame.init()
	self.screen = pygame.display.set_mode ((1190, 321))
	pygame.display.set_caption ("Robot Navigator")
	pygame.mouse.set_visible (1)
	self.background = pygame.Surface (self.screen.get_size ())
	self.background = self.background.convert()
	self.background, otracosa = load_image ("dsic.jpg")
	#background.fill((250, 250, 250))
	if pygame.font:
		self.font = pygame.font.Font (None, 36)
		self.text = self.font.render ("DSIC Robot Navigator", 1, (10, 10, 10))
		self.textpos = self.text.get_rect ()
		self.textpos.centerx = self.background.get_rect ().centerx
		self.background.blit (self.text, self.textpos)
	self.screen.blit(self.background, (0, 0))
	pygame.display.flip ()
	self.whiff_sound = load_sound ('whiff.wav')
	self.punch_sound = load_sound ('punch.wav')
	self.chimp = Chimp ()
	self.fist = Fist ()
	self.robot = Robot ()
	self.target = Target()
	if self.monkey_game:
		self.allsprites = pygame.sprite.RenderPlain ((self.fist, self.chimp, self.robot, self.target))
	else:
		self.allsprites = pygame.sprite.RenderPlain ((self.robot,self.target))
	self.clock = pygame.time.Clock()
	self.robot.setPos(10, 10)
	self.initialized = True
	renderRobot = self.renderRobot  # Set global renderer	
	print "Behaviour: pygame_setup: done!"

    def renderRobot(self, x, y):
	print "renderRobot: ", x, y
	self.robot.setPos(int(x), int(y))

	
    def _onTick (self):
	if self.initialized == False:
		self.pygame_setup()
    	#self.clock.tick (60)
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			self.myAgent.stop()
			raise SystemExit
		elif event.type == KEYDOWN and event.key == K_ESCAPE:
			pygame.quit()
			self.myAgent.stop()
			raise SystemExit
		elif event.type == KEYDOWN and event.key == K_m:
			if self.monkey_game == False:
				self.monkey_game = True
				self.allsprites = pygame.sprite.RenderPlain ((self.fist, self.chimp, self.robot))
				pygame.mouse.set_visible (0)
			else:
				self.monkey_game = False
				self.allsprites = pygame.sprite.RenderPlain ((self.robot))
				pygame.mouse.set_visible (1)
		elif event.type == MOUSEBUTTONDOWN:
			if self.monkey_game:
				if self.fist.punch(self.chimp):
					self.punch_sound.play() #punch
					self.chimp.punched()
				else:
					self.whiff_sound.play() #miss
					#rx, ry = robot.getPos()
					#robot.setPos(rx+2, ry+2)
			self.mouse = pygame.mouse.get_pos()
			print "MOUSE ", self.mouse
			self.target.setPos(self.mouse[0], self.mouse[1])
		elif event.type == MOUSEBUTTONUP:
			self.fist.unpunch()

	self.allsprites.update()
	self.screen.blit(self.background, (0, 0))
	self.allsprites.draw(self.screen)
	pygame.display.flip()
	#time.sleep (0.01) 
			
  def __init__ (self, agentjid, passwd):
  	Agent.Agent.__init__(self, agentjid, passwd)

  def _setup (self):
	self.subscribers = []
	self.renderer = self.RendererBehaviour(0.01)

	ACLtemplate = Behaviour.ACLTemplate()
        ACLtemplate.setPerformative('subscribe')
        template = (Behaviour.MessageTemplate(ACLtemplate))
        self.addBehaviour(self.SubscriberBehaviour(), template)

	ACLtemplate2 = Behaviour.ACLTemplate()
        ACLtemplate2.setPerformative('query-ref')
        template2 = Behaviour.MessageTemplate(ACLtemplate2)
        self.addBehaviour(self.OracleBehaviour(), template2)

  	self.setDefaultBehaviour(self.renderer)

	"""
	ACLtemplate = Behaviour.ACLTemplate()
        ACLtemplate.setConversationId(msg.getConversationId())
        ACLtemplate.setSender(msg.getSender())
        template = (Behaviour.MessageTemplate(ACLtemplate))
	"""

  def coords2pygame(self, xcoords, ycoords):
		
	xpygame = (xcoords * 12.84)+ 81
	ypygame = 238 - ( ycoords * 11.71 )
		
	return xpygame, ypygame


if __name__ == "__main__":
	oagent = OracleAgent("oracle@tatooine.dsic.upv.es", "secret")
	oagent.start()
	try:
		while True:
			time.sleep(0.5)
	except:
		oagent.stop()
