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

import curses
import curses.ascii
import select
import sys

import SnakeCurses
import SnakeGame
import SnakeNet
from SnakeConfig import *
from SnakeDebug import *
from SnakeEnums import *

clientState = None

# the lobby server address #
lobbyAddr = None

# an instance of a running game #
game = None

motd = None
lobbyList = None

def start():
    global clientState
    clientState = ClientState.INIT

    SnakeNet.InitClientSocket()
    SnakeCurses.InitClientWindow(startWithCurses)

def startWithCurses():
    startMOTDMode()

    while True:
        readable, writable, exceptional = select.select([SnakeNet.sock, sys.stdin], [], [])

        if SnakeNet.sock in readable:
            handleNetMessage()
        elif sys.stdin in readable:
            handleInput()

def quit():
    if lobbyAddr:
        SnakeNet.SendQuitMessageTo(lobbyAddr)
    SnakeNet.CloseSocket()

    if game:
        game.quit()

    sys.exit()

def handleNetMessage():
    global clientState, motd, lobbyList

    address, msgType, msgBody = SnakeNet.UnpackMessage()

    if msgType == MessageType.MOTD:
        if clientState <= ClientState.MOTD and not lobbyAddr and address == (HOST, SERVER_PORT):
            clientState = ClientState.MOTD
            motd = msgBody
            SnakeCurses.ShowMOTD(address, motd, lobbyList)
    elif msgType == MessageType.LOBBY_REP:
        if clientState <= ClientState.MOTD and not lobbyAddr and address == (HOST, SERVER_PORT):
            clientState = ClientState.MOTD
            lobbyList = SnakeNet.UnpackLobbyList(msgBody)
            SnakeCurses.ShowMOTD(address, motd, lobbyList)
    elif msgType == MessageType.LOBBY_JOIN:
        if clientState == ClientState.MOTD and not lobbyAddr:
            joinLobby(address)

def handleInput():
    c = SnakeCurses.GetKey()
    SnakeCurses.ShowDebug('Keycode: ' + str(c))

    if c == curses.ascii.ESC:
        quit()
    elif curses.ascii.isdigit(c):
        if clientState == ClientState.MOTD:
            SnakeNet.SendLobbyJoinRequestTo((HOST, lobbyList[int(curses.ascii.unctrl(c)) - 1][1]))

def startMOTDMode():
    global motd, lobbyList
    motd, lobbyList = (None, None)

    clientState = ClientState.MOTD

    SnakeCurses.ShowMessage('Contacting server at ' + HOST + ' . . .')
    SnakeNet.SendHelloMessage()
    SnakeNet.SendLobbyListRequest()

def joinLobby(address):
    global clientState, lobbyAddr
    clientState = ClientState.LOBBY
    lobbyAddr = address

    SnakeCurses.ShowLobby()

def startGame():
    global game

    #FIXME need IDs list from server
    game = SnakeGame.SnakeGame(WIN_WIDTH, WIN_HEIGHT, (0, 1))
    #game.startGame()

