#!/usr/bin/python2

#TODO add copyright and license info

import time
import os 
from os.path import basename
import socket
from struct import pack
from struct import unpack
from struct import calcsize

#from Snake import *
from SnakeGame import *

#FIXME allow host and port config from command line. what if port is appended to hostname?
HOST = '' # any network interface
PORT = 11845

MAX_MSG_SIZE = 1024
MAX_MOTD_SIZE = 1024

STRUCT_FMT_LOBBY = '!H'

#FIXME make database of player names/passwords
PLAYER_NAME = 'Guest'

def main():
    # get program name and fork to server or client mode
    if 'snakes' == basename(sys.argv[0]):
        doMainServerStuff()
    elif 'snake' == basename(sys.argv[0]):
        doClientStuff()
    else:
        print 'Usage: This program must be called via symlink with name `snake` (client) or `snakes` (server).'

def doMainServerStuff():
    connectNum = 1

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5) # argument is size of connection backlog
    print 'Server has started on port ' + str(PORT) + '. Waiting for clients...'

    # wait for connection
    while 1:
        (clientsocket, address) = s.accept()
        pid = os.fork()
        if (0 == pid):
            # s.shutdown(socket.SHUT_RDWR) # NOTE: We don't call shutdown because that really ends the TCP connection.
            s.close()                      #       Instead, we just want to close the file descriptor

            doLobbyServerStuff(clientsocket, connectNum)

            #FIXME do any cleanup after a lobby closes?

            # lobby process will die after this
            break
        else:
            # clientsocket.shutdown(socket.SHUT_RDWR) # we must not call shutdown() because TCP
            clientsocket.close()
            #FIXME save child ID so we can talk to it?
            connectNum = connectNum + 1
            continue

def doLobbyServerStuff(clientsocket, clientNo):
    #FIXME test that we can open the port first! (main server must not be in charge of connectNum--but we have to use a mutex if we increment it here in lobby server)
    print 'Client connected. Sending to game lobby ' + str(clientNo) + '.'

    # send MOTD
    #FIXME send MOTD before lobby num? i should add a field to demux messages rather than expect them in an exact sequence
    f = open('MOTD')
    #FIXME catch any errors from file access here
    clientsocket.send(f.read(MAX_MOTD_SIZE))

    # before moving to UDP socket, tell client lobby port
    clientsocket.send(pack(STRUCT_FMT_LOBBY, PORT + clientNo))

    # NOTE: we have to open a new listening socket so client sees an open connection (or until we write a client that waits)
    # bind socket to UDP port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT + clientNo))

    clientsocket.shutdown(socket.SHUT_RDWR)
    clientsocket.close()

    # NOTE: https://docs.python.org/2/library/socketserver.html#module-SocketServer
    #       says something about using threads because Python networking may be slow

    # wait for connection
    #FIXME this loop needs to die eventually; add flag and/or timeout
    while 1:
        #TODO process whole network queue
        data, addr = s.recvfrom(MAX_MSG_SIZE)

        #TODO need to verify sender address? session could easily be clobbered if not
        print data

    print 'Lobby server ' + str(clientNo) + ' is closing.'

def doClientStuff():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print 'Connected to server.'
    #TODO print server hostname and address. anything else?

    # get MOTD
    print 'Message of the Day from server:'
    print s.recv(MAX_MOTD_SIZE)

    # get lobby info
    lobbyPort = unpack(STRUCT_FMT_LOBBY, s.recv(calcsize(STRUCT_FMT_LOBBY)))[0]
    #FIXME client sees port number, not actual lobby number. Subtract PORT here or tell client their client num?
    print 'Joining lobby number ' + str(lobbyPort) + '.'

    # move to UDP port for game
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # these dimension units are in text cells, not pixels
    WIN_WIDTH, WIN_HEIGHT = 60, 35

    game = SnakeGame(WIN_WIDTH, WIN_HEIGHT)

    # main game loop
    #FIXME client should go back to lobby after game is over
    while True:
        #FIXME does game know about networking? how much input does it pass on to server?
        #      
        game.processInput()

        game.tick()

        game.drawWindow()

        # pause the screen for just a bit
        time.sleep(0.1)

if __name__ == "__main__":
    main()
