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
        s.bind((HOST, self.connectPort))
        print 'Lobby server ' + str(self.lobbyNum) + ' has started on port ' + str(self.connectPort) + '. Waiting for clients...'

#FIXME need to listen for new and current clients with select() or something
#and run the game in it's own thread???

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

#FIXME do we really need threads or select()? all clients use the one port and send UDP messages. and we don't read stdin...
#      However, we do need the game to tick() while waiting for net messages. so we need to (*quickly*) poll and handle any messages
#      (and not block if there are none) or run the game in a thread. the game needs to tick at a steady rate, but even if there's 
#      contention for the socket, we should want to process all messages that came in, because 
#      active player messages need to be handled ASAP.
#      I could also use a timeout on the select() call and periodically check if we need to tick(). That will be the simplest thing and
#      the tick()'s will depend on the granularity of the timeout, but it shouldn't be too bad

      #TODO only allow one player change per game tick

            # NOTE: we want select to timeout in order to see if the game needs to tick
            readable, writable, exceptional = select([s], [], [], 0.025)

            if s in readable:
                msg, address = s.recvfrom(MAX_MSG_SIZE)

                msgType, msgLen = unpack('!BH', msg[:3])

                if msgType == MessageType.HELLO:
                    print 'Client says hello to lobby.'
                    s.sendto(pack('!BH', MessageType.HELLO, 3), address)
                elif msgType == MessageType.LOBBY_JOIN:
                    #FIXME send accept or reject message to join request

                    #FIXME if the client is already in a list, clearly they were dropped. i need to handle that case
                    if (address, 0) not in self.activePlayers and (address, 1) not in self.activePlayers and address not in self.spectatingPlayers and (len(self.activePlayers) + len(self.spectatingPlayers) < MAX_LOBBY_SIZE):
                        print 'Woohoo! We got a new client!'
                        #TODO tell other clients we have another player 
                        #FIXME add to spectating players list
                        #spectatingPlayers.add(address)
                        self.activePlayers.add((address, 1))
                elif msgType == MessageType.LOBBY_QUIT:
                    #TODO
                    pass
                elif msgType == MessageType.READY:
                    #TODO only set to ready if there are at least 2 players
                    if (address, 0) in self.activePlayers:
                        self.activePlayers.remove((address, 0)) # 0 means not ready
                        #TODO can we keep the set in the same order?
                        self.activePlayers.add((address, 1)) # 1 means ready
                    
                    #FIXME if len(activePlayers) > 1...
                    # check if everyone is ready to start
                    #TODO set a timer when a majority is ready in order to prevent griefers
                    readyToStart = True
                    for addr, status in self.activePlayers:
                        if status != 1:
                            readyToStart = False
                            break
                    if readyToStart:
                        #FIXME
                        pass
                elif msgType == MessageType.NOT_READY:
                    #FIXME
                    pass
                elif msgType == MessageType.UPDATE:
                    clientTickNum, newSnakeDir = unpack(STRUCT_FMT_GAME_UPDATE, msg[3:])
                    print 'Tick num: ' + str(clientTickNum) + ', New snake direction: ' + str(newSnakeDir)
                elif msgType == MessageType.CHAT:
                    pass
            else:
                #TODO what to do for timeout
                pass

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
            (msg, address) = s.recvfrom(MAX_MSG_SIZE)

            # fork and respond
            #TODO os.fork() only available on *nix
            #TODO what happens to the child processes when they die? do i have to join() or something
            #      so they don't become zombies?
            pid = os.fork()
            if pid == 0:
                #FIXME we get an exception if the input isn't of the expected size, so we need to check msg length
                unpackedMsg = unpack('!BH', msg)
                # check header for message type and reply accordingly
                if unpackedMsg[0] == MessageType.HELLO:
                    # send MOTD
                    print 'Client connected. Sending MOTD.'
                    f = open('MOTD')
                    #TODO use actual size of MOTD on file, not max (or whichever is less)
                    buf = pack('!BH', MessageType.MOTD, 3 + MAX_MOTD_SIZE)
                    #TODO catch any exceptions from file access here
                    buf += f.read(MAX_MOTD_SIZE)
                    s.sendto(buf, address)
                elif unpackedMsg[0] == MessageType.LOBBY_REQ:
                    # send list of lobbies
                    print 'Sending lobby list.'
                    buf = pack('!BH', MessageType.LOBBY_REP, 3 + 1 + numLobbies * 3)
                    buf += pack(STRUCT_FMT_LOBBY_COUNT, numLobbies)
                    for lobby in lobbies:
                        buf += pack(STRUCT_FMT_LOBBY, lobby.lobbyNum, lobby.connectPort)
                    #print '\tMessage size: ' + str(len(buf)) + '. Expected: ' + str(3 + calcsize(STRUCT_FMT_LOBBY_COUNT + STRUCT_FMT_LOBBY_LIST)) + '.'
                    s.sendto(buf, address)

                s.close()
                sys.exit(0)
