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

import socket

from select import select
from struct import pack
from struct import unpack
from struct import calcsize

from SnakeConfig import *
from SnakeDebug import *

MAX_MSG_SIZE = 1024

# net message header
# B: message type
# H: length of message (including header)
STRUCT_FMT_HDR = '!BH'

# number of lobbies
STRUCT_FMT_LOBBY_COUNT = '!B'

# info for single lobby
# B: lobby number
# H: port number
STRUCT_FMT_LOBBY = '!BH'

# game update message
# I: tick num of update (game time elapsed)
# B: new heading of player's snake
STRUCT_FMT_GAME_UPDATE = '!IB'

sock = None

class MessageType:
    """Enum for Snake network messages"""
    NONE, HELLO, MOTD, LOBBY_REQ, LOBBY_REP, LOBBY_JOIN, LOBBY_QUIT, READY, NOT_READY, START, UPDATE, CHAT, SETUP = range(13)

def SendMOTDTo(address):
    buf = pack(STRUCT_FMT_HDR, MessageType.MOTD, calcsize(STRUCT_FMT_HDR) + len(MOTD))
    buf += MOTD

    print_debug('SnakeNet', 'Sending MOTD to ' + address[0] + '.')

    sock.sendto(buf, address)

def SendLobbyListTo(address, lobbies):
    buf = pack(STRUCT_FMT_HDR, MessageType.LOBBY_REP, calcsize(STRUCT_FMT_HDR) + calcsize(STRUCT_FMT_LOBBY_COUNT) + calcsize(STRUCT_FMT_LOBBY) * len(lobbies))
    buf += pack(STRUCT_FMT_LOBBY_COUNT, len(lobbies))
    for lobby in lobbies:
        buf += pack(STRUCT_FMT_LOBBY, lobby.lobbyNum, lobby.connectPort)

    print_debug('SnakeNet', str(len(lobbies)) + ' lobbies sent to ' + address[0] + '.')

    sock.sendto(buf, address)

def SendSetupMessage():
    sock.send(pack(STRUCT_FMT_HDR, MessageType.SETUP, calcsize(STRUCT_FMT_HDR)))

def SendStartMessage():
    sock.send(pack(STRUCT_FMT_HDR, MessageType.START, calcsize(STRUCT_FMT_HDR)))

def SendHelloMessage():
    print_debug('SnakeNet', 'Sending HELLO to ' + HOST + '.')
    sock.sendto(pack(STRUCT_FMT_HDR, MessageType.HELLO, calcsize(STRUCT_FMT_HDR)), (HOST, SERVER_PORT))

def SendQuitMessageTo(address):
    if address:
        sock.sendto(pack(STRUCT_FMT_HDR, MessageType.LOBBY_QUIT, calcsize(STRUCT_FMT_HDR)), address)

def ReceiveMOTD():
    msg, srvaddr = sock.recvfrom(calcsize(STRUCT_FMT_HDR) + MAX_MSG_SIZE)
    if IsServer(srvaddr):
        return msg[calcsize(STRUCT_FMT_HDR):]
    else:
        print_debug('SnakeNet', 'Ignoring message from unexpected sender.')
        return None

def IsServer(addr):
    return addr[0] == HOST and addr[1] == SERVER_PORT

def SendLobbyListRequest():
    sock.sendto(pack(STRUCT_FMT_HDR, MessageType.LOBBY_REQ, calcsize(STRUCT_FMT_HDR)), (HOST, SERVER_PORT))

def ReceiveLobbyList():
    msg, srvaddr = sock.recvfrom(MAX_MSG_SIZE)
    if IsServer(srvaddr):
        lobbyCount = int(unpack(STRUCT_FMT_LOBBY_COUNT, msg[calcsize(STRUCT_FMT_HDR)])[0]) # this is a really ugly statement but int(msg[calcsize(STRUCT_FMT_HDR)]) throws an exception
        lobbyList = msg[calcsize(STRUCT_FMT_HDR) + calcsize(STRUCT_FMT_LOBBY_COUNT):]

        print_debug('SnakeNet', str(lobbyCount) + ' lobbies received from ' + srvaddr[0] + '.')

        toReturn = []
        for i in range(lobbyCount):
            lobbyNum, lobbyPort = unpack(STRUCT_FMT_LOBBY, lobbyList[i * calcsize(STRUCT_FMT_LOBBY):i * calcsize(STRUCT_FMT_LOBBY) + calcsize(STRUCT_FMT_LOBBY)])
            toReturn.append((lobbyNum, lobbyPort))
        return toReturn
    else:
        print_debug('SnakeNet', 'Ignoring message from unexpected sender.')
        return None

def SendLobbyJoinRequestTo(address):
    sock.sendto(pack(STRUCT_FMT_HDR, MessageType.LOBBY_JOIN, calcsize(STRUCT_FMT_HDR)), address)

def SendGameUpdateTo(address, packedUpdate):
    msg = pack(STRUCT_FMT_HDR, MessageType.UPDATE, calcsize(STRUCT_FMT_HDR) + calcsize(STRUCT_FMT_GAME_UPDATE))
    msg += packedUpdate
    sock.sendto(msg, address)

def WaitForClient():
    msg, address = sock.recvfrom(MAX_MSG_SIZE)
    #FIXME we get an exception if the input isn't of the expected size, so we need to check msg length
    msgType, msgLen = unpack(STRUCT_FMT_HDR, msg[:calcsize(STRUCT_FMT_HDR)])
    return address, msgType

def InitMainServerSocket():
    global sock

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', SERVER_PORT))

    print_debug('SnakeNet', 'Initializing server socket on port ' + str(sock.getsockname()[1]) + '.')

def InitLobbyServerSocket():
    global sock

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 0)) # random port
    sock.setblocking(0) # non-blocking

    print_debug('SnakeNet', 'Initializing server socket on port ' + str(sock.getsockname()[1]) + '.')

    return sock.getsockname()[1]

def InitClientSocket():
    global sock

    print_debug('SnakeNet', 'Initializing client socket.')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def CloseSocket():
    sock.close()

def CheckForMessage():
    # NOTE: We want select() to timeout in order to see if the game needs to tick.
    #       We use select() simply so we don't have to do our own timeout.
    readable, writable, exceptional = select([sock], [], [], 0.005)

    if sock in readable:
        # NOTE: it's possible for the socket to not actually be ready, like in the case of a checksum error
        msg, address = sock.recvfrom(MAX_MSG_SIZE)
        msgType, msgLen = unpack(STRUCT_FMT_HDR, msg[:calcsize(STRUCT_FMT_HDR)])
        #FIXME return message body
        return address, msgType, None
    else:
        return None, MessageType.NONE, None
