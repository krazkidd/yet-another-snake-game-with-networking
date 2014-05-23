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

class Dir:
        """An enum of the cardinal directions."""
        Up, Down, Left, Right = range(4)

class Pellet:

        """This is what the Snake eats.

        For now, this just holds a position. Other attributes could
        be added in the future like power-up abilities."""

        def __init__(self, stdscr_x, stdscr_y, fgcolor = 'red', bgcolor = 'black'):
                
                """On creation, randomly set a position using the
                given arguments as maximum values."""

                self.posx = random.randint(0, stdscr_x - 1) # subtract 1 because cursor position is zero-based
                self.posy = random.randint(0, stdscr_y - 1)
		#Color
		self.fgcolor = fgcolor
		self.bgcolor = bgcolor

class Snake:

        """This is the human player's avatar in the game.

        For every tick of the game world, the Snake moves. And for every
        pellet it eats, its length grows.

        """

        def __init__(self, headX = 15, headY = 15, heading = Dir.Right, length = 4, fgcolor = 'red', bgcolor = 'black'):
                # the (X,Y) position of the snake's head
                self.headX = headX
                self.headY = headY
                # the heading of the snake
                self.heading = heading
                # the snake's body length which grows after
                # eating a pellet
                self.length = length
                #Color
                self.fgcolor = fgcolor
                self.gbcolor = bgcolor
                # store body segments as tuples (x, y)
                self.body = deque([(headX - 3, headY), (headX - 2, headY), (headX - 1, headY),(headX, headY)])
                #self.body = deque([(headX, headY), (headX - 1, headY), (headX - 2, headY),(headX - 3, headY)])
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
                        self.headX += 1
                elif self.heading == Dir.Left:
                        self.headX -= 1
                elif self.heading == Dir.Up:
                        self.headY -= 1
                else: # self.heading == Dir.Down
                        self.headY += 1

                self.body.append((self.headX, self.headY))

                # pop the last body segment unless the snake is supposed to grow
                if self.shouldGrow == True:
                        self.shouldGrow = False
                else:
                        self.body.popleft()

        def changeHeading(self, newHeading):

                """Tell the Snake the new direction to move in.

                The Snake cannot go backwards, so the only real change that
                can happen is to turn left or right.

                Returns False if there was no heading change; True if there was 
                a change.

                """

                #FIXME when changing heading, keep track of old heading until the next move()

                # don't do anything if the new heading is opposite the current heading
                if self.heading == Dir.Up and newHeading == Dir.Down:
                        return False
                elif self.heading == Dir.Down and newHeading == Dir.Up:
                        return False
                elif self.heading == Dir.Left and newHeading == Dir.Right:
                        return False
                elif self.heading == Dir.Right and newHeading == Dir.Left:
                        return False

                self.heading = newHeading
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

        def __init__(self, headX = 30, headY = 30, heading = Dir.Right, length = 4, fgcolor = 'blue', bgcolor = 'black' ):
                # the (X,Y) position of the snake's head
                self.headX = headX
                self.headY = headY
                # the heading of the snake
                self.heading = heading
                # the snake's body length which grows after
                # eating a pellet
                self.length = length
                #Color  
                self.fgcolor = fgcolor
                self.bgcolor = bgcolor
                # set up body (NOTE: we are assuming here the snake's heading is to the right)
                #self.body = deque([(headX, headY), (headX - 1, headY), (headX - 2, headY),(headX - 3, headY)])
                self.body = deque([(headX - 3, headY), (headX - 2, headY), (headX - 1, headY),(headX, headY)])
                self.shouldGrow = False

        def move(self, p):

                """Move (update) the snake's body.

                This should be called once for every unit
                of time that passes.

                """

                # This AI isn't very smart. It just compares it's head position to the pellet's
                # position and decides which direction it should be going. 
                # NOTE: There is a bug here. If a new pellet appears on the opposite side of the
                # SnakeAI's heading, it will only want to go directly backwards, which it's not
                # allowed to do.
                if p.posx > self.headX:
                        # use changeHeading() instead of manipulating heading directly
                        self.changeHeading(Dir.Right)
                elif p.posx < self.headX:
                        self.changeHeading(Dir.Left)

                #TODO this allows snake to bite itself because we actually change heading in the
                #     if block above (without actually moving the snake's body) and then change
                #     the direction back on itself here (this bug reveals itself when the snake
                #     is moving up and a new pellet appears below the Y position of the head)
                if p.posy < self.headY:
                        self.changeHeading(Dir.Up)
                elif p.posy > self.headY:
                        self.changeHeading(Dir.Down)

                # Look! We call the parent class's move() method to do the actual
                # position update. We must use Snake.move(self, ...) instead of
                # self.move(...) to do this.
                Snake.move(self, p)

