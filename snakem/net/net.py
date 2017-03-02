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
import sys
from select import select
from struct import pack
from struct import unpack
from struct import calcsize

from snakem.config import *
from snakem.enums import *

MAX_MSG_SIZE = 1024

sock = None

def InitServerSocket(port=0):
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', port))

    return sock.getsockname()[1] # return port

def InitClientSocket():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def CloseSocket():
    if sock:
        sock.close()

def SendMessage(address, msgType, msgBody=None):
    buf = None
    if msgBody:
        buf = pack(MsgFmt.HDR, msgType, calcsize(MsgFmt.HDR) + len(msgBody))
        buf += msgBody
    else:
        buf = pack(MsgFmt.HDR, msgType, calcsize(MsgFmt.HDR))

    sock.sendto(buf, address)

def ReceiveMessage():
    msg, address = sock.recvfrom(MAX_MSG_SIZE)
    msgType, msgLen = unpack(MsgFmt.HDR, msg[:calcsize(MsgFmt.HDR)])
    #TODO verify msg size!
    if len(msg) > calcsize(MsgFmt.HDR):
        return address, msgType, msg[calcsize(MsgFmt.HDR):]
    else:
        return address, msgType, None

def SendHelloMessage(address):
    SendMessage(address, MsgType.HELLO)

def SendMOTD(address):
    SendMessage(address, MsgType.MOTD, MOTD)

def SendQuitMessage(address):
    SendMessage(address, MsgType.LOBBY_QUIT)

def SendLobbyListRequest(address):
    SendMessage(address, MsgType.LOBBY_REQ)

def SendLobbyList(address, lobbies):
    buf = pack(MsgFmt.LBY_CNT, len(lobbies))
    for lobby in lobbies:
        buf += pack(MsgFmt.LBY, lobby.lobbyNum, lobby.connectPort)

    SendMessage(address, MsgType.LOBBY_REP, buf)

def UnpackLobbyList(msgBody):
    lobbyCount = unpack(MsgFmt.LBY_CNT, msgBody[:calcsize(MsgFmt.LBY_CNT)])[0]
    packedLobbies = msgBody[calcsize(MsgFmt.LBY_CNT):]

    lobbyList = []
    for i in range(lobbyCount):
        lobbyList.append(unpack(MsgFmt.LBY, packedLobbies[i * calcsize(MsgFmt.LBY):i * calcsize(MsgFmt.LBY) + calcsize(MsgFmt.LBY)]))

    return lobbyList

def SendLobbyJoinRequest(address):
    SendMessage(address, MsgType.LOBBY_JOIN)

def SendReadyMessage(address):
    SendMessage(address, MsgType.READY)

def SendSetupMessage(address):
    SendMessage(address, MsgType.SETUP)

def SendStartMessage(address):
    SendMessage(address, MsgType.START)

