#TODO add copyright and license info

import os
import sys

import pygame
from pygame.locals import *
import pygcurse

from Snake import *

class SnakeGame:
    def __init__(self, winWidth, winHeight):
        self.winWidth = winWidth
        self.winHeight = winHeight

        # instantiate players' snakes
        self.snake1 = Snake(15, 15, Dir.Right, 4)
        self.snakeAI = SnakeAI(30, 30, Dir.Right, 4)

        self.pellet = Pellet(winWidth - 1, winHeight - 1, 'yellow') 

        # initiate pygame and pygcurse
        os.environ['SDL_VIDEO_CENTERED'] = '1' # center window in Windows
        pygame.init()
        self.win = pygcurse.PygcurseWindow(winWidth, winHeight, 'Snake')
        self.win.autoupdate = False # turn off autoupdate so window doesn't flicker

    def processInput(self):
        # process input queue
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    self.snake1.changeHeading(Dir.Up)
                elif event.key == K_DOWN:
                    self.snake1.changeHeading(Dir.Down)
                elif event.key == K_LEFT:
                    self.snake1.changeHeading(Dir.Left)
                elif event.key == K_RIGHT:
                    self.snake1.changeHeading(Dir.Right)

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

    def drawWindow(self):
        # clear the screen
        #win.erase() # this would be used instead but for a bug...
        self.win.fill(' ')

        # draw outside border
        #TODO

        # draw game data
        self.win.putchars("Score: " + str(self.snake1.length), 0, 0)

        #FIXME draw snakes and pellet (get positions from class)
        for pos in self.snake1.body:
            # pos is a tuple (x, y)
            self.win.putchars('O', pos[0], pos[1], fgcolor = self.snake1.fgcolor)

        for pos in self.snakeAI.body:
            self.win.putchars('O', pos[0], pos[1], self.snakeAI.fgcolor)

        # draw pellet
        self.win.putchar('+', self.pellet.posx, self.pellet.posy, self.pellet.fgcolor)

        # actually paint the window
        self.win.update()
