#!/usr/bin/python2

#TODO add copyright and license info

import time
import os 
from os.path import basename
import socket
from struct import pack
from struct import unpack
from struct import calcsize

from SnakeNet import *

def main():
    # get program name and fork to server or client mode
    if 'snakes' == basename(sys.argv[0]):
        doServerStuff()
    elif 'snake' == basename(sys.argv[0]):
        Client.start()
    else:
        print 'Usage: This program must be called via symlink with name `snake` (client) or `snakes` (server).'

def doServerStuff():
    # NOTE: main server needs to fork immediately so it can process simultaneous requests. so we need to
    #   pass a list of lobby servers and their ports to be reached on.

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
            sys.exit(0)

    #FIXME always test that we can open the port first! (main server must not be in charge of connectNum--but we have to use a mutex if we increment it here in lobby server)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5) # argument is size of connection backlog
    print 'Main server has started on port ' + str(PORT) + '. Waiting for clients...'

    # wait for connection
    while 1:
        # connect to client
        (clientsocket, address) = s.accept()

        # fork and respond
        #FIXME os.fork() only available on *nix
        #FIXME what happens to the child processes when they die? do i have to join() or something
        #      so they don't become zombies?
        pid = os.fork()
        if pid == 0:
            # s.shutdown(socket.SHUT_RDWR) # NOTE: We don't call shutdown because that really ends the TCP connection.
            s.close()                      #       Instead, we just want to close the file descriptor

            print 'Client connected. Sending MOTD.'

            # send MOTD
            #FIXME send MOTD before lobby num? i should add a field to demux messages rather than expect them in an exact sequence
            f = open('MOTD')
            #FIXME catch any errors from file access here
            clientsocket.send(f.read(MAX_MOTD_SIZE))

            # send list of lobbies
            response = pack(STRUCT_FMT_LOBBY_COUNT, numLobbies)
            for lobby in lobbies:
                response += pack(STRUCT_FMT_LOBBY, lobby.lobbyNum, lobby.connectPort)
            print 'Sending lobby list. Message size: ' + str(len(response)) + '. Expected: ' + str(calcsize(STRUCT_FMT_LOBBY_COUNT + STRUCT_FMT_LOBBY_LIST)) + '.'
            clientsocket.send(response)

            clientsocket.shutdown(socket.SHUT_RDWR)
            clientsocket.close()

            sys.exit(0)
        else:
            # clientsocket.shutdown(socket.SHUT_RDWR) # we must not call shutdown() because TCP
            clientsocket.close()

if __name__ == "__main__":
    main()
