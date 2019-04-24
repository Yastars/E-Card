from PodSixNet.Connection import ConnectionListener, connection
from time import sleep
import pygame
from pygame.locals import *
import math




	



class ECardGame(ConnectionListener):
	def Network_yourturn(self, data):
    	#torf = short for true or false
	    self.turn = data["torf"]

	def Network_win(self, data):
		self.nextRound = True
		self.me += 1
	
	def Network_lose(self, data):
		self.nextRound = True
		self.otherplayer += 1

	def Network_swapCards(self, data):
		if self.es ==1:
			self.es = 3
			self.turn = False
		else:
			self.es = 1
			self.turn = True
		
	def Network_showBoard(self, data):
		# self.showBoard = True
		self.showBoard = True
		for x in range(4):
			# sleep(1)
			pygame.time.delay(100)
			print('sleepx',x)
		print('showBoard')

	def Network_startgame(self, data):
		self.running=True
		self.num=data["player"]
		self.gameid=data["gameid"]
		self.es = data["es"]
		self.initCards(self.es) # 1 for slave, 3 foremperor
	def Network_placeCard(self, data):
		#get attributes
		cardNum = data["cardNum"]
		#board other player 450, 170
		#board owner 450, 315
		#print(self.num,data['num'],cardNum)
		if data['num']==self.num:
			self.board[0]=cardNum
			# self.showCard(cardNum,450,315)
			print('I throwed A Card')
		else:
			self.board[1]=cardNum
			print('He throwed A Card')
			self.otherCounter -= 1
			# self.showCard(cardNum, 450, 170)

	def __init__(self):
		self.ownerCards = [[False for x in range(2)] for y in range(4)] #used
		self.board = [None for x in range(2)]
		self.otherCounter = 4
		self.gameid = None
		self.num = None
		self.running=False
		self.showBoard= False
		self.es = None
		self.me=0
		self.otherplayer=0
		self.didiwin=False
		self.nextRound = False

		self.justplaced=10
		pygame.init()
		width, height = 1000, 600
		self.screen = pygame.display.set_mode((width, height)) 	#initialize screen
		pygame.display.set_caption("E-Card Game")
		self.clock=pygame.time.Clock() 							#initialize pygame clock
		self.initGraphics()
		pygame.font.init()
		#init cards
		
		self.Connect(("127.0.0.1", 9413)) #Initialize PodSixNet Client

		self.running=False
		while not self.running:
			self.Pump()
			connection.Pump()
			sleep(0.01)
		#determine attributes from player #
		if self.num==0:
			self.turn=True
			# self.marker = self.greenplayer
			# self.othermarker = self.blueplayer
		else:
			self.turn=False
			# self.marker=self.blueplayer
			# self.othermarker = self.greenplayer

	def update(self):
		self.justplaced-=1
		#Pump server and client looking for new messages
		connection.Pump()
		self.Pump()
		self.clock.tick(60) #fps
		self.screen.fill(0) #clear screen
		mouse = pygame.mouse.get_pos()
		self.drawBoard(mouse)	#draw board
		
		for event in pygame.event.get():
			if event.type == QUIT: #quit if the quit button was pressed
				exit()


		if pygame.mouse.get_pressed()[0] and self.justplaced<=0 and self.turn==True and self.board[0]==None:
			self.throwCard(mouse)
			self.justplaced=10
		pygame.display.flip() #update screen
		
		if(self.showBoard):
			i=0
			while i<30:
				pygame.display.flip()
				pygame.time.delay(50)
				print(i)
				i += 1
			self.showBoard = False
			self.board = [None for x in range(2)]

		if(self.nextRound):
			self.nextRound = False
			self.ownerCards = [[False for x in range(2)] for y in range(4)] #used
			self.initCards(self.es)
			self.otherCounter = 4
			print('Next Round')





	def initGraphics(self):
		self.emperor=pygame.image.load("emperor.jpg")
		self.citizen=pygame.image.load("citizen.jpg")
		self.slave=pygame.image.load("slave.jpg")
		self.deck=pygame.image.load("deck.jpg")
		self.othersTurn=pygame.image.load("othersTurn.jpg")
		self.yourTurn=pygame.image.load("yourTurn.jpg")
		
		
	def drawBoard(self, mouse):
		#board other player 450, 170
		#board owner 450, 315
		#Show board
		if(self.showBoard):
			self.showCard(self.board[0], 450 ,315)
			self.showCard(self.board[1], 450 ,170)
		else:
			if(self.board[0]!= None):
				self.showCard(-1, 450 ,315)
			if(self.board[1]!= None):
				self.showCard(-1, 450 ,170) 
		self.screen.blit(self.deck, [50, 230]) #draw deck
		for x in range(self.otherCounter):
			self.screen.blit(self.deck, [240+(140*x), 5]) #draw other player's cards
		#self.screen.blit(self.emperor, [240, 465])	#draw emporer or slave
		for x in range(4):
			y = 0
			if(mouse[0]>240+(140*x)and mouse[0]<240+(140*x)+140 and mouse[1]>465 and mouse[1]<595):
				y = -20
			if(not self.ownerCards[x][1]):
				self.showCard(self.ownerCards[x][0],240+(140*x),465+y)
		self.screen.blit(self.yourTurn if self.turn else self.othersTurn, (130, 395))
		
		

		myfont = pygame.font.SysFont(None, 32)

        #create text surface
		myfont64 = pygame.font.SysFont(None, 64)
		myfont20 = pygame.font.SysFont(None, 20)

		scoreme = myfont64.render(str(self.me), 1, (255,255,255))
		scoreother = myfont64.render(str(self.otherplayer), 1, (255,255,255))
		scoretextme = myfont20.render("You", 1, (255,255,255))
		scoretextother = myfont20.render("Other Player", 1, (255,255,255))
		count = myfont20.render("Enjoy!", 1, (255,255,255))

		self.screen.blit(scoretextme, (800, 520))
		self.screen.blit(scoreme, (850, 530))
		self.screen.blit(scoretextother, (800, 52))
		self.screen.blit(scoreother, (850, 72))
		self.screen.blit(count, (72, 400))
		
		
		
		

	def initCards(self, es):
		self.ownerCards[0][0]=es # 1 slave  3 Emperor
		for x in range(3):
			self.ownerCards[x+1][0]=2
	
	
	
	
	#board = []
	
	def throwCard(self, mouse):
		for x in range(4):
				if(mouse[0]>240+(140*x)and mouse[0]<240+(140*x)+140 and mouse[1]>465 and mouse[1]<595)  and not self.ownerCards[x][1]:
					self.ownerCards[x][1] = True #make that card as used
					self.board[0] = self.ownerCards[x][0]
					print("Owner placed Card = ", self.ownerCards[x][0]," on board.")
					self.Send({"action": "placeCard", "cardNum":self.ownerCards[x][0], "gameid": self.gameid, "num": self.num})
					#board owner 450, 315



	def showCard(self, cardNum, x, y):
		if cardNum == 1:
			self.screen.blit(self.slave, [x, y])
		elif cardNum == 2:
			self.screen.blit(self.citizen, [x, y])
		elif cardNum == 3:
			self.screen.blit(self.emperor, [x, y])
		else:
			self.screen.blit(self.deck, [x, y])


	def bestCard(self, c1, c2):
		if abs(c1 - c2)==2: return 1
		elif c1>c2:
			return c1
		else:
			return c2
			
			
ECard_Game=ECardGame() #Main()
while 1:
    if ECard_Game.update() == 1:
        break
#ECard_Game.finished()