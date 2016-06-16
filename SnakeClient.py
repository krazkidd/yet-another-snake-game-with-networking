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
import time # for sleep()

import curses
import curses.ascii

import SnakeCurses
import SnakeGame
import SnakeNet
from SnakeConfig import *
from SnakeEnums import *

mainSrvAddr = (HOST, SERVER_PORT)
motd = None
lobbyList = None

# the lobby server address #
lobbyAddr = None

clientState = None 

game = None

sockTimeout = None

tickTime = 0.0

def start():
    SnakeNet.InitClientSocket()
    SnakeCurses.InitClientWindow(startWithCurses)

def startWithCurses():
    global tickTime

    startMOTDMode()

    while True:
        readable, writable, exceptional = select.select([SnakeNet.sock, sys.stdin], [], [], sockTimeout)

        if SnakeNet.sock in readable:
            handleNetMessage()

        if sys.stdin in readable:
            handleInput()

        if clientState == GameState.GAME:
            tickTime += sockTimeout
            if tickTime >= 0.1:
                tickTime -= 0.1
                game.tick()
                SnakeCurses.ShowGame(game)

def quit():
    if clientState == GameState.LOBBY:
        SnakeNet.SendQuitMessageTo(lobbyAddr)
    SnakeNet.CloseSocket()

    sys.exit()

def handleNetMessage():
    global motd, lobbyList, lobbyAddr

    address, msgType, msgBody = SnakeNet.UnpackMessage()

    #TODO restructure to check sender addresses first, like SnakeGame
    if clientState == GameState.MOTD and address == mainSrvAddr:
        if msgType == MessageType.MOTD:
            motd = msgBody
            SnakeCurses.ShowMOTD(address, motd, lobbyList)
        elif msgType == MessageType.LOBBY_REP:
            lobbyList = SnakeNet.UnpackLobbyList(msgBody)
            SnakeCurses.ShowMOTD(address, motd, lobbyList)
    elif clientState == GameState.MOTD: #TODO check address == expected lobby addr
        if msgType == MessageType.LOBBY_JOIN:
            lobbyAddr = address
            startLobbyMode()
        elif msgType == MessageType.LOBBY_QUIT:
            SnakeCurses.ShowDebug('Lobby rejected your join request.')
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
        elif c in (ord('X'), ord('x')):
            SnakeNet.SendReadyMessageTo(lobbyAddr)
    elif clientState == GameState.GAME:
        if c == curses.ascii.ESC:
            #TODO make it harder to quit running game
            SnakeNet.SendQuitMessageTo(lobbyAddr)
            startMOTDMode()
        elif c in (ord('H'), ord('h'), curses.KEY_LEFT):
            game.snakes[0].changeHeading(Dir.Left)
        elif c in (ord('J'), ord('j',), curses.KEY_DOWN):
            game.snakes[0].changeHeading(Dir.Down)
        elif c in (ord('K'), ord('k',), curses.KEY_UP):
            game.snakes[0].changeHeading(Dir.Up)
        elif c in (ord('L'), ord('l',), curses.KEY_RIGHT):
            game.snakes[0].changeHeading(Dir.Right)
    elif clientState == GameState.GAME_OVER:
        if c == curses.ascii.ESC:
            startLobbyMode()

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
    global clientState, game, sockTimeout
    clientState = GameState.GAME

    #TODO get win width/height from server
    #game = SnakeGame.SnakeGame(WIN_WIDTH, WIN_HEIGHT, 1, 1)
    h, w = SnakeCurses.GetWindowSize()
    game = SnakeGame.SnakeGame(w, h, 1, 1)

    sockTimeout = 0.005

    SnakeCurses.ShowGame(game)

