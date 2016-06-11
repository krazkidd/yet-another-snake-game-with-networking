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

import curses
import select
import sys

import SnakeCurses
import SnakeGame
import SnakeNet
from SnakeConfig import *
from SnakeDebug import *

# the lobby server address #
lobbyAddr = None

# an instance of a running game #
game = None

def start():
    SnakeNet.InitClientSocket()
    SnakeCurses.InitClientWindow(startWithCurses)

def startWithCurses():
    SnakeNet.SendHelloMessage()
    SnakeNet.SendLobbyListRequest()

    while True:
        readable, writable, exceptional = select.select([SnakeNet.sock, sys.stdin], [], [])

        if SnakeNet.sock in readable:
            handleNetMessage()
        elif sys.stdin in readable:
            handleInput()

def quit():
    if lobbyAddr:
        SnakeNet.SendQuitMessageTo(lobbyAddr)
    SnakeNet.CloseSocket()

    if game:
        game.quit()

    sys.exit()

def handleNetMessage():
    address, msgType, msgBody = SnakeNet.UnpackMessage()

    if msgType == SnakeNet.MessageType.MOTD:
        if not lobbyAddr and address == (HOST, SERVER_PORT):
            SnakeCurses.ShowMOTD(HOST, str(msgBody))
    elif msgType == SnakeNet.MessageType.LOBBY_REP:
        if not lobbyAddr and address == (HOST, SERVER_PORT):
            #joinLobby(SnakeNet.UnpackLobbyList(msgBody))
            pass
    elif msgType == SnakeNet.MessageType.LOBBY_JOIN:
        if address == lobbyAddr:
            print_debug('SnakeClient', 'starting game, yo')
            startGame()

def joinLobby(lobbyList):
    global lobbyAddr

    print 'There are currently ' + str(len(lobbyList)) + ' lobbies on this server:'
    for i in range(len(lobbyList)):
        print str(i + 1) + '. Lobby ' + str(lobbyList[i][0]) + ' on port ' + str(lobbyList[i][1])
        pass

    selection = int(raw_input('\nWhich lobby would you like to join? '))

    lobbyAddr = (HOST, lobbyList[selection - 1][1])

    SnakeNet.SendLobbyJoinRequestTo(lobbyAddr)

def handleInput():
    c = SnakeCurses.GetKey()
    SnakeCurses.ShowDebug('Keycode: ' + str(c))

    if c == 27: # escape
        quit()

def startGame():
    global game

    #FIXME need IDs list from server
    game = SnakeGame.SnakeGame(WIN_WIDTH, WIN_HEIGHT, (0, 1))
    #game.startGame()

