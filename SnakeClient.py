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
import time # for sleep()

import SnakeCurses
import SnakeGame
import SnakeNet
from SnakeConfig import *
from SnakeEnums import *

clientState = None

mainSrvAddr = (HOST, SERVER_PORT)
motd = None
lobbyList = None

# the lobby server address #
lobbyAddr = None

def start():
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
    if clientState == GameState.LOBBY:
        SnakeNet.SendQuitMessageTo(lobbyAddr)
    SnakeNet.CloseSocket()

    sys.exit()

def handleNetMessage():
    global motd, lobbyList, lobbyAddr

    address, msgType, msgBody = SnakeNet.UnpackMessage()

    if clientState == GameState.MOTD and address == mainSrvAddr:
        if msgType == MessageType.MOTD:
            motd = msgBody
            SnakeCurses.ShowMOTD(address, motd, lobbyList)
        elif msgType == MessageType.LOBBY_REP:
            lobbyList = SnakeNet.UnpackLobbyList(msgBody)
            SnakeCurses.ShowMOTD(address, motd, lobbyList)
    if clientState == GameState.MOTD: #TODO check address == expected lobby addr
        if msgType == MessageType.LOBBY_JOIN:
            lobbyAddr = address
            startLobbyMode()
    elif clientState == GameState.LOBBY and address == lobbyAddr:
        if msgType == MessageType.START:
            startGameMode()

def handleInput():
    c = SnakeCurses.GetKey()
    SnakeCurses.ShowDebug('Keycode: ' + str(c))

    if clientState == GameState.MOTD:
        if c == curses.ascii.ESC:
            quit()
        elif curses.ascii.isdigit(c):
            selection = int(curses.ascii.unctrl(c))
            if selection >= 1 and selection <= len(lobbyList):
                SnakeNet.SendLobbyJoinRequestTo((mainSrvAddr[0], lobbyList[selection - 1][1]))
        elif c in (ord('R'), ord('r')):
            SnakeNet.SendLobbyListRequest()
    elif clientState == GameState.LOBBY:
        if c == curses.ascii.ESC:
            SnakeNet.SendQuitMessageTo(lobbyAddr)
            startMOTDMode()

def startMOTDMode():
    global clientState
    clientState  = GameState.MOTD

    SnakeCurses.ShowMessage('Contacting server at ' + mainSrvAddr[0] + ':' + str(mainSrvAddr[1]) + ' . . .')
    SnakeNet.SendHelloMessage()
    SnakeNet.SendLobbyListRequest()

def startLobbyMode():
    global clientState
    clientState = GameState.LOBBY

    SnakeCurses.ShowLobby()

def startGameMode():
    global clientState
    clientState = GameState.GAME

    game = SnakeGame.SnakeGame(WIN_WIDTH, WIN_HEIGHT, (0, 1))
    #game.startGame()

    SnakeCurses.ShowMessage('The game will start running here . . .')

    time.sleep(1)

    startLobbyMode()

