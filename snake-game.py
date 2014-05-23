#!/usr/bin/python2
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

from os.path import basename

import SnakeClient
import SnakeServer

def main():
    # get program name and fork to server or client mode
    if 'snakes' == basename(sys.argv[0]):
        SnakeServer.MainServer.start()
    elif 'snake' == basename(sys.argv[0]):
        SnakeClient.start()
    else:
        print 'Usage: This program must be called via symlink with name `snake` (client) or `snakes` (server).'

if __name__ == "__main__":
    main()
