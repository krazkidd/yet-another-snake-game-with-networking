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
from time import time

import SnakeGame
import SnakeNet
from SnakeConfig import *
from SnakeDebug import *

class LobbyServer:
    def __init__(self, lobbyNum):
        # unique server ID #
        self.lobbyNum = lobbyNum

        # activePlayers maps net addresses to tuples of (X, Y) where:
        #   X: ready status (0 for not ready, 1 for ready)
        #   Y: Snake object when a game is running
        self.activePlayers = dict()
        # spectatingPlayers maps net addresses to nothing, currently
        self.spectatingPlayers = dict()

        self.game = None

        # open a socket and wait for clients
        self.connectPort = SnakeNet.InitLobbyServerSocket()
    # end __init__()

    # lobby server thread runs here
    def start(self):
        # NOTE: summary of net stuff
        # when all players are ready, start a new game and send
        #   initial state
        # get messages from players and update game state
        #  * we don't need to update any other player right away unless
        #    they are very close
        #  * but we do need to send updates every so often just to keep
        #    clients synch'd
        # the only client updates should be the turning of the avatar (left or right)
        #  * keep track of a sequence number in update packets, as well as client
        #    gameworld ticks since last update (so the server can reproduce what client has)

        try:
            while True:
                self.processNetMessages()

                if self.game:
                    currTime = time()
                    if currTime - lastTickTime > 0.1:
                        self.game.tick()
                        lastTickTime = currTime
            # end while (main server loop)
        except BaseException as e:
            print_err('LobbyServer', str(self.lobbyNum) + ': ' + str(e))
        finally:
            SnakeNet.CloseSocket()
    # end start()

    def Game(self):
        self.game = SnakeGame.SnakeGame(WIN_WIDTH, WIN_HEIGHT, self.activePlayers.keys())

        for addr, playerTuple in self.activePlayers:
            SendSetupMessage(addr)

        for addr, playerTuple in self.activePlayers:
            SendStartMessage(addr)
        for addr in self.spectatingPlayers:
            SendStartMessage(addr)
    # end startGame()

    def processNetMessages(self):
        address, msgType, msgBody = SnakeNet.CheckForMessage()

        #FIXME this will break the game if the server receives a lot of messages, because it's busy handling those
        #      instead of ticking the game
        while not msgType == SnakeNet.MessageType.NONE:
            if msgType == SnakeNet.MessageType.HELLO:
                SendHelloMessageTo(address)
            elif msgType == SnakeNet.MessageType.LOBBY_JOIN:
                if address in self.activePlayers or address in self.spectatingPlayers or (len(self.activePlayers) + len(self.spectatingPlayers) < MAX_LOBBY_SIZE):
                    print_debug('LobbyServer', 'Woohoo! We got a new client!')
                    SendLobbyJoinRequestTo(address) # LOBBY_JOIN is used for join confirmation
                    self.spectatingPlayers[address] = None
                else:
                    SendQuitMessageTo(address) # LOBBY_QUIT is used for join rejection
            elif msgType == SnakeNet.MessageType.LOBBY_QUIT:
                if address in self.activePlayers:
                    print_debug('LobbyServer', 'Active player is quitting.')
                    del self.activePlayers[address]
                elif address in self.spectatingPlayers:
                    print_debug('LobbyServer', 'Spectating player is quitting.')
                    del self.spectatingPlayers[address]
#           elif msgType == SnakeNet.MessageType.READY:
#               if address in self.activePlayers:
#                   self.activePlayers[address][0] = 1
#                   # check if everyone is ready to start
#                   #TODO set a timer when a majority is ready in order to prevent griefers
#                   readyToStart = True
#                   for addr, playerTuple in self.activePlayers:
#                       if playerTuple[0] != 1:
#                           readyToStart = False
#                           break
#                   if readyToStart:
#                       #FIXME start a game
#                       pass
#           elif msgType == SnakeNet.MessageType.NOT_READY:
#               if address in self.activePlayers:
#                   # get player info from activePlayers list
#                   playerTuple = self.activePlayers[address]
#                   # set ready status
#                   playerTuple[0] = 0
#                   # put it back
#                   self.activePlayers[address] = playerTuple
#               #TODO if we started the majority-ready timer and we lost majority, stop it
            elif msgType == SnakeNet.MessageType.UPDATE:
                # process update from client; change server state if valid; echo to other clients
                #clientTickNum, newSnakeDir = unpack(STRUCT_FMT_GAME_UPDATE, msg[calcsize(STRUCT_FMT_HDR):])
                #TODO validate client input (check tick num--it shouldn't be off server tick num by more than 1 and if it is off, send server state)
                print_debug('LobbyServer', 'Tick num: ' + str(clientTickNum) + ', New snake direction: ' + str(newSnakeDir))
                for addr in self.activePlayers:
                    # don't echo UPDATE to player that just sent it
                    #TODO use better variable names
                    if addr != address:
                        sock.sendto(msg, addr)
#           elif msgType == SnakeNet.MessageType.CHAT:
#               pass

            address, msgType, msgBody = CheckForMessage()
        # end while (net message queue is empty)
    # end processNetMessages()
# end class LobbyServer

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

                if msgType == SnakeNet.MessageType.HELLO:
                    SnakeNet.SendMOTDTo(address)
                elif msgType == SnakeNet.MessageType.LOBBY_REQ:
                    SnakeNet.SendLobbyListTo(address, lobbies)
        except BaseException as e:
            print_err('MainServer', str(e))
        finally:
            SnakeNet.CloseSocket()
            sys.exit(1)

        SnakeNet.CloseSocket()
        sys.exit(0)
# end class MainServer
