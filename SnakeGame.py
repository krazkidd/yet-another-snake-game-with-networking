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

from pygame import event

from Snake import *

class GameState:
    """Enum for Snake game state"""
    GAME_OVER = 1

class SnakeGame:
    def __init__(self, boardWidth, boardHeight, playersList):
        self.boardWidth = boardWidth
        self.boardHeight = boardHeight

        # instantiate players' snakes
        snake1 = Snake(15, 15, Dir.Right, 4)
        snake2 = SnakeAI(30, 30, Dir.Right, 4)
        #TODO if playersList is less than size of game, add robot players (to playersList, so the zip() works)
        #snakeAI = SnakeAI(30, 30, Dir.Right, 4)
        self.snakes = zip(playersList, (snake1, snake2))

        self.pellet = Pellet(boardWidth - 1, boardHeight - 1, 'yellow') 

        self.gameStateChanged = False
        self.tickNum = 0
    # end __init__()

    def processInput(self, direction):
FIXME
        if self.snake1.changeHeading(direction):
            self.gameStateChanged = True
    # end processInput()

#FIXME return game condition (running or game over) or report it via member variable
    def tick(self):
        for snake in self.snakes:
            # move players' snakes
            #FIXME snakes need to know positions of other snakes (at least in the local area)
            snake.move(self.pellet)

            # check for self-collision
            if snake.isColl(snake):
                print 'a snake bit itself'     

            # check if colliding with any other snakes
            #FIXME collision detection (do something better than O(n²)
            for otherSnake in self.snakes:
                if snake != otherSnake:
                    elif snake.isColl(otherSnake):
                        print 'some snake ran into another snake'     

            #TODO check if hitting the edge
            #if ...

            # check if snake is on a pellet
            if snake.headX == self.pellet.posx and snake.headY == self.pellet.posy:
                snake.length += 1
                self.pellet = Pellet(self.winWidth - 1, self.winHeight - 1, fgcolor = 'yellow')
                snake.grow()

        self.tickNum += 1
    # end tick()
# end class SnakeGame
