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
import sys
import time

from snakem.game import game
from snakem.net import net
from snakem.config import *
from snakem.test.debug import *
from snakem.enums import *

class LobbyServer:
    def __init__(self, lobbyNum):
        # unique server ID #
        self.lobbyNum = lobbyNum
        self.connectPort = net.InitServerSocket()

        self.serverState = None

        # activePlayers maps net addresses to tuples of (X, Y) where:
        #   X: ready status (MsgType.{NOT_,}READY)
        #   Y: Snake object when a game is running
        self.activePlayers = dict()

        self.game = None

        self.sockTimeout = 0.0

    def start(self):
        print 'Lobby server ' + str(self.lobbyNum) + ' has started on port ' + str(self.connectPort) + '. Waiting for clients...'

        self.startLobbyMode()

        tickTime = 0.0

        try:
            while True:
                net.WaitForInput(self.handleNetMessage, timeout=self.sockTimeout)

                if self.serverState == GameState.GAME:
                    tickTime += self.sockTimeout
                    if tickTime >= STEP_TIME:
                        tickTime -= STEP_TIME
                        self.game.tick()
        except BaseException as e:
            print_err('LobbyServer', str(self.lobbyNum) + ': ' + str(e))
        finally:
            net.CloseSocket()

    def handleNetMessage(self):
        address, msgType, msgBody = net.ReceiveMessage()

        if address in self.activePlayers:
            if self.serverState == GameState.LOBBY:
                if msgType == MsgType.LOBBY_JOIN:
                    net.SendLobbyJoinRequest(address) # LOBBY_JOIN is used for join confirmation
                    self.activePlayers[address] = (MsgType.NOT_READY, None) # reset READY status
                elif msgType == MsgType.LOBBY_QUIT:
                    del self.activePlayers[address]
                elif msgType == MsgType.READY:
                    self.activePlayers[address] = (MsgType.READY, None)
                    allReady = True
                    for addr, playerTuple in self.activePlayers.iteritems():
                        allReady = allReady and playerTuple[0] == MsgType.READY
                    if allReady:
                        self.startGameMode()
            elif self.serverState == GameState.GAME:
                #TODO pass message to game
                pass
        else: # address not in self.activePlayers
            if self.serverState == GameState.LOBBY:
                if msgType == MsgType.LOBBY_JOIN:
                    if len(self.activePlayers) < MAX_PLAYERS:
                        net.SendLobbyJoinRequest(address) # LOBBY_JOIN is used for join confirmation
                        self.activePlayers[address] = (MsgType.NOT_READY, None)
                    else:
                        net.SendQuitMessage(address) # LOBBY_QUIT is used for join rejection

    def startLobbyMode(self):
        self.serverState = GameState.LOBBY
        self.sockTimeout = 0.0

    def startGameMode(self):
        self.serverState = GameState.GAME
        self.sockTimeout = 0.005

        self.game = game.Game(WIN_WIDTH, WIN_HEIGHT, len(self.activePlayers))

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

        net.InitServerSocket(SERVER_PORT)

        print 'Main server has started on port ' + str(SERVER_PORT) + '. Waiting for clients...'

        try:
            while True:
                address, msgType, msgBody = net.ReceiveMessage()

                if msgType == MsgType.HELLO:
                    net.SendMOTD(address)
                elif msgType == MsgType.LOBBY_REQ:
                    net.SendLobbyList(address, lobbies)
        except BaseException as e:
            print_err('MainServer', str(e))
        finally:
            net.CloseSocket()

