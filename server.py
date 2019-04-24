import PodSixNet.Channel
import PodSixNet.Server
from time import sleep

class ClientChannel(PodSixNet.Channel.Channel):

    def Network(self, data):
        print (data)

    def Close(self):
        self._server.close(self.gameid)

    def Network_placeCard(self, data):
		#cardNum
        cardNum = data["cardNum"]
		#player number (1 or 0)
        num=data["num"]
        self.gameid = data["gameid"]
        self._server.placeCard(cardNum, data, self.gameid, num)
		
		
class ServerECard(PodSixNet.Server.Server):
	def __init__(self, *args, **kwargs):
		PodSixNet.Server.Server.__init__(self, *args, **kwargs)
		self.games = []
		self.queue = None
		self.currentIndex=0

	channelClass = ClientChannel
	def Connected(self, channel, addr):
		print  ('new connection:', channel)
		if self.queue==None:
			self.currentIndex+=1
			channel.gameid=self.currentIndex
			self.queue=Game(channel, self.currentIndex)
		else:
			channel.gameid=self.currentIndex
			self.queue.player1=channel
			self.queue.player0.Send({"action": "startgame","player":0, "es":1, "gameid": self.queue.gameid})
			self.queue.player1.Send({"action": "startgame","player":1, "es":3, "gameid": self.queue.gameid})
			self.games.append(self.queue)
			self.queue=None
	def close(self, gameid):
		try:
			game = [a for a in self.games if a.gameid==gameid][0]
			game.player0.Send({"action":"close"})
			game.player1.Send({"action":"close"})
		except:
			pass

	def placeCard(self, cardNum, data, gameid, num):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].placeCard(cardNum, data, num)
	
	
	
	def tick(self):
		for game in self.games:
			# print('Board0=',game.board[0],'Board0=',game.board[1])
			if game.board[0] != None and game.board[1] != None:
				over = False
				game.countThrow += 1
				game.player0.Send({"action":"showBoard","c0":game.board[0], "c1":game.board[1]})
				game.player1.Send({"action":"showBoard","c0":game.board[1], "c1":game.board[0]})
				print("action:showBoard")
				bestCard = game.bestCard(game.board[0],game.board[1])
				if game.board[0] == game.board[1] :
					print('equal')
				elif bestCard == game.board[0]:
					game.player0.Send({"action":"win"})
					game.player1.Send({"action":"lose"})
					game.countRound += 1
				else:
					game.player1.Send({"action":"win"})
					game.player0.Send({"action":"lose"})
					game.countRound += 1
				game.board[0],game.board[1] = None,None
				
			
			if game.countRound >= 3:
				game.countRound = 0
				game.player0.Send({"action":"swapCards"})
				game.player1.Send({"action":"swapCards"})
				game.turn = 0 if game.turn else 1
        		game.player1.Send({"action":"yourturn", "torf":True if game.turn==1 else False})
        		game.player0.Send({"action":"yourturn", "torf":True if game.turn==0 else False})
				
					# game.board[0],game.board[1] = None,None
			# sleep(5)
			# game.player0.Send({"action":"initBoard"})
					# game.player1.Send({"action":"initBoard"})
				# if not game.countThrow or game.countThrow == 4:
				# 	game.player0.send({"action":"initBoard","value":True})
				# 	game.player1.send({"action":"initBoard","value":True})
				# 	if(game.countThrow==4): 
				# 		game.countThrow = 0
				# if(game.countSwap >= 1 and game.countRound >= 5):
				# 	sleep(1000000)
				# if game.countRound >= 5:
				# 	game.countThrow = 0
				# 	game.countRound = 0
				# 	game.countSwap = 1
		self.Pump()

class Game:
    def __init__(self, player0, currentIndex):
        self.countThrow = 0 
        self.countRound = 0
        self.countSwap = 0
		# whose turn (1 or 0)
        self.turn = 0
        #owner cards
        self.owner = [[False for x in range(2)] for y in range(4)] #used
        self.board = [None for x in range(2)]
        #initialize the players including the one who started the game
        self.player0=player0
        self.player1=None
        #gameid of game
        self.gameid=currentIndex
	
    def placeCard(self, cardNum, data, num):
		#make sure it's their turn
        if num==self.turn:
        	self.turn = 0 if self.turn else 1
        	self.player1.Send({"action":"yourturn", "torf":True if self.turn==1 else False})
        	self.player0.Send({"action":"yourturn", "torf":True if self.turn==0 else False})
        	
        	
        self.board[num] = cardNum
        print('Board0=',self.board[0],'Board1=',self.board[1])
        #send data and turn data to each player
        self.player0.Send(data)
        self.player1.Send(data)

    def bestCard(self, c1, c2):
        if abs(c1 - c2)==2: return 1
        elif c1>c2:
        	return c1
        else:
        	return c2	
		
host, port="127.0.0.1", 9413		
serverECard = ServerECard(localaddr=(host, int(port)))
print("E-Card Game developed by Yasoo@YassineQassar, find me on Github")
while True:
	serverECard.tick()
	sleep(0.0001)


