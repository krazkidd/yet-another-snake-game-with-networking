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

import random
from collections import deque

from SnakeEnums import *

class Pellet:

    """This is what the Snake eats.

    Holds a randomized position."""

    def __init__(self, minX, minY, maxX, maxY):

        """On creation, randomly set a position using the
        given arguments as maximum values."""

        self.__minX = minX
        self.__minY = minY
        self.__maxX = maxX
        self.__maxY = maxY

        self.RandomizePosition()

    def RandomizePosition(self):
        self.pos = (random.randint(self.__minX, self.__maxX), random.randint(self.__minY, self.__maxY))

class Snake:

    """This is the human player's avatar in the game.

    For every tick of the game world, the Snake moves. And for every
    pellet it eats, its length grows.

    """

    def __init__(self, headX, headY, heading):
        self.headPos = (headX, headY)

        if heading in (Dir.Right, Dir.Down):
            self.body = deque([
                (headX, headY),
                (headX - 1, headY),
                (headX - 2, headY),
                (headX - 3, headY)
                ])
        else: # heading in (Dir.Left, Dir.Up)
            self.body = deque([
                (headX, headY),
                (headX + 1, headY),
                (headX + 2, headY),
                (headX + 3, headY)
                ])

        self.heading = heading
        self.headingChanged = False
        self.nextHeading = None

        self.shouldGrow = False

    def grow(self):

        """Grow the Snake one segment longer.

        This is called whenever a snake eats a pellet.
        """

        # this just sets a flag so that on the next move(),
        # the last body segment won't be popped off
        self.shouldGrow = True

    def move(self, p):

        """Move (update) the snake's body.

        This should be called once for every unit
        of time that passes.
        Arguments:
        p -- a Pellet object

        """

        # check the heading of the snake and move the
        # head's position accordingly
        if self.heading == Dir.Right:
            self.headPos = (self.headPos[0] + 1, self.headPos[1])
        elif self.heading == Dir.Left:
            self.headPos = (self.headPos[0] - 1, self.headPos[1])
        elif self.heading == Dir.Up:
            self.headPos = (self.headPos[0], self.headPos[1] - 1)
        else: # self.heading == Dir.Down
            self.headPos = (self.headPos[0], self.headPos[1] + 1)

        self.body.appendleft(self.headPos)

        # pop the last body segment unless the snake is supposed to grow
        if self.shouldGrow == True:
            self.shouldGrow = False
        else:
            self.body.pop()

        if self.nextHeading:
            self.heading = self.nextHeading
            self.nextHeading = None

        self.headingChanged = False

    def changeHeading(self, newHeading):

        """Tell the Snake the new direction to move in.

        The Snake cannot go backwards, so the only real change that
        can happen is to turn left or right.

        Returns False if there was no heading change; True if there was 
        a change.

        """

        # if heading was already changed, queue the change for
        # the next move()
        if self.headingChanged:
            self.nextHeading = newHeading
            return False

        # skip if move is parallel
        if ((self.heading in (Dir.Up, Dir.Down) and newHeading in (Dir.Up, Dir.Down))
                or (self.heading in (Dir.Left, Dir.Right) and newHeading in (Dir.Left, Dir.Right))):
            return False

        self.heading = newHeading
        self.headingChanged = True
        return True

    def isColl(self, otherSnake):

        """Check if this Snake is colliding with another (or itself).

        In the snake game, we need to check if a snake's head is in
        the same position of any of its other body segments or any of
        the body segments of another snake.

        The parameter otherSnake can be a reference to self in order to
        perform collision detection on self.

        This method can only check for collisions with Snake objects, 
        not walls or other obstacles."""

        # when doing collision detection on self, we must ignore the
        # head position already in the body deque
        if self == otherSnake:
            if self.body.count(self.body[-1]) > 1: # body[-1] gets the head pos.
                return True
        else:
            if otherSnake.body.count(self.body[-1]) > 0:
                return True

        return False

class SnakeAI(Snake):

    """This is the computer's avatar in the game.

    It currently has a very rudimentary AI.

    """

    def move(self, p):

        """Move (update) the snake's body.

        This should be called once for every unit
        of time that passes.

        """

        # This AI isn't very smart. It just compares it's head position to the pellet's
        # position and decides which direction it should be going. 
        desiredDir = None
        if p.pos[0] > self.headPos[0]:
            desiredDir = Dir.Right
        elif p.pos[0] < self.headPos[0]:
            desiredDir = Dir.Left
        elif p.pos[1] < self.headPos[1]:
            desiredDir = Dir.Up
        elif p.pos[1] > self.headPos[1]:
            desiredDir = Dir.Down

        if not desiredDir == self.heading:
            if desiredDir in (Dir.Down, Dir.Up) and self.heading in (Dir.Down, Dir.Up):
                if self.headPos[1] == 1:
                    self.changeHeading(Dir.Right)
                #TODO pass gameboard instance or size so
                #     we can check height
                #elif self.headPos[1] = MAX_GAMEBOARD_WIDTH:
                #    self.changeHeading(Dir.Left)
                else:
                    if random.randint(0, 1) == 0:
                        self.changeHeading(Dir.Right)
                    else:
                        self.changeHeading(Dir.Up)
            else:
                if desiredDir in (Dir.Left, Dir.Right) and self.heading in (Dir.Left, Dir.Right):
                    if self.headPos[0] == 1:
                        self.changeHeading(Dir.Down)
                    #TODO pass gameboard instance or size so
                    #     we can check height
                    #elif self.headPos[1] = MAX_GAMEBOARD_WIDTH:
                    #    self.changeHeading(Dir.LEFT)
                    else:
                        if random.randint(0, 1) == 0:
                            self.changeHeading(Dir.Down)
                        else:
                            self.changeHeading(Dir.Up)

            self.changeHeading(desiredDir)

        Snake.move(self, p)
