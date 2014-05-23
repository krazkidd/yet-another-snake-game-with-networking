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
import socket
import sys

from time import time
from struct import pack
from struct import unpack
from struct import calcsize
from select import select

import pygame
from pygame.locals import *
import pygcurse

import SnakeGame
from SnakeGame import Dir
from SnakeNet import *

# the network socket to send/receive on #
s = None
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
    global s

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# end init()

def quit():
    # send QUIT message to lobby server if we're connected to one
    if lobbyAddr:
        s.sendto(pack(STRUCT_FMT_HDR, MessageType.LOBBY_QUIT, calcsize(STRUCT_FMT_HDR)), lobbyAddr)

    s.close()
    pygame.quit()
    sys.exit()
# end quit()

def start():
    init()
    joinLobby()

    # main game loop
    while True:
        # check user input
        processUserInput()

        # get messages from server
        processNetMessages()

        if game:
            currTime = time()
            if currTime - lastTickTime > 0.1:
                game.tick()
                lastTickTime = currTime
                drawWindow()
    # end while (main client loop)

    #TODO this is never reached
    quit()
# end start()

def joinLobby():
    global lobbyAddr

    s.sendto(pack(STRUCT_FMT_HDR, MessageType.HELLO, calcsize(STRUCT_FMT_HDR)), (HOST, PORT))
    #print 'Sending HELLO to server.'
    #TODO print server hostname and address. anything else?

    #FIXME allow direct connection to lobbies. if response isn't MOTD, it's a lobby

    # get MOTD
    msg, srvaddr = s.recvfrom(calcsize(STRUCT_FMT_HDR) + MAX_MOTD_SIZE)
    print '\nMessage of the Day from server:'
    print msg[calcsize(STRUCT_FMT_HDR):] + '\n'

    # get lobby info
    s.sendto(pack(STRUCT_FMT_HDR, MessageType.LOBBY_REQ, calcsize(STRUCT_FMT_HDR)), (HOST, PORT))
    msg, srvaddr = s.recvfrom(MAX_MSG_SIZE)
    lobbyCount = int(unpack(STRUCT_FMT_LOBBY_COUNT, msg[calcsize(STRUCT_FMT_HDR)])[0]) # this is a really ugly statement but int(msg[calcsize(STRUCT_FMT_HDR)]) throws an exception
    lobbyList = msg[calcsize(STRUCT_FMT_HDR) + calcsize(STRUCT_FMT_LOBBY_COUNT):]
    print 'There are currently ' + str(lobbyCount) + ' lobbies on this server:'
    for i in range(0, lobbyCount):
        lobbyNum, lobbyPort = unpack(STRUCT_FMT_LOBBY, lobbyList[i * calcsize(STRUCT_FMT_LOBBY):i * calcsize(STRUCT_FMT_LOBBY) + calcsize(STRUCT_FMT_LOBBY)])
        print str(i + 1) + '. Lobby ' + str(lobbyNum) + ' on port ' + str(lobbyPort)

    selection = int(raw_input('Which lobby would you like to join? '))
    
    selectedLobby, selectedPort = unpack(STRUCT_FMT_LOBBY, lobbyList[selection * calcsize(STRUCT_FMT_LOBBY):selection * calcsize(STRUCT_FMT_LOBBY) + calcsize(STRUCT_FMT_LOBBY)])    
    print 'Joining lobby number ' + str(selectedLobby) + '.'

    # try to join lobby
    s.sendto(pack(STRUCT_FMT_HDR, MessageType.LOBBY_JOIN, calcsize(STRUCT_FMT_HDR)), (HOST, selectedPort))

    #TODO make sure we joined successfully (listen for ACCEPT or REJECT message)

    lobbyAddr = (srvaddr[0], selectedPort)
# end joinLobby() 

def startGame():
    global win
    global game

FIXME need IDs list from server
    game = SnakeGame.SnakeGame(WIN_WIDTH, WIN_HEIGHT, (0, 1)))

    # initiate pygame and pygcurse
    os.environ['SDL_VIDEO_CENTERED'] = '1' # center window in Windows
    pygame.init()
    win = pygcurse.PygcurseWindow(WIN_WIDTH, WIN_HEIGHT, 'Snake')
    win.autoupdate = False # turn off autoupdate so window doesn't flicker

    drawWindow()
# end startGame()

def drawWindow():
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
# end drawWindow()

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

    FIXME  send player input if it changed game state
    sendNetMessages()
# end processUserInput()

def processNetMessages():
    # NOTE: I use select because someone on StackOverflow said it's easier than setting non-blocking mode
    readable, writable, exceptional = select([s], [], [], 0)

    #FIXME this will break the game if the client receives a lot of messages (because it won't handle user input)
    while readable:
        #if s in readable:
        msg, addr = s.recvfrom(MAX_MSG_SIZE)

        # only look at it if it's from the server
        if addr == lobbyAddr:
            msgType, msgLen = unpack(STRUCT_FMT_HDR, msg[:calcsize(STRUCT_FMT_HDR)])

            if msgType == INIT_STATE:
                FIXME
            elif msgType == START:
                startGame()
            elif msgType == MessageType.SERVER_UPDATE:
                FIXME
            elif msgType == MessageType.CLIENT_UPDATE:
                print 'We got an update from another player.'
        
        readable, writable, exceptional = select([s], [], [], 0)
# end processNetMessages()

def sendNetMessages():
    if game.gameStateChanged == True:
        msg = pack(STRUCT_FMT_HDR, MessageType.UPDATE, calcsize(STRUCT_FMT_HDR) + calcsize(STRUCT_FMT_GAME_UPDATE))
        msg += pack(STRUCT_FMT_GAME_UPDATE, game.tickNum, game.snake1.heading)
        s.sendto(msg, lobbyAddr)
        game.gameStateChanged = False
# end sendNetMessages()
