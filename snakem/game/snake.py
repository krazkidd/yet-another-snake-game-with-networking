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

from collections import deque

from snakem.enums import *

class Snake:

    """This is the human player's avatar in the game.

    For every tick of the game world, the Snake moves. And for every
    pellet it eats, its length grows.

    """

    def __init__(self, headPos, heading, length=4):
        self.body = deque()

        x, y = headPos
        for i in range(length):
            if heading == Dir.Right:
                self.body.append((x - i, y))
            elif heading == Dir.Left:
                self.body.append((x + i, y))
            elif heading == Dir.Up:
                self.body.append((x, y + i))
            elif heading == Dir.Down:
                self.body.append((x, y - i))

        self.heading = heading
        self.isAlive = True

        self.__nextHeading = None
        self.__headingChanged = False
        self.__shouldGrow = False

    def grow(self):

        """Grow the Snake one segment longer.

        This is called whenever a snake eats a pellet.
        
        """

        # this just sets a flag so that on the next move(),
        # the last body segment won't be popped off
        self.__shouldGrow = True

    def move(self):

        """Move (update) the snake's body.

        This should be called once for every game tick.
        
        """

        if self.isAlive:
            x, y = self.body[0]

            # check the heading of the snake and move the
            # head's position accordingly
            if self.heading == Dir.Right:
                self.body.appendleft((x + 1, y))
            elif self.heading == Dir.Left:
                self.body.appendleft((x - 1, y))
            elif self.heading == Dir.Up:
                self.body.appendleft((x, y - 1))
            elif self.heading == Dir.Down:
                self.body.appendleft((x, y + 1))

            # pop the last body segment unless the snake is supposed to grow
            if self.__shouldGrow:
                self.__shouldGrow = False
            else:
                self.body.pop()

            if self.__nextHeading:
                self.heading = self.__nextHeading
                self.__nextHeading = None

            self.__headingChanged = False

    def changeHeading(self, newHeading):

        """Tell the Snake the new direction to move in.

        The Snake cannot go backwards, so the only real change that
        can happen is to turn left or right.

        Returns False if there was no heading change; True if there was 
        a change.

        """

        # if heading was already changed, queue the change for
        # the next move()
        if self.__headingChanged:
            self.__nextHeading = newHeading
            return False

        # skip if move is parallel
        if (self.heading in (Dir.Up, Dir.Down) and newHeading in (Dir.Up, Dir.Down)) \
           or (self.heading in (Dir.Left, Dir.Right) and newHeading in (Dir.Left, Dir.Right)):
            return False

        self.heading = newHeading
        self.__headingChanged = True

        return True
