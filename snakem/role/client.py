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

import select
import sys

import curses.ascii

from snakem.game import display
from snakem.game import game
from snakem.net import net

from snakem.config import *
from snakem.test.debug import *
from snakem.enums import *

mainSrvAddr = (HOST, SERVER_PORT)
motd = None
lobbyList = None

# the lobby server address #
lobbyAddr = None

clientState = None 

# the running game instance #
game = None

# how long to wait for input when a game is running #
sockTimeout = None

def start():
    net.InitClientSocket()
    display.InitClientWindow(startWithCurses)

def startWithCurses():
    startMOTDMode()

    tickTime = 0

    try:
        while True:
            readable, writable, exceptional = select.select([net.sock, sys.stdin], [], [], sockTimeout)

            if net.sock in readable:
                handleNetMessage()

            if sys.stdin in readable:
                handleInput()

            if clientState == GameState.GAME:
                tickTime += sockTimeout
                if tickTime >= STEP_TIME:
                    tickTime -= STEP_TIME
                    game.tick()
                    display.ShowGame(game)
    finally:
        if lobbyAddr:
            net.SendQuitMessage(lobbyAddr)
        net.CloseSocket()

def handleNetMessage():
    global motd, lobbyList

    address, msgType, msgBody = net.ReceiveMessage()

    if address == lobbyAddr:
        if clientState == GameState.MOTD:
            if msgType == MsgType.LOBBY_JOIN:
                startLobbyMode()
            elif msgType == MsgType.LOBBY_QUIT:
                display.ShowDebug('Lobby rejected your join request.')
                startMOTDMode()
        elif clientState == GameState.LOBBY:
            if msgType == MsgType.START:
                startGameMode()
        elif clientState == GameState.GAME:
            #TODO pass message to game
            pass
    elif address == mainSrvAddr:
        if clientState == GameState.MOTD:
            if msgType == MsgType.MOTD:
                motd = msgBody
                display.ShowMOTD(address, motd, lobbyList)
            elif msgType == MsgType.LOBBY_REP:
                lobbyList = net.UnpackLobbyList(msgBody)
                display.ShowMOTD(address, motd, lobbyList)

def handleInput():
    global lobbyAddr

    c = display.GetKey()

    if clientState == GameState.MOTD:
        if c in KEYS_LOBBY_QUIT:
            sys.exit()
        elif curses.ascii.isdigit(c):
            selection = int(curses.ascii.unctrl(c))
            if selection >= 1 and selection <= len(lobbyList):
                lobbyAddr = (mainSrvAddr[0], lobbyList[selection - 1][1])
                net.SendLobbyJoinRequest(lobbyAddr)
        elif c in KEYS_LOBBY_REFRESH:
            net.SendHelloMessage(mainSrvAddr)
            net.SendLobbyListRequest(mainSrvAddr)
    elif clientState == GameState.LOBBY:
        if c in KEYS_LOBBY_QUIT:
            net.SendQuitMessage(lobbyAddr)
            startMOTDMode()
        elif c in KEYS_LOBBY_READY:
            net.SendReadyMessage(lobbyAddr)
    elif clientState == GameState.GAME:
        if c == KEYS_GAME_QUIT:
            #TODO make it harder to quit running game
            net.SendQuitMessage(lobbyAddr)
            startMOTDMode()
        elif c in KEYS_MV_LEFT:
            game.snakes[0].changeHeading(Dir.Left)
        elif c in KEYS_MV_DOWN:
            game.snakes[0].changeHeading(Dir.Down)
        elif c in KEYS_MV_UP:
            game.snakes[0].changeHeading(Dir.Up)
        elif c in KEYS_MV_RIGHT:
            game.snakes[0].changeHeading(Dir.Right)
    elif clientState == GameState.GAME_OVER:
        if c in KEYS_LOBBY_QUIT:
            startLobbyMode()

def startMOTDMode():
    global clientState, lobbyAddr
    clientState  = GameState.MOTD
    lobbyAddr = None

    net.SendHelloMessage(mainSrvAddr)
    net.SendLobbyListRequest(mainSrvAddr)

    display.ShowMessage('Contacting server at ' + mainSrvAddr[0] + ':' + str(mainSrvAddr[1]) + ' . . .')

def startLobbyMode():
    global clientState, sockTimeout
    clientState = GameState.LOBBY
    sockTimeout = None

    display.ShowLobby()

def startGameMode():
    global clientState, sockTimeout, game
    clientState = GameState.GAME
    sockTimeout = 0.005

    #TODO get win width/height from server
    #game = game.Game(WIN_WIDTH, WIN_HEIGHT, 1, 1)
    h, w = display.GetWindowSize()
    game = game.Game(w, h, 1, 1)

    display.ShowGame(game)
