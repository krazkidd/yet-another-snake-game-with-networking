#!/usr/bin/python2

import time
import sys
import os 

import pygame
from pygame.locals import *
import pygcurse

from Snake import *
from Pellet import *

# these dimension units are in text cells, not pixels
WIN_WIDTH, WIN_HEIGHT = 60, 35

# instantiate players' snakes
snake1 = Snake(15, 15, Dir.Right, 4)
snakeAI = SnakeAI(30, 30, Dir.Right, 4)

pellet = Pellet(WIN_WIDTH - 1, WIN_HEIGHT - 1) 

# initiate pygame and pygcurse
os.environ['SDL_VIDEO_CENTERED'] = '1' # center window in Windows
pygame.init()
win = pygcurse.PygcurseWindow(WIN_WIDTH, WIN_HEIGHT, 'Snake')
win.autoupdate = False # turn off autoupdate so window doesn't flicker

# main game loop
while True:
	# clear the screen
	#win.erase() # this would be used instead but for a bug...
	win.fill(' ')

	# draw outside border
#TODO

	# draw game data
	win.putchars("Score: " + str(snake1.length), 0, 0)

	# draw snakes
	win.putchars('O', snake1.headX, snake1.headY, fgcolor = 'red', bgcolor = 'black')
	win.putchars('O', snake_ai.headX, snake_ai.headY, fgcolor = 'blue', bgcolor = 'black')

	# draw pellet
	win.putchar('+', pellet.posx, pellet.posy, fgcolor = 'yellow', bgcolor = 'black')

	# actually paint the window
	win.update()

	# pause the screen for just a bit
	time.sleep(0.1)

	# process input queue
	for event in pygame.event.get():
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_UP:
				snake1.changeHeading(Dir.Up)
			elif event.key == K_DOWN:
				snake1.changeHeading(Dir.Down)
			elif event.key == K_LEFT:
				snake1.changeHeading(Dir.Left)
			elif event.key == K_RIGHT:
				snake1.changeHeading(Dir.Right)

	# move players' snakes
	snake1.move(pellet)
	#Snake.move(snake1) # an alternative way to call a particular object's method
	snakeAI.move(pellet)	
	
	# check if player's head is on a pellet. If so, consume it and create a new one
	if snake1.headX == pellet.posx and snake1.headY == pellet.posy:
		snake1.length += 1
		pellet = Pellet(WIN_WIDTH - 1, WIN_HEIGHT - 1)

	# (SnakeAI) check if player's head is on a pellet. If so, consume it and create a new one
	elif snakeAI.headX == pellet.posx and snakeAI.headY == pellet.posy:
		snakeAI.length += 1
		pellet = Pellet(WIN_WIDTH - 1, WIN_HEIGHT - 1)

#TODO check if player has hit the edge and end the game if so
	#if ...
