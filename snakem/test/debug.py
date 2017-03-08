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

import datetime
import sys

from snakem.enums import MsgType

name = 'None'

doPrintDebug = False
doPrintError = False
doPrintNetMsg = False

netMsgNames = dict([(MsgType.NONE, "None"), (MsgType.HELLO, "Hello"), (MsgType.MOTD, "MOTD"), (MsgType.LOBBY_REQ, "Lobby request"),
                    (MsgType.LOBBY_REP, "Lobby reply"), (MsgType.LOBBY_JOIN, "Lobby join"), (MsgType.LOBBY_QUIT, "Lobby quit"), (MsgType.READY, "Ready"),
                    (MsgType.NOT_READY, "Not ready"), (MsgType.START, "Start"), (MsgType.END, "End"), (MsgType.SNAKE_UPDATE, "Snake update"),
                    (MsgType.SETUP, "Setup"), (MsgType.INPUT, "Input")])

def init_debug(nm, debug, error, netMsg):
    global name, doPrintDebug, doPrintError, doPrintNetMsg

    name = str(nm)
    doPrintDebug = debug
    doPrintError = error
    doPrintNetMsg = netMsg

def print_debug(msg):
    if doPrintDebug:
        print 'DEBUG (' + datetime.datetime.now().strftime("%H:%M:%S") + ') ' + name + ': ' + str(msg)

def print_err(msg):
    if doPrintError:
        print 'ERROR (' + datetime.datetime.now().strftime("%H:%M:%S") + ') ' + name + ' (line ' + str(sys.exc_info()[-1].tb_lineno) + '): ' + str(msg)

def print_net_msg(address, msgType, msgBody):
    if doPrintNetMsg:
        if msgType in netMsgNames:
            msgTypeStr = netMsgNames[msgType]
        else:
            msgTypeStr = 'Unknown type'

        if msgBody:
            print 'NETMSG (' + address[0] + ') ' + name + ': <' + msgTypeStr + '> Body length: ' + str(len(msgBody))
        else:
            print 'NETMSG (' + address[0] + ') ' + name + ': <' + msgTypeStr + '>'