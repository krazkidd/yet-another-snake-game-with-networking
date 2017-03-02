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

################ CLIENT CONFIG VARS ################

# which server to connect to
HOST = '127.0.0.1'

# key bindings
KEYS_LOBBY_QUIT = (ord('Q'), ord('q'), curses.ascii.ESC)
KEYS_LOBBY_REFRESH = (ord('R'), ord('r'))
KEYS_LOBBY_READY = (ord('X'), ord('x'))
#KEYS_LOBBY_1PLAYER = (ord('Y'), ord('y'))

KEYS_GAME_QUIT = (curses.ascii.ESC)

KEYS_MV_LEFT = (ord('H'), ord('h'), curses.KEY_LEFT)
KEYS_MV_DOWN = (ord('J'), ord('j',), curses.KEY_DOWN)
KEYS_MV_UP = (ord('K'), ord('k',), curses.KEY_UP)
KEYS_MV_RIGHT = (ord('L'), ord('l',), curses.KEY_RIGHT)

################ SERVER CONFIG VARS ################

# the port the server binds to
SERVER_PORT = 11845

# welcome message for new clients
MOTD = 'Welcome to my Snake-M development server!'

# number of lobby servers to spawn
NUM_LOBBIES = 5


########## (SERVER ONLY) GAME CONFIG VARS ##########

# game window dimensions (units are text cells)
WIN_WIDTH, WIN_HEIGHT = 60, 35


################# GAME CONFIG VARS #################

# how often to advance the game state #
STEP_TIME = 0.1

MAX_PLAYERS = 4

