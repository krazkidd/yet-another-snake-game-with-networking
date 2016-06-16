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

        self.serverState = None

        # activePlayers maps net addresses to tuples of (X, Y) where:
        #   X: ready status (MessageType.{NOT_,}READY)
        #   Y: Snake object when a game is running
        self.activePlayers = dict()

        self.game = None

        self.connectPort = SnakeNet.InitLobbyServerSocket()

    def start(self):
        self.startLobbyMode()

        try:
            while True:
                readable, writable, exceptional = select.select([SnakeNet.sock], [], [], 0.005)

                if SnakeNet.sock in readable:
                    self.handleNetMessage()
                else:
                    #TODO manage clients and game
                    pass
        except BaseException as e:
            print_err('LobbyServer', str(self.lobbyNum) + ': ' + str(e))
        finally:
            SnakeNet.CloseSocket()

    def handleNetMessage(self):
        address, msgType, msgBody = SnakeNet.UnpackMessage()

        if self.serverState == GameState.LOBBY:
            if msgType == MessageType.HELLO:
                SnakeNet.SendHelloMessageTo(address)
            elif msgType == MessageType.LOBBY_JOIN:
                #TODO reinstate lobby size check--disabled so we don't have to restart server every time client crashes
                #if address not in self.activePlayers and len(self.activePlayers) < SnakeGame.MAX_PLAYERS:
                print_debug('LobbyServer', 'Woohoo! We got a new client!')
                SnakeNet.SendLobbyJoinRequestTo(address) # LOBBY_JOIN is used for join confirmation
                self.activePlayers[address] = (MessageType.NOT_READY, None)
                #else:
                #    print_debug('LobbyServer', 'Lobby full. New client rejected.')
                #    SnakeNet.SendQuitMessageTo(address) # LOBBY_QUIT is used for join rejection
            elif msgType == MessageType.LOBBY_QUIT:
                if address in self.activePlayers:
                    print_debug('LobbyServer', 'Active player is quitting.')
                    del self.activePlayers[address]
            elif msgType == MessageType.READY:
                if address in self.activePlayers:
                    self.activePlayers[address] = (MessageType.READY, None)
                    allReady = True
                    for addr in self.activePlayers:
                        allReady = allReady and self.activePlayers[addr][0] == MessageType.READY
                    if allReady:
                        self.startGameMode()
        elif self.serverState == GameState.GAME and (address in self.activePlayers):
            #TODO pass message to game
            pass

    def startLobbyMode(self):
        self.serverState = GameState.LOBBY

    def startGameMode(self):
        self.serverState = GameState.GAME

        self.game = SnakeGame.SnakeGame(WIN_WIDTH, WIN_HEIGHT, len(self.activePlayers))

        for addr in self.activePlayers:
            SnakeNet.SendSetupMessage(addr)

        for addr in self.activePlayers:
            SnakeNet.SendStartMessage(addr)

class MainServer:
    @staticmethod
    def start():
        pid = 0
        # start lobbies as separate processes
        lobbies = []
        for i in range(1, 1 + NUM_LOBBIES):
            lobby = LobbyServer(i)
            lobbies.append(lobby)
            pid = os.fork()
            if pid == 0:
                lobbies = None
                lobby.start()
                sys.exit(0) # end lobby process if it ever exits

        print_debug('MainServer', str(len(lobbies)) + ' lobbies started.')

        SnakeNet.InitMainServerSocket()

        print 'Main server has started on port ' + str(SERVER_PORT) + '. Waiting for clients...'

        try:
            while True:
                address, msgType = SnakeNet.WaitForClient()

                if msgType == MessageType.HELLO:
                    SnakeNet.SendMOTDTo(address)
                elif msgType == MessageType.LOBBY_REQ:
                    SnakeNet.SendLobbyListTo(address, lobbies)
        except BaseException as e:
            print_err('MainServer', str(e))
        finally:
            SnakeNet.CloseSocket()
            sys.exit(1)

        SnakeNet.CloseSocket()
        sys.exit(0)

