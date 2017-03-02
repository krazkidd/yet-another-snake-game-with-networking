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

import select
import sys

from snakem.game.pellet import Pellet
from snakem.game.snake import Snake
from snakem.game.snake import SnakeAI
from snakem.enums import *

class Game:
    def __init__(self, width, height, numHumans=1, numAI=0):
        self.width = width
        self.height = height

        #TODO add pellet after snakes and make sure pellet doesn't appear
        #     on top of a snake...
        self.pellet = Pellet(1, 1, width - 1 - 1, height - 1 - 1)

        startPos = [
            (width/4, height/4),
            (width - width/4, height/4),
            (width - width/4, height - height/4),
            (width/4, height - height/4)
            ]
        startDir = [Dir.Right, Dir.Left, Dir.Left, Dir.Right]

        count = 0

        self.snakes = list()
        if numHumans >= 1:
            self.snakes.append(Snake(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1
        if numHumans >= 2:
            self.snakes.append(Snake(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1
        if numHumans >= 3:
            self.snakes.append(Snake(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1
        if numHumans >= 4:
            self.snakes.append(Snake(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1

        if numAI >= 1 and numHumans + 1 <= MAX_PLAYERS:
            self.snakes.append(SnakeAI(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1
        if numAI >= 2 and numHumans + 2 <= MAX_PLAYERS:
            self.snakes.append(SnakeAI(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1
        if numAI >= 3 and numHumans + 3 <= MAX_PLAYERS:
            self.snakes.append(SnakeAI(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1
        if numAI >= 4 and numHumans + 4 <= MAX_PLAYERS:
            self.snakes.append(SnakeAI(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1

        self.tickNum = 0

    def tick(self):
        for snake in self.snakes:
            snake.move(self.pellet)

        # check if colliding with self or any other snakes
        for snake in self.snakes:
            for otherSnake in self.snakes:
                if snake.isColl(otherSnake):
                    #TODO kill snake
                    pass

        if snake.headPos[0] in (0, self.width - 1) or snake.headPos[1] in (0, self.height - 1):
            #TODO kill snake
            pass
        elif snake.headPos == self.pellet.pos:
            self.pellet.RandomizePosition()
            snake.grow()

        self.tickNum += 1

