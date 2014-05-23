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

import SnakeGame
from SnakeNet import *

class LobbyServer:
    def __init__(self, lobbyNum):
        # unique server ID #
        self.lobbyNum = lobbyNum
        # the port to listen on #
        #FIXME try different port until success
        self.connectPort = PORT + self.lobbyNum
        # these two player lists map player IP addresses to other player information #
        # activePlayers maps addresses to tuples of (X, Y) where:
        #   X: ready status (0 for not ready, 1 for ready)
        #   Y: Snake object when a game is running
        self.activePlayers = dict()
        # spectatingPlayers maps addresses to nothing currently
        self.spectatingPlayers = dict()

        # open a socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((HOST, self.connectPort))
        print 'Lobby server ' + str(self.lobbyNum) + ' has started on port ' + str(self.connectPort) + '. Waiting for clients...'
    # end __init__()

    # server thread runs here
    def start(self):
        # NOTE: we need the socket to be non-blocking since we try to flush the whole net message queue when select says it's ready
        s.setblocking(0)

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

        while True:
            self.processNetMessages()

            if self.game:
                currTime = time()
                if currTime - lastTickTime > 0.1:
                    self.game.tick()
                    lastTickTime = currTime
        # end while (main server loop)

        #TODO this is never reached because we don't have an exit condition
        print 'Lobby server ' + str(self.lobbyNum) + ' is closing.'
    # end start()

    def startGame(self):
        self.game = SnakeGame.SnakeGame(WIN_WIDTH, WIN_HEIGHT, self.activePlayers.keys())

        TODO send SETUP message with initial game state and tell them which snake they are
        for addr, playerTuple in self.activePlayers:
            #TODO wait for confirmation

        # send START messages
        for addr, playerTuple in self.activePlayers:
            s.sendto(pack(STRUCT_FMT_HDR
        for addr in self.spectatingPlayers:
            s.sendto(pack(STRUCT_FMT_HDR, MessageType.START, calcsize(STRUCT_FMT_HDR))
    # end startGame()

    def processNetMessages(self):
        s = self.s

        # NOTE: We want select to timeout in order to see if the game needs to tick
        #       We use select() simply so we don't have to do our own timeout
        readable, writable, exceptional = select([s], [], [], 0.005)

        if s in readable:
            # NOTE: it's possible for the socket to not actually be ready, like in the case of a checksum error
            msg, address = s.recvfrom(MAX_MSG_SIZE)

            #FIXME this will break the game if the server receives a lot of messages, because it's busy handling those
            #      instead of ticking the game
            while msg:
                msgType, msgLen = unpack(STRUCT_FMT_HDR, msg[:calcsize(STRUCT_FMT_HDR)])

                if msgType == MessageType.HELLO:
                    print 'Client says hello to lobby.'
                    s.sendto(pack(STRUCT_FMT_HDR, MessageType.HELLO, calcsize(STRUCT_FMT_HDR)), address)
                elif msgType == MessageType.LOBBY_JOIN:
                    #FIXME send accept or reject message to join request

                    #FIXME if the client is already in a list, clearly they were dropped. i need to handle that case
                    if address not in self.activePlayers and address not in self.spectatingPlayers and (len(self.activePlayers) + len(self.spectatingPlayers) < MAX_LOBBY_SIZE):
                        print 'Woohoo! We got a new client!'
                        #TODO tell other clients we have another player 
                        #FIXME add to spectating players list instead
                        #self.spectatingPlayers[address] = ()
                        self.activePlayers[address] = (1, None)

                        #FIXME move to READY message. this is just a shortcut for now
                        if len(self.activePlayers) == 2:
                            self.startGame()
                            lastTickTime = time()
#                    elif msgType == MessageType.LOBBY_QUIT:
#                        if address in self.activePlayers:
#                            #TODO do something special if game is running
#                            del self.activePlayers[address]
#                            #TODO tell other clients we lost a player 
#                        elif address in self.spectatingPlayers:
#                            del self.spectatingPlayers[address]
#                            #TODO tell other clients we lost a player 
#                    elif msgType == MessageType.READY:
#                        if address in self.activePlayers:
#                            self.activePlayers[address][0] = 1
#
#                            # check if everyone is ready to start
#                            #TODO set a timer when a majority is ready in order to prevent griefers
#                            readyToStart = True
#                            for addr, playerTuple in self.activePlayers:
#                                if playerTuple[0] != 1:
#                                    readyToStart = False
#                                    break
#                            if readyToStart:
#                                #FIXME start a game
#                                pass
#                    elif msgType == MessageType.NOT_READY:
#                        if address in self.activePlayers:
#                            # get player info from activePlayers list
#                            playerTuple = self.activePlayers[address]
#                            # set ready status
#                            playerTuple[0] = 0
#                            # put it back
#                            self.activePlayers[address] = playerTuple
#                        #TODO if we started the majority-ready timer and we lost majority, stop it
                elif msgType == MessageType.UPDATE:
                    # process update from client; change server state if valid; echo to other clients
                    clientTickNum, newSnakeDir = unpack(STRUCT_FMT_GAME_UPDATE, msg[calcsize(STRUCT_FMT_HDR):])
                    #TODO validate client input (check tick num--it shouldn't be off server tick num by more than 1 and if it is off, send server state)
                    print 'Tick num: ' + str(clientTickNum) + ', New snake direction: ' + str(newSnakeDir)
                    for addr in self.activePlayers:
                        # don't echo UPDATE to player that just sent it
                        #TODO use better variable names
                        if addr != address:
                            s.sendto(msg, addr)
#                    elif msgType == MessageType.CHAT:
#                        pass

                # NOTE: socket s is in non-blocking mode and throws an exception if there's nothing to recv
                try:
                    # check for another message
                    msg, address = s.recvfrom(MAX_MSG_SIZE)
                except socket.error:
                    msg = None
            # end while (net message queue is empty)
        # end processNetMessages()
# end class LobbyServer

class MainServer:
    @staticmethod
    def start():
        # start static lobbies as separate processes
        numLobbies = 5
        lobbies = set()
        #TODO make lobby creation dynamic (i.e. user-created)
        for i in range(1, numLobbies + 1):
            lobby = LobbyServer(i)
            lobbies.add(lobby)
            pid = os.fork()
            if pid == 0:
                lobbies = ()
                lobby.start()
                sys.exit(0) # end process if lobby ever exits

        #TODO always test that we can open the port first! (main server must not be in charge of connectNum--but we have to use a mutex if we increment it here in lobby server)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((HOST, PORT))
        print 'Main server has started on port ' + str(PORT) + '. Waiting for clients...'

        # serve forever
        while 1:
            # listen for clients
            msg, address = s.recvfrom(MAX_MSG_SIZE)

            # fork and respond
            #TODO os.fork() only available on *nix
            #TODO what happens to the child processes when they die? do i have to join() or something
            #      so they don't become zombies?
            pid = os.fork()
            if pid == 0:
                #FIXME we get an exception if the input isn't of the expected size, so we need to check msg length
                msgType, msgLen = unpack(STRUCT_FMT_HDR, msg[:calcsize(STRUCT_FMT_HDR)])
                # check header for message type and reply accordingly
                if msgType == MessageType.HELLO:
                    # send MOTD
                    print 'Client connected. Sending MOTD.'
                    #TODO catch any exceptions from file access here
                    f = open('MOTD')
                    motdStr = f.read(MAX_MOTD_SIZE)
                    buf = pack(STRUCT_FMT_HDR, MessageType.MOTD, calcsize(STRUCT_FMT_HDR) + len(motdStr))
                    buf += motdStr
                    s.sendto(buf, address)
                    f.close()
                elif msgType == MessageType.LOBBY_REQ:
                    # send list of lobbies
                    buf = pack(STRUCT_FMT_HDR, MessageType.LOBBY_REP, calcsize(STRUCT_FMT_HDR) + calcsize(STRUCT_FMT_LOBBY_COUNT) + calcsize(STRUCT_FMT_LOBBY) * numLobbies)
                    buf += pack(STRUCT_FMT_LOBBY_COUNT, numLobbies)
                    for lobby in lobbies:
                        buf += pack(STRUCT_FMT_LOBBY, lobby.lobbyNum, lobby.connectPort)
                    s.sendto(buf, address)

                s.close()
                sys.exit(0)
# end class MainServer
