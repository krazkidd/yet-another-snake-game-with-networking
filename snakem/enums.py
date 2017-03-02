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

class Dir:
    """An enum of the cardinal directions."""
    Up, Down, Left, Right = range(4)

class GameState:
    MOTD, LOBBY, GAME_SETUP, GAME, GAME_OVER = range(5)

class MsgFmt:
    # net message header
    # B: message type
    # H: length of message (including header)
    HDR = '!BH'

    # number of lobbies
    LBY_CNT = '!B'

    # info for single lobby
    # B: lobby number
    # H: port number
    LBY = '!BH'

    # game update message
    # I: tick num of update (game time elapsed)
    # B: new heading of player's snake
    GAME_UPDATE = '!IB'

class MsgType:
    """Enum for Snake network messages"""
    NONE, HELLO, MOTD, LOBBY_REQ, LOBBY_REP, LOBBY_JOIN, LOBBY_QUIT, READY, NOT_READY, START, UPDATE, CHAT, SETUP = range(13)
