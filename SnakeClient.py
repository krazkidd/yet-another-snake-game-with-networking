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

import sys

import SnakeGame
from SnakeConfig import *
from SnakeNet import *

# the lobby server address #
lobbyAddr = None

# an instance of a running game #
game = None

def quit():
    if lobbyAddr:
        print_debug('SnakeClient', 'Quitting lobby.')
        SendQuitMessageTo(lobbyAddr)

    if game:
        game.quit()

    CloseSocket()
    sys.exit()

def start():
    InitClientSocket()

    SendHelloMessage()

    SendLobbyListRequest()

    processNetMessages()

    quit()
    
def joinLobby(lobbyList):
    global lobbyAddr
    
    print 'There are currently ' + str(len(lobbyList)) + ' lobbies on this server:'
    for i in range(len(lobbyList)):
        print str(i + 1) + '. Lobby ' + str(lobbyList[i][0]) + ' on port ' + str(lobbyList[i][1])

    selection = int(raw_input('\nWhich lobby would you like to join? '))

    lobbyAddr = (HOST, lobbyList[selection - 1][1])
    
    SendLobbyJoinRequestTo(lobbyAddr)

def startGame():
    global game

    #FIXME need IDs list from server
    game = SnakeGame.SnakeGame(WIN_WIDTH, WIN_HEIGHT, (0, 1))
    game.startGame()

def processNetMessages():
    address, msgType, msgBody = CheckForMessage()

    while not msgType == MessageType.NONE:
        if msgType == MessageType.MOTD:
            if address == (HOST, SERVER_PORT):
                print '\nMessage of the Day from ' + HOST + ':\n' + str(msgBody) + '\n'
        elif msgType == MessageType.LOBBY_REP:
            if address == (HOST, SERVER_PORT):
                joinLobby(UnpackLobbyList(msgBody))
        elif msgType == MessageType.LOBBY_JOIN:
            if address == lobbyAddr:
                print 'we\'re in!'
        elif msgType == MessageType.LOBBY_QUIT:
            if address == lobbyAddr:
                quit()

        address, msgType, msgBody = CheckForMessage()
