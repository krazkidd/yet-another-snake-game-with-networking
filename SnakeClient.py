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

import SnakeCurses
import SnakeGame
import SnakeNet
from SnakeConfig import *
from SnakeDebug import *
from SnakeEnums import *

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
    SnakeNet.InitClientSocket()
    SnakeCurses.InitClientWindow(startWithCurses)

def startWithCurses():
    startMOTDMode()

    tickTime = 0

    try:
        while True:
            readable, writable, exceptional = select.select([SnakeNet.sock, sys.stdin], [], [], sockTimeout)

            if SnakeNet.sock in readable:
                handleNetMessage()

            if sys.stdin in readable:
                handleInput()

            if clientState == GameState.GAME:
                tickTime += sockTimeout
                if tickTime >= STEP_TIME:
                    tickTime -= STEP_TIME
                    game.tick()
                    SnakeCurses.ShowGame(game)
    finally:
        if lobbyAddr:
            SnakeNet.SendQuitMessageTo(lobbyAddr)
        SnakeNet.CloseSocket()

def handleNetMessage():
    global motd, lobbyList, lobbyAddr

    address, msgType, msgBody = SnakeNet.UnpackMessage()

    if address == lobbyAddr:
        if clientState == GameState.LOBBY:
            if msgType == MessageType.START:
                startGameMode()
        elif clientState == GameState.GAME:
            #TODO pass message to game
            pass
    elif address == mainSrvAddr:
        if clientState == GameState.MOTD:
            if msgType == MessageType.MOTD:
                motd = msgBody
                SnakeCurses.ShowMOTD(address, motd, lobbyList)
            elif msgType == MessageType.LOBBY_REP:
                lobbyList = SnakeNet.UnpackLobbyList(msgBody)
                SnakeCurses.ShowMOTD(address, motd, lobbyList)
    #TODO check address == expected lobby addr
    elif clientState == GameState.MOTD:
        if msgType == MessageType.LOBBY_JOIN:
            lobbyAddr = address
            startLobbyMode()
        elif msgType == MessageType.LOBBY_QUIT:
            SnakeCurses.ShowDebug('Lobby rejected your join request.')
            # show new debug message
            SnakeCurses.ShowMOTD(address, motd, lobbyList)

def handleInput():
    c = SnakeCurses.GetKey()

    if clientState == GameState.MOTD:
        if c in KEYS_LOBBY_QUIT:
            sys.exit()
        elif curses.ascii.isdigit(c):
            selection = int(curses.ascii.unctrl(c))
            if selection >= 1 and selection <= len(lobbyList):
                SnakeNet.SendLobbyJoinRequestTo((mainSrvAddr[0], lobbyList[selection - 1][1]))
        elif c in KEYS_LOBBY_REFRESH:
            SnakeNet.SendHelloMessage()
            SnakeNet.SendLobbyListRequest()
        elif c in KEYS_LOBBY_1PLAYER:
            #TODO this is a temp hack to start single player game
            startGameMode()
    elif clientState == GameState.LOBBY:
        if c in KEYS_LOBBY_QUIT:
            SnakeNet.SendQuitMessageTo(lobbyAddr)
            startMOTDMode()
        elif c in KEYS_LOBBY_READY:
            SnakeNet.SendReadyMessageTo(lobbyAddr)
    elif clientState == GameState.GAME:
        if c == KEYS_GAME_QUIT:
            #TODO make it harder to quit running game
            SnakeNet.SendQuitMessageTo(lobbyAddr)
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
    global clientState
    clientState  = GameState.MOTD

    SnakeNet.SendHelloMessage()
    SnakeNet.SendLobbyListRequest()

    SnakeCurses.ShowMessage('Contacting server at ' + mainSrvAddr[0] + ':' + str(mainSrvAddr[1]) + ' . . .')

def startLobbyMode():
    global clientState, sockTimeout
    clientState = GameState.LOBBY
    sockTimeout = None

    SnakeCurses.ShowLobby()

def startGameMode():
    global clientState, sockTimeout, game
    clientState = GameState.GAME
    sockTimeout = 0.005

    #TODO get win width/height from server
    #game = SnakeGame.SnakeGame(WIN_WIDTH, WIN_HEIGHT, 1, 1)
    h, w = SnakeCurses.GetWindowSize()
    game = SnakeGame.SnakeGame(w, h, 1, 1)

    SnakeCurses.ShowGame(game)

