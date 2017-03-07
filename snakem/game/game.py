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

from snakem.game.pellet import Pellet
from snakem.game.snake import Snake
from snakem.enums import *

class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.snakes = dict()
        self.pellet = None

        self.tickNum = 0

    def tick(self):
        # move all snakes before checking collisions
        for snake in self.snakes.itervalues():
            snake.move()

        for snake in self.snakes.itervalues():
            # check with other snakes
            for otherSnake in self.snakes.itervalues():
                if snake is not otherSnake and snake.body[0] in otherSnake.body:
                    snake.isAlive = False

            x, y = snake.body[0]
            # check boundaries
            if x in (0, self.width - 1) or y in (0, self.height - 1):
                snake.isAlive = False
            # check pellet
            elif snake.body[0] == self.pellet.pos:
                snake.grow()
                self.SpawnNewPellet()

        self.tickNum += 1

    def SpawnNewSnake(self, id=None):
        # NOTE: Only 4 snakes are supported.

        if id is None:
            id = len(self.snakes)

            if not id < 4:
                return None

        startPos = [
            (self.width / 4, self.height / 4),
            (self.width - self.width / 4, self.height / 4),
            (self.width - self.width / 4, self.height - self.height / 4),
            (self.width / 4, self.height - self.height / 4)
        ]
        startDir = [Dir.Right, Dir.Left, Dir.Left, Dir.Right]

        self.snakes[id] = Snake(startPos[id], startDir[id])

        return id

    def SpawnNewPellet(self):
        self.pellet = Pellet(1, 1, self.width - 1 - 1, self.height - 1 - 1)

        # make sure pellet doesn't appear on top of a snake...
        isGoodPos = False
        while not isGoodPos:
            for snake in self.snakes.itervalues():
                if self.pellet.pos in snake.body:
                    self.pellet.RandomizePosition()
                    break
            else:
                isGoodPos = True

    def UpdateSnake(self, id, heading, isAlive, body):
        if id not in self.snakes:
            # just add the snake, I guess?
            self.SpawnNewSnake(id)

        s = self.snakes[id]
        s.heading = heading
        s.isAlive = isAlive
        s.body = body