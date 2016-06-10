# -*- coding: utf-8 -*-

# *************************************************************************
#
#  This file is part of Snake-M.
#
#  Copyright © 2014 Mark Ross <krazkidd@gmail.com>
#
#  Snake-M is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Snake-M is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Snake-M.  If not, see <http://www.gnu.org/licenses/>.
#  
# *************************************************************************

import os
from time import time

import pygame
from pygame.locals import * # keyboard keys and stuff
import pygcurse

from Snake import *

class GameState:
    """Enum for Snake game state"""
    GAME_OVER = 1

class SnakeGame:
    def __init__(self, boardWidth, boardHeight, playersList):
        self.boardWidth = boardWidth
        self.boardHeight = boardHeight

        self.win = None
        
        snake1 = Snake(15, 15, Dir.Right, 4)
        #TODO if playersList is less than size of game, add robot players (to playersList, so the zip() works)

        self.snakes = zip(playersList, (snake1))

        self.pellet = Pellet(self.boardWidth - 1, self.boardHeight - 1, 'yellow') 

        self.gameStateChanged = False
        self.tickNum = 0
    # end __init__()

def startGame(self):    
    # initiate pygame and pygcurse
    os.environ['SDL_VIDEO_CENTERED'] = '1' # center window in Windows
    pygame.init()
    self.win = pygcurse.PygcurseWindow(WIN_WIDTH, WIN_HEIGHT, 'Snake')
    self.win.autoupdate = False # turn off autoupdate so window doesn't flicker

    drawWindow()

def drawWindow(self):
    global win

    # clear the screen
    #win.erase() # this would be used instead but for a bug...
    self.win.fill(' ')

    # draw outside border
    #TODO

    # draw game data
    self.win.putchars("Player 1 score: " + str(game.snakes[0].length), 0, 0)
    self.win.putchars("Player 2 score: " + str(game.snakes[1].length), 30, 0)

    for snake in self.snakes:
        for pos in snake:
            # pos is a tuple (x, y)
            self.win.putchars('O', pos[0], pos[1], fgcolor = snake.fgcolor)

    # draw pellet
    self.win.putchar('+', game.pellet.posx, game.pellet.posy, game.pellet.fgcolor)

    # actually paint the window
    self.win.update()

def quit():
    pygame.quit()

#FIXME return game condition (running or game over) or report it via member variable
    def tick(self):
        for snake in self.snakes:
            # move players' snakes
            #FIXME snakes need to know positions of other snakes (at least in the local area)
            snake.move(self.pellet)

            # check for self-collision
            if snake.isColl(snake):
                print_debug('SnakeGame', 'a snake bit itself')

            # check if colliding with any other snakes
            #FIXME collision detection (do something better than O(n²)
            for otherSnake in self.snakes:
                if snake != otherSnake:
                    if snake.isColl(otherSnake):
                        print_debug('SnakeGame', 'some snake ran into another snake')

            #TODO check if hitting the edge
            #if ...

            # check if snake is on a pellet
            if snake.headX == self.pellet.posx and snake.headY == self.pellet.posy:
                snake.length += 1
                self.pellet = Pellet(self.winWidth - 1, self.winHeight - 1, fgcolor = 'yellow')
                snake.grow()

        self.tickNum += 1
    # end tick()

def processUserInput(self):
    # process input queue
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            quit()
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                self.snake1.changeHeading(Dir.Up)
            elif event.key == K_DOWN:
                self.snake1.changeHeading(Dir.Down)
            elif event.key == K_LEFT:
                self.snake1.changeHeading(Dir.Left)
            elif event.key == K_RIGHT:
                self.snake1.changeHeading(Dir.Right)

    #FIXME  send player input if it changed game state
    self.sendNetMessages()

def sendNetMessages(self):
    if self.game.gameStateChanged == True:
        SendGameUpdateTo(lobbyAddr, pack(STRUCT_FMT_GAME_UPDATE, game.tickNum, game.snake1.heading))
        self.game.gameStateChanged = False
