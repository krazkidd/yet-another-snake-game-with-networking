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

# the lobby server address
lobbyAddr = None

clientState = None 

gameInstance = None

def start():
    net.InitClientSocket()
    display.InitClientWindow(startWithCurses)

def startWithCurses():
    startMOTDMode()

    tickTime = 0.0

    try:
        while True:
            net.WaitForInput(handleNetMessage, handleInput, not clientState == GameState.GAME)

            if clientState == GameState.GAME:
                tickTime += net.TIMEOUT
                if tickTime >= STEP_TIME:
                    tickTime -= STEP_TIME
                    display.ShowGame(gameInstance)
    finally:
        if lobbyAddr:
            net.SendQuitMessage(lobbyAddr)
        net.CloseSocket()

def handleNetMessage(address, msgType, msgBody):
    global motd, lobbyList

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
            handleNetMessageDuringGame(msgType, msgBody)
    elif address == mainSrvAddr:
        if clientState == GameState.MOTD:
            if msgType == MsgType.MOTD:
                motd = msgBody
                display.ShowMOTD(address, motd, lobbyList)
            elif msgType == MsgType.LOBBY_REP:
                lobbyList = net.UnpackLobbyList(msgBody)
                display.ShowMOTD(address, motd, lobbyList)

def handleNetMessageDuringGame(msgType, msgBody):
    if msgType == MsgType.SNAKE_UPDATE:
        gameInstance.UpdateSnake(net.UnpackSnakeUpdate(msgBody))
    elif msgType == MsgType.END:
        endGameMode()
        startLobbyMode()

def handleInput():
    global lobbyAddr

    c = display.GetKey()

    if clientState == GameState.MOTD:
        if c in KEYS_LOBBY_QUIT:
            sys.exit()
        elif curses.ascii.isdigit(c):
            selection = int(curses.ascii.unctrl(c))
            if 1 <= selection <= len(lobbyList):
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
        if c in KEYS_GAME_QUIT:
            #TODO make it harder to quit running game
            net.SendQuitMessage(lobbyAddr)
            startMOTDMode()
        elif c in KEYS_MV_LEFT:
            net.SendInputMessage(lobbyAddr, Dir.Left)
        elif c in KEYS_MV_DOWN:
            net.SendInputMessage(lobbyAddr, Dir.Down)
        elif c in KEYS_MV_UP:
            net.SendInputMessage(lobbyAddr, Dir.Up)
        elif c in KEYS_MV_RIGHT:
            net.SendInputMessage(lobbyAddr, Dir.Right)
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
    global clientState
    clientState = GameState.LOBBY

    display.ShowLobby()

def startGameMode():
    global clientState, gameInstance
    clientState = GameState.GAME

    #TODO get win width/height from server (and/or change display code to handle large maps)
    #gameInstance = game.Game(WIN_WIDTH, WIN_HEIGHT)
    h, w = display.GetWindowSize()
    gameInstance = game.Game(w, h)

    display.ShowGame(gameInstance)

def endGameMode():
    global gameInstance

    gameInstance = None
