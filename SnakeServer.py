import time
import os 
import socket
import curses
import sys

from struct import pack
from struct import unpack
from struct import calcsize
from select import select

import SnakeGame
from SnakeNet import *

class LobbyServer:
    def __init__(self, lobbyNum):
        self.lobbyNum = lobbyNum
        #FIXME try different port until success
        self.connectPort = PORT + self.lobbyNum
        self.activePlayers = set()
        self.spectatingPlayers = set()

    # server thread runs here
    def start(self):
        # open a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setblocking(0)
        s.bind((HOST, self.connectPort))
        print 'Lobby server ' + str(self.lobbyNum) + ' has started on port ' + str(self.connectPort) + '. Waiting for clients...'

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

        while 1:
            # NOTE: We want select to timeout in order to see if the game needs to tick
            #       We use select() simply so we don't have to do our own timeout
            readable, writable, exceptional = select([s], [], [], 0.025)

            if s in readable:
                # NOTE: it's possible for the socket to not actually be ready, like in the case of a checksum error
                msg, address = s.recvfrom(MAX_MSG_SIZE)

                #FIXME this will break the game if the server receives a lot of messages
                while msg:
                    msgType, msgLen = unpack(STRUCT_FMT_HDR, msg[:calcsize(STRUCT_FMT_HDR)])

                    if msgType == MessageType.HELLO:
                        print 'Client says hello to lobby.'
                        s.sendto(pack(STRUCT_FMT_HDR, MessageType.HELLO, calcsize(STRUCT_FMT_HDR)), address)
                    elif msgType == MessageType.LOBBY_JOIN:
                        #FIXME send accept or reject message to join request

                        #FIXME if the client is already in a list, clearly they were dropped. i need to handle that case
                        if (address, 0) not in self.activePlayers and (address, 1) not in self.activePlayers and address not in self.spectatingPlayers and (len(self.activePlayers) + len(self.spectatingPlayers) < MAX_LOBBY_SIZE):
                            print 'Woohoo! We got a new client!'
                            #TODO tell other clients we have another player 
                            #FIXME add to spectating players list instead
                            #spectatingPlayers.add(address)
                            self.activePlayers.add((address, 1))
                    elif msgType == MessageType.LOBBY_QUIT:
                        #FIXME use a dictionary instead of array of tuples...
                        if (address, 0) in self.activePlayers:
                            self.activePlayers.remove((address, 0))
                        elif (address, 1) in self.activePlayers:
                            self.activePlayers.remove((address, 1))
                        elif address in self.spectatingPlayers:
                            self.spectatingPlayers.remove(address)
                            #TODO tell other clients we lost a player 
                    elif msgType == MessageType.READY:
                        if (address, 0) in self.activePlayers:
                            self.activePlayers.remove((address, 0)) # 0 means not ready
                            #TODO can we keep the set in the same order?
                            self.activePlayers.add((address, 1)) # 1 means ready
                        
                        # check if everyone is ready to start
                        #TODO set a timer when a majority is ready in order to prevent griefers
                        readyToStart = True
                        for addr, status in self.activePlayers:
                            if status != 1:
                                readyToStart = False
                                break
                        if readyToStart:
                            #FIXME start a game
                            pass
                    elif msgType == MessageType.NOT_READY:
                        if (address, 1) in self.activePlayers:
                            self.activePlayers.remove((address, 1))
                            #TODO can we keep the set in the same order?
                            self.activePlayers.add((address, 0))
                        #TODO if we started the majority-ready timer and we lost majority, stop it
                    elif msgType == MessageType.UPDATE:
                        clientTickNum, newSnakeDir = unpack(STRUCT_FMT_GAME_UPDATE, msg[calcsize(STRUCT_FMT_HDR):])
                        #FIXME
                        print 'Tick num: ' + str(clientTickNum) + ', New snake direction: ' + str(newSnakeDir)
                        #TODO check if we need to (and can--don't allow multiple changes per tick) update the game state. if changed, push to other clients
                        #TODO only send update if there was a state change
                        for addr, rdyStatus in self.activePlayers:
                            # don't echo UPDATE to player that just sent it
                            #TODO use better variable names
                            if addr != address:
                                s.sendto(msg, addr)
                        for addr, rdyStatus in self.spectatingPlayers:
                            #TODO use better variable names
                            s.sendto(msg, addr)
                    elif msgType == MessageType.CHAT:
                        pass

                    try:
                        # check for another message
                        msg, address = s.recvfrom(MAX_MSG_SIZE)
                    except socket.error:
                        msg = None

            #FIXME test if it's time to tick()

        print 'Lobby server ' + str(clientNo) + ' is closing.'

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
