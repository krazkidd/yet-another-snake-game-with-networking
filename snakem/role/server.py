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

import snakem.config.server as cfg

from snakem.game import game
from snakem.net import net
from snakem.test import debug
from snakem.enums import *

class MainServer:
    def __init__(self):
        self.lobbies = []

    def start(self):
        debug.init_debug('MainServer', cfg.PRINT_DEBUG, cfg.PRINT_ERROR, cfg.PRINT_NETMSG)

        # start lobbies as separate processes
        for i in range(1, cfg.NUM_LOBBIES + 1):
            lobby = LobbyServer(i)
            pid = os.fork()
            if pid == 0:
                lobby.start()
                sys.exit(0)
            self.lobbies.append(lobby)

        net.InitServerSocket(cfg.BIND_ADDR)

        print 'Main server has started on port ' + str(cfg.BIND_ADDR[1]) + '. Waiting for clients...'

        try:
            while True:
                net.WaitForInput(self.handleNetMessage)
        except BaseException as e:
            debug.print_err(str(e))
        finally:
            net.CloseSocket()

    def handleNetMessage(self, address, msgType, msgBody):
        if msgType == MsgType.HELLO:
            net.SendMOTD(address, cfg.MOTD)
        elif msgType == MsgType.LOBBY_REQ:
            net.SendLobbyList(address, self.lobbies)

class LobbyServer(MainServer):
    def __init__(self, lobbyNum):
        # unique server ID #
        self.lobbyNum = lobbyNum
        self.connectPort = net.InitServerSocket((cfg.BIND_ADDR[0], 0)) # port = 0 will use random port

        self.serverState = None

        # activePlayers maps net addresses to tuples of (r, s) where:
        #   r = ready status (MsgType.{NOT_,}READY)
        #   s = snake id when a game is running
        self.activePlayers = dict()

        self.game = None

    def start(self):
        debug.init_debug('LobbyServer', cfg.PRINT_DEBUG, cfg.PRINT_ERROR, cfg.PRINT_NETMSG)

        print 'Lobby server ' + str(self.lobbyNum) + ' has started on port ' \
           + str(self.connectPort) + '. Waiting for clients...'

        self.startLobbyMode()

        tickTime = 0.0

        try:
            while True:
                net.WaitForInput(self.handleNetMessage, doBlock=not self.serverState == GameState.GAME)

                if self.serverState == GameState.GAME:
                    tickTime += net.TIMEOUT
                    if tickTime >= cfg.STEP_TIME:
                        tickTime -= cfg.STEP_TIME
                        self.game.tick()

                        for addr in self.activePlayers:
                            for id, s in self.game.snakes.iteritems():
                                net.SendSnakeUpdate(addr, self.game.tickNum, id, s)

                        for s in self.game.snakes.itervalues():
                            if s.isAlive:
                                break
                        else:
                            self.endGameMode()
                            self.startLobbyMode()
        except BaseException as e:
            debug.print_err(str(self.lobbyNum) + ': ' + str(e))
        finally:
            net.CloseSocket()

    def handleNetMessage(self, address, msgType, msgBody):
        if address in self.activePlayers:
            if self.serverState == GameState.GAME:
                self.handleNetMessageDuringGame(address, msgType, msgBody)
            elif self.serverState == GameState.LOBBY:
                status, id = self.activePlayers[address]

                if msgType == MsgType.LOBBY_JOIN:
                    net.SendLobbyJoinRequest(address)  # LOBBY_JOIN is used for join confirmation
                    self.activePlayers[address] = (MsgType.NOT_READY, id)  # reset READY status
                elif msgType == MsgType.LOBBY_QUIT:
                    del self.activePlayers[address]
                elif msgType == MsgType.READY:
                    self.activePlayers[address] = (MsgType.READY, id)

                    for addr, playerTuple in self.activePlayers.iteritems():
                        if not playerTuple[0] == MsgType.READY:
                            break
                    else:
                        self.startGameMode()
                elif msgType == MsgType.NOT_READY:
                    self.activePlayers[address] = (MsgType.NOT_READY, id)
        else:  # address not in self.activePlayers
            if self.serverState == GameState.LOBBY:
                if msgType == MsgType.LOBBY_JOIN:
                    if len(self.activePlayers) < 4:
                        net.SendLobbyJoinRequest(address)  # LOBBY_JOIN is used for join confirmation
                        self.activePlayers[address] = (MsgType.NOT_READY, None)
                    else:
                        net.SendQuitMessage(address)  # LOBBY_QUIT is used for join rejection

    def handleNetMessageDuringGame(self, address, msgType, msgBody):
        doUpdateClients = False

        if msgType == MsgType.INPUT:
            self.game.snakes[self.activePlayers[address][1]].changeHeading(net.UnpackInputMessage(msgBody))
            doUpdateClients = True

        if doUpdateClients:
            for addr in self.activePlayers:
                for id, s in self.game.snakes.iteritems():
                    net.SendSnakeUpdate(addr, self.game.tickNum, id, s)

    def startLobbyMode(self):
        self.serverState = GameState.LOBBY

    def startGameMode(self):
        self.serverState = GameState.GAME

        self.game = game.Game(cfg.WIN_WIDTH, cfg.WIN_HEIGHT)

        for addr, playerTuple in self.activePlayers.iteritems():
            self.activePlayers[addr] = (playerTuple[0], self.game.SpawnNewSnake())

        self.game.SpawnNewPellet()

        for addr in self.activePlayers:
            for id, s in self.game.snakes.iteritems():
                net.SendSnakeUpdate(addr, self.game.tickNum, id, s)

        for addr in self.activePlayers:
            net.SendStartMessage(addr)

    def endGameMode(self):
        for addr in self.activePlayers:
            net.SendEndMessage(addr)

        self.game = None
