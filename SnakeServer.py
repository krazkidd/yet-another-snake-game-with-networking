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
import select
import sys
import time

import SnakeGame
import SnakeNet
from SnakeConfig import *
from SnakeDebug import *
from SnakeEnums import *

class LobbyServer:
    def __init__(self, lobbyNum):
        # unique server ID #
        self.lobbyNum = lobbyNum
        self.connectPort = SnakeNet.InitServerSocket()

        self.serverState = None

        # activePlayers maps net addresses to tuples of (X, Y) where:
        #   X: ready status (MessageType.{NOT_,}READY)
        #   Y: Snake object when a game is running
        self.activePlayers = dict()

        self.game = None

        self.sockTimeout = None

    def start(self):
        print 'Lobby server ' + str(self.lobbyNum) + ' has started on port ' + str(self.connectPort) + '. Waiting for clients...'

        self.startLobbyMode()

        tickTime = 0

        try:
            while True:
                readable, writable, exceptional = select.select([SnakeNet.sock], [], [], self.sockTimeout)

                if SnakeNet.sock in readable:
                    self.handleNetMessage()

                if self.serverState == GameState.GAME:
                    tickTime += self.sockTimeout
                    if tickTime >= STEP_TIME:
                        tickTime -= STEP_TIME
                        self.game.tick()
        except BaseException as e:
            print_err('LobbyServer', str(self.lobbyNum) + ': ' + str(e))
        finally:
            SnakeNet.CloseSocket()

    def handleNetMessage(self):
        address, msgType, msgBody = SnakeNet.ReceiveMessage()

        if address in self.activePlayers:
            if self.serverState == GameState.LOBBY:
                if msgType == MessageType.LOBBY_JOIN:
                    SnakeNet.SendLobbyJoinRequest(address) # LOBBY_JOIN is used for join confirmation
                    self.activePlayers[address] = (MessageType.NOT_READY, None) # reset READY status
                elif msgType == MessageType.LOBBY_QUIT:
                    del self.activePlayers[address]
                elif msgType == MessageType.READY:
                    self.activePlayers[address] = (MessageType.READY, None)
                    allReady = True
                    for addr, playerTuple in self.activePlayers.iteritems():
                        allReady = allReady and playerTuple[0] == MessageType.READY
                    if allReady:
                        self.startGameMode()
            elif self.serverState == GameState.GAME:
                #TODO pass message to game
                pass
        else: # address not in self.activePlayers
            if self.serverState == GameState.LOBBY:
                if msgType == MessageType.LOBBY_JOIN:
                    if len(self.activePlayers) < SnakeGame.MAX_PLAYERS:
                        SnakeNet.SendLobbyJoinRequest(address) # LOBBY_JOIN is used for join confirmation
                        self.activePlayers[address] = (MessageType.NOT_READY, None)
                    else:
                        SnakeNet.SendQuitMessage(address) # LOBBY_QUIT is used for join rejection

    def startLobbyMode(self):
        self.serverState = GameState.LOBBY
        self.sockTimeout = None

    def startGameMode(self):
        self.serverState = GameState.GAME
        self.sockTimeout = 0.005

        self.game = SnakeGame.SnakeGame(WIN_WIDTH, WIN_HEIGHT, len(self.activePlayers))

        #TODO start sending game setup messages

class MainServer:
    @staticmethod
    def start():
        # start lobbies as separate processes
        lobbies = []
        for i in range(1, NUM_LOBBIES + 1):
            lobby = LobbyServer(i)
            pid = os.fork()
            if pid == 0:
                lobby.start()
                sys.exit(0)
            lobbies.append(lobby)

        SnakeNet.InitServerSocket(SERVER_PORT)

        print 'Main server has started on port ' + str(SERVER_PORT) + '. Waiting for clients...'

        try:
            while True:
                address, msgType, msgBody = SnakeNet.ReceiveMessage()

                if msgType == MessageType.HELLO:
                    SnakeNet.SendMOTD(address)
                elif msgType == MessageType.LOBBY_REQ:
                    SnakeNet.SendLobbyList(address, lobbies)
        except BaseException as e:
            print_err('MainServer', str(e))
        finally:
            SnakeNet.CloseSocket()

