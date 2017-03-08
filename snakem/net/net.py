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
import select
from struct import pack
from struct import unpack
from struct import calcsize

from snakem.test import debug
from snakem.enums import *

MAX_MSG_SIZE = 1024

# how long to wait for an input event
TIMEOUT = 0.005

sock = None

def InitServerSocket(addr):
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(addr)

    return sock.getsockname()[1] # return port

def InitClientSocket():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def CloseSocket():
    if sock:
        sock.close()

def WaitForInput(netCallback, keyboardCallback=None, doBlock=True):
    if doBlock:
        # we block on this call so we're not wasting cycles outside of an active game
        readable, writable, exceptional = select.select([sock, sys.stdin], [], [])
    else:
        readable, writable, exceptional = select.select([sock, sys.stdin], [], [], TIMEOUT)

    if keyboardCallback is not None and sys.stdin in readable:
        keyboardCallback()
    elif netCallback is not None and sock in readable:
        address, msgType, msgBody = ReceiveMessage()
        netCallback(address, msgType, msgBody)

def SendMessage(address, msgType, msgBody=None):
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
        msgBody = msg[calcsize(MsgFmt.HDR):]
    else:
        msgBody = None

    debug.print_net_msg(address, msgType, msgBody)

    return address, msgType, msgBody

def SendHelloMessage(address):
    SendMessage(address, MsgType.HELLO)

def SendMOTD(address, motd):
    SendMessage(address, MsgType.MOTD, motd)

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
    size = calcsize(MsgFmt.LBY)
    for i in range(lobbyCount):
        lobbyList.append(unpack(MsgFmt.LBY, packedLobbies[i * size:(i + 1) * size]))

    return lobbyList

def SendSnakeUpdate(address, tick, id, snake):
    #TODO don't exceed MAX_MSG_SIZE (without breaking the game--allow splitting an update or increase MAX_MSG_SIZE)
    buf = pack(MsgFmt.SNAKE_UPDATE_HDR, tick, id, snake.heading, snake.isAlive, len(snake.body))
    for pos in snake.body:
        buf += pack(MsgFmt.SNAKE_UPDATE_BDY, pos[0], pos[1])

    SendMessage(address, MsgType.SNAKE_UPDATE, buf)

def UnpackSnakeUpdate(msgBody):
    tick, id, heading, isAlive, length = unpack(MsgFmt.SNAKE_UPDATE_HDR, msgBody[:calcsize(MsgFmt.SNAKE_UPDATE_HDR)])
    bodyBuf = msgBody[calcsize(MsgFmt.SNAKE_UPDATE_HDR):]

    body = list()
    size = calcsize(MsgFmt.SNAKE_UPDATE_BDY)
    for i in range(length):
        body.append((unpack(MsgFmt.SNAKE_UPDATE_BDY, bodyBuf[i * size:(i + 1) * size])))

    return tick, id, heading, isAlive, body

def SendLobbyJoinRequest(address):
    SendMessage(address, MsgType.LOBBY_JOIN)

def SendReadyMessage(address):
    SendMessage(address, MsgType.READY)

def SendSetupMessage(address):
    SendMessage(address, MsgType.SETUP)

def SendStartMessage(address):
    SendMessage(address, MsgType.START)

def SendEndMessage(address):
    SendMessage(address, MsgType.END)

def SendInputMessage(address, heading):
    SendMessage(address, MsgType.INPUT, pack(MsgFmt.PLAYER_INPUT, heading))

def UnpackInputMessage(msgBody):
    return unpack(MsgType.INPUT, msgBody)
