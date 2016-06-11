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

from SnakeDebug import *

stdscr = None

_appCallback = None

_lastDebugMessage = ''

def InitClientWindow(appCallback):
    global _appCallback
    _appCallback = appCallback

    # cbreak on, echo off, keypad on, colors on
    curses.wrapper(_WrapperCallback)

def _WrapperCallback(scr):
    global stdscr
    stdscr = scr
    _appCallback()

def ShowMessage(msg):
    Erase()
    h, w = GetWindowSize()
    stdscr.addstr(h / 2, max(0, w / 2 - len(msg) / 2), msg)
    stdscr.refresh()

def ShowMOTD(host, msg):
    Erase()
    stdscr.addstr(0, 0, 'Message of the Day from ' + host + ':')
    h, w = GetWindowSize()
    stdscr.addstr(h / 2, max(0, w / 2 - len(msg) / 2), msg)
    stdscr.refresh()

def ShowDebug(msg):
    global _lastDebugMessage

    if PRINT_DEBUG:
        _lastDebugMessage = msg
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h - 1, 0, msg)
        stdscr.hline(h - 1, len(msg), '-', w - len(msg))

def GetWindowSize():
    h, w = stdscr.getmaxyx()
    if PRINT_DEBUG:
        h = h - 1
    return (h, w)

def GetKey():
    return stdscr.getch()

def Erase():
    stdscr.erase()
    ShowDebug(_lastDebugMessage)
