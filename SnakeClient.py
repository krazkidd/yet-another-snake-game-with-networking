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

import time
import os 
import sys

from time import time
from struct import pack
from struct import unpack
from struct import calcsize

import pygame
from pygame.locals import *
import pygcurse

import SnakeGame
from SnakeConfig import *
from SnakeGame import Dir
from SnakeNet import *

# the lobby server address #
lobbyAddr = None
# list of players that will be active during a game #
activeList = ()
# list of spectating players #
spectatingList = ()
# tells whether the player is ready to start a game or not #
isReady = False
# an instance of a running game #
game = None
# Pygcurse window object #
win = None

def init():
    InitClientSocket()

def quit():
    global lobbyAddr

    SendQuitMessageTo(lobbyAddr)

    CloseSocket()

    pygame.quit()
    sys.exit()

def start():
    global game

    init()
    joinLobby()

    try:
        # main game loop
        while True:
            if game:
                processUserInput()

            processNetMessages()

            if game:
                currTime = time()
                if currTime - lastTickTime > 0.1:
                    game.tick()
                    lastTickTime = currTime
                    drawWindow()
        # end while (main client loop)
    except BaseException as e:
        print_err('SnakeClient', str(e))
    finally:
        quit()

def joinLobby():
    global lobbyAddr

    SendHelloMessage()

    motd = ReceiveMOTD()
    print '\nMessage of the Day from ' + HOST + ':\n' + motd

    SendLobbyListRequest()
    lobbyList = ReceiveLobbyList()
    print 'There are currently ' + str(len(lobbyList)) + ' lobbies on this server:'
    for i in range(len(lobbyList)):
        print str(i + 1) + '. Lobby ' + str(lobbyList[i][0]) + ' on port ' + str(lobbyList[i][1])

    selection = int(raw_input('Which lobby would you like to join? '))

    selectedLobby, selectedPort = lobbyList[selection - 1]
    print 'Joining lobby number ' + str(selectedLobby) + '.'

    SendLobbyJoinRequestTo((HOST, selectedPort))

    #TODO make sure we joined successfully (listen for ACCEPT or REJECT message)

    lobbyAddr = (HOST, selectedPort)

def startGame():
    global win, game

    #FIXME need IDs list from server
    game = SnakeGame.SnakeGame(WIN_WIDTH, WIN_HEIGHT, (0, 1))

    # initiate pygame and pygcurse
    os.environ['SDL_VIDEO_CENTERED'] = '1' # center window in Windows
    pygame.init()
    win = pygcurse.PygcurseWindow(WIN_WIDTH, WIN_HEIGHT, 'Snake')
    win.autoupdate = False # turn off autoupdate so window doesn't flicker

    drawWindow()

def drawWindow():
    global win, game

    # clear the screen
    #win.erase() # this would be used instead but for a bug...
    win.fill(' ')

    # draw outside border
    #TODO

    # draw game data
    win.putchars("Player 1 score: " + str(game.snakes[0].length), 0, 0)
    win.putchars("Player 2 score: " + str(game.snakes[1].length), 30, 0)

    for snake in game.snakes:
        for pos in snake:
            # pos is a tuple (x, y)
            win.putchars('O', pos[0], pos[1], fgcolor = snake.fgcolor)

    # draw pellet
    win.putchar('+', game.pellet.posx, game.pellet.posy, game.pellet.fgcolor)

    # actually paint the window
    win.update()

def processUserInput():
    # process input queue
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            quit()
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                game.processInput(Dir.Up)
            elif event.key == K_DOWN:
                game.processInput(Dir.Down)
            elif event.key == K_LEFT:
                game.processInput(Dir.Left)
            elif event.key == K_RIGHT:
                game.processInput(Dir.Right)

    #FIXME  send player input if it changed game state
    sendNetMessages()

def processNetMessages():
    address, msgType, msgBody = CheckForMessage()

    #FIXME this will break the game if the client receives a lot of messages (because it won't handle user input)
    while not msgType == MessageType.NONE:
        # only look at it if it's from the server
        if addr == lobbyAddr:
            if msgType == MessageType.INIT_STATE:
                #FIXME
                pass
            elif msgType == MessageType.START:
                startGame()
            elif msgType == MessageType.SERVER_UPDATE:
                #FIXME
                pass
            elif msgType == MessageType.CLIENT_UPDATE:
                print 'We got an update from another player.'

        address, msgType, msgBody = CheckForMessage()

def sendNetMessages():
    if game.gameStateChanged == True:
        SendGameUpdateTo(lobbyAddr, pack(STRUCT_FMT_GAME_UPDATE, game.tickNum, game.snake1.heading))
        game.gameStateChanged = False
