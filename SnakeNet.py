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

# NOTE: I found this interesting paper:
#   Constructing Client-Server Multi-Player Asynchronous Networked Games Using a Single-Computer Model
#     by Zimmerman et al.
#     @ URL: http://www.tffenterprises.com/~dmz/publications/conference/asyncnetgames.pdf
# It discusses how to approach turning a local multiplayer game to a networked one and uses Tron
#   specifically as an example. My net code should implement something very similar to what
#   they describe.

#FIXME allow host and port config from command line. what if port is appended to hostname?
HOST = ''
PORT = 11845

MAX_MSG_SIZE = 1024 # could go up to 1500? (well, could go up to max IP limit, technically)
#FIXME MAX_MOTD_SIZE should not exceed MAX_MSG_SIZE + header size (currently 3 bytes)
MAX_MOTD_SIZE = 1024

MAX_LOBBY_SIZE = 8

# these dimension units are in text cells, not pixels
WIN_WIDTH, WIN_HEIGHT = 60, 35

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

# NOTE: https://docs.python.org/2/library/socketserver.html#module-SocketServer
#       says something about using threads because Python networking may be slow

class MessageType:
    """Enum for Snake network messages"""
    HELLO, MOTD, LOBBY_REQ, LOBBY_REP, LOBBY_JOIN, LOBBY_QUIT, READY, NOT_READY, START, UPDATE, CHAT = range(1, 12)
