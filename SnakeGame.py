#TODO add copyright and license info

from pygame import event

from Snake import *

class SnakeGame:
    def __init__(self, winWidth, winHeight):
        self.winWidth = winWidth
        self.winHeight = winHeight

        # instantiate players' snakes
        self.snake1 = Snake(15, 15, Dir.Right, 4)
        self.snakeAI = SnakeAI(30, 30, Dir.Right, 4)

        self.pellet = Pellet(winWidth - 1, winHeight - 1, 'yellow') 

        self.isDirChangeAllowed = True
        self.gameStateChanged = False
        self.tickNum = 0

    def processInput(self, direction):
        if self.isDirChangeAllowed:
            self.snake1.changeHeading(direction)
            self.isDirChangeAllowed = False
            self.gameStateChanged = True

    def tick(self):
        # move players' snakes
        self.snake1.move(self.pellet)
        #Snake.move(snake1) # an alternative way to call a particular object's method
        self.snakeAI.move(self.pellet)    
        
        # check if player's head is on a pellet. If so, consume it and create a new one
        if self.snake1.headX == self.pellet.posx and self.snake1.headY == self.pellet.posy:
            self.snake1.length += 1
            self.pellet = Pellet(self.winWidth - 1, self.winHeight - 1, fgcolor = 'yellow')
            self.snake1.grow()
            #s.sendto('Player 1 score:' + str(self.snake1.length), (HOST, lobbyPort))
        # (SnakeAI) check if player's head is on a pellet. If so, consume it and create a new one
        elif self.snakeAI.headX == self.pellet.posx and self.snakeAI.headY == self.pellet.posy:
            self.snakeAI.length += 1
            self.pellet = Pellet(self.winWidth - 1, self.winHeight - 1, 'yellow')
            self.snakeAI.grow()
            #s.sendto('SnakeAI score:' + str(self.snakeAI.length), (HOST, lobbyPort))

        # check if any snakes are colliding with any other snakes
        #if self.snake1.isColl((self.snake1.headX, self.snake1.headY)): # previous use of Snake.isColl()
        if self.snake1.isColl(self.snake1):
            print 'snake1 bit itself'     
        elif self.snake1.isColl(self.snakeAI):
            print 'snake1 ran into the other snake'     

        if self.snakeAI.isColl(self.snakeAI):
            print 'snakeAI bit itself'
        elif self.snakeAI.isColl(self.snake1):
            print 'snakeAI ran into the other snake'     

        #TODO check if any snakes have hit the edge
        #if ...

        self.isDirChangeAllowed = True
        self.tickNum += 1
