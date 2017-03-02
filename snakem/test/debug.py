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

PRINT_DEBUG = True
PRINT_ERROR = True

def print_debug(name, msg):
    if PRINT_DEBUG:
        print 'DEBUG (' + datetime.datetime.now().strftime("%H:%M:%S") + ') ' + str(name) + ': ' + str(msg)

def print_err(name, msg):
    if PRINT_ERROR:
        print 'ERROR (' + datetime.datetime.now().strftime("%H:%M:%S") + ') ' + str(name) + ' (line ' + str(sys.exc_info()[-1].tb_lineno) + '): ' + str(msg)

