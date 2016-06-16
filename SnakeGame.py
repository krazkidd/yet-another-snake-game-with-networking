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

import curses
import curses.ascii

import Snake
import SnakeNet
from SnakeEnums import *

MAX_PLAYERS = 4

class SnakeGame:
    def __init__(self, width, height, numHumans=1, numAI=0):
        self.width = width
        self.height = height

        #TODO add pellet after snakes and make sure pellet doesn't appear
        #     on top of a snake...
        self.pellet = Snake.Pellet(1, 1, width - 1 - 1, height - 1 - 1)

        startPos = [
            (width/4, height/4),
            (width - width/4, height/4),
            (width/4, height - height/4),
            (width - width/4, height - height/4)
            ]
        startDir = [Dir.Right, Dir.Down, Dir.Left, Dir.Up]

        count = 0

        self.snakes = list()
        if numHumans >= 1:
            self.snakes.append(Snake.Snake(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1
        if numHumans >= 2:
            self.snakes.append(Snake.Snake(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1
        if numHumans >= 3:
            self.snakes.append(Snake.Snake(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1
        if numHumans >= 4:
            self.snakes.append(Snake.Snake(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1

        if numAI >= 1 and numHumans + 1 <= MAX_PLAYERS:
            self.snakes.append(Snake.SnakeAI(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1
        if numAI >= 2 and numHumans + 2 <= MAX_PLAYERS:
            self.snakes.append(Snake.SnakeAI(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1
        if numAI >= 3 and numHumans + 3 <= MAX_PLAYERS:
            self.snakes.append(Snake.SnakeAI(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1
        if numAI >= 4 and numHumans + 4 <= MAX_PLAYERS:
            self.snakes.append(Snake.SnakeAI(startPos[count][0], startPos[count][1], startDir[count]))
            count += 1

        self.tickNum = 0

    def input(self, snakeIndex, dir):
        self.snakes[snakeIndex].changeHeading(dir)

    def tick(self):
        for snake in self.snakes:
            snake.move(self.pellet)

            # check for self-collision
            if snake.isColl(snake):
                #TODO kill snake
                pass

            # check if colliding with any other snakes
            #FIXME collision detection (do something better than O(n²)
            for otherSnake in self.snakes:
                if snake != otherSnake:
                    if snake.isColl(otherSnake):
                        #TODO kill snake
                        pass

            #TODO check if hitting the edge
            if snake.headPos[0] in (0, self.width) or snake.headPos[1] in (0, self.height):
                #TODO kill snake
                pass

            # check if snake is on a pellet
            if snake.headPos == self.pellet.pos:
                self.pellet.RandomizePosition()
                snake.grow()

        self.tickNum += 1

