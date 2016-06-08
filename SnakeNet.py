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

from SnakeDebug import *

MOTD = 'Welcome to my Snake-M development server!'

HOST = 'localhost'
PORT = 11845

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

class MessageType:
    """Enum for Snake network messages"""
    NONE, HELLO, MOTD, LOBBY_REQ, LOBBY_REP, LOBBY_JOIN, LOBBY_QUIT, READY, NOT_READY, START, UPDATE, CHAT, SETUP = range(13)

def SendMOTDTo(socket, address):
    buf = pack(STRUCT_FMT_HDR, MessageType.MOTD, calcsize(STRUCT_FMT_HDR) + len(MOTD))
    buf += MOTD

    print_debug('Sending MOTD to ' + address[0] + '.')

    socket.sendto(buf, address)

def SendLobbyListTo(socket, address, lobbies):
    buf = pack(STRUCT_FMT_HDR, MessageType.LOBBY_REP, calcsize(STRUCT_FMT_HDR) + calcsize(STRUCT_FMT_LOBBY_COUNT) + calcsize(STRUCT_FMT_LOBBY) * len(lobbies))
    buf += pack(STRUCT_FMT_LOBBY_COUNT, len(lobbies))
    for lobby in lobbies:
        buf += pack(STRUCT_FMT_LOBBY, lobby.lobbyNum, lobby.connectPort)

    print_debug(str(len(lobbies)) + ' lobbies sent to ' + address[0] + '.')

    socket.sendto(buf, address)

def SendSetupMessage(socket):
    socket.send(pack(STRUCT_FMT_HDR, MessageType.SETUP, calcsize(STRUCT_FMT_HDR)))

def SendStartMessage(socket):
    socket.send(pack(STRUCT_FMT_HDR, MessageType.START, calcsize(STRUCT_FMT_HDR)))

def SendHelloMessageTo(socket, address):
    print_debug('Sending HELLO to ' + address[0] + '.')
    socket.sendto(pack(STRUCT_FMT_HDR, MessageType.HELLO, calcsize(STRUCT_FMT_HDR)), address)

def SendQuitMessageTo(socket, address):
    socket.sendto(pack(STRUCT_FMT_HDR, MessageType.LOBBY_QUIT, calcsize(STRUCT_FMT_HDR)), address)

def ReceiveMOTDFrom(socket):
    msg, srvaddr = socket.recvfrom(calcsize(STRUCT_FMT_HDR) + MAX_MSG_SIZE)
    return msg[calcsize(STRUCT_FMT_HDR):], srvaddr

def SendLobbyListRequestTo(socket, address):
    socket.sendto(pack(STRUCT_FMT_HDR, MessageType.LOBBY_REQ, calcsize(STRUCT_FMT_HDR)), address)

def ReceiveLobbyListFrom(socket):
    msg, srvaddr = socket.recvfrom(MAX_MSG_SIZE)
    lobbyCount = int(unpack(STRUCT_FMT_LOBBY_COUNT, msg[calcsize(STRUCT_FMT_HDR)])[0]) # this is a really ugly statement but int(msg[calcsize(STRUCT_FMT_HDR)]) throws an exception
    lobbyList = msg[calcsize(STRUCT_FMT_HDR) + calcsize(STRUCT_FMT_LOBBY_COUNT):]

    print_debug(str(lobbyCount) + ' lobbies received from ' + srvaddr[0] + '.')

    toReturn = []
    for i in range(0, lobbyCount):
        lobbyNum, lobbyPort = unpack(STRUCT_FMT_LOBBY, lobbyList[i * calcsize(STRUCT_FMT_LOBBY):i * calcsize(STRUCT_FMT_LOBBY) + calcsize(STRUCT_FMT_LOBBY)])
        toReturn.append((lobbyNum, lobbyPort))
    return toReturn, srvaddr

def SendLobbyJoinRequestTo(socket, address):
    socket.sendto(pack(STRUCT_FMT_HDR, MessageType.LOBBY_JOIN, calcsize(STRUCT_FMT_HDR)), address)

def SendGameUpdateTo(socket, address, packedUpdate):
    msg = pack(STRUCT_FMT_HDR, MessageType.UPDATE, calcsize(STRUCT_FMT_HDR) + calcsize(STRUCT_FMT_GAME_UPDATE))
    msg += packedUpdate
    socket.sendto(msg, address)

def WaitForClient(socket):
    msg, address = socket.recvfrom(MAX_MSG_SIZE)
    #FIXME we get an exception if the input isn't of the expected size, so we need to check msg length
    msgType, msgLen = unpack(STRUCT_FMT_HDR, msg[:calcsize(STRUCT_FMT_HDR)])
    return address, msgType

def GetSocketForMainServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
    return s

def GetSocketForLobbyServer(port):
    # open a socket and wait for clients
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, port))

    # NOTE: we need the socket to be non-blocking since we try to flush the whole net message queue when select says it's ready
    s.setblocking(0)
    return s

def GetSocketForClient():
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def CheckForMessage(socket):
    # NOTE: We want select() to timeout in order to see if the game needs to tick.
    #       We use select() simply so we don't have to do our own timeout.
    readable, writable, exceptional = select([socket], [], [], 0.005)

    if socket in readable:
        # NOTE: it's possible for the socket to not actually be ready, like in the case of a checksum error
        msg, address = socket.recvfrom(MAX_MSG_SIZE)
        msgType, msgLen = unpack(STRUCT_FMT_HDR, msg[:calcsize(STRUCT_FMT_HDR)])
        #FIXME return message body
        return address, msgType, None
    else:
        return None, MessageType.NONE, None
