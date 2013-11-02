#!/usr/bin/python2

import curses
import time
from Snake import Dir

# player's snake
snakeHeadX = 15
snakeHeadY = 15
snakeHeading = Dir.Right
snakeLength = 4

def moveSnake():
	"""Move (update) the snake's body.

	This should be called once for every unit
	of time that passes."""
	global snakeHeadX, snakeHeadY, snakeHeading, snakeLength

	# check the heading of the snake and move the
	# head's position accordingly
	if snakeHeading == Dir.Right:
		snakeHeadX += 1
	elif snakeHeading == Dir.Left:
		snakeHeadX -= 1
	elif snakeHeading == Dir.Up:
		snakeHeadY -= 1
	else: # snakeHeading == Dir.Down
		snakeHeadY += 1

# initiate curses
stdscr = curses.initscr() # get window object for whole screen
curses.noecho() # turn off character echo
curses.cbreak() # get input after every keypress
curses.start_color() # for color support
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) # define a color for player's snake
stdscr.keypad(1) # return special keys as single chars
stdscr.nodelay(True)
curses.curs_set(0) # make cursor invisible

# main game loop
while True:
	# clear the screen
	stdscr.erase()

	# draw outside border
	stdscr.border()

	# draw snake
	stdscr.addch(snakeHeadY, snakeHeadX, 'O', curses.color_pair(1))

	stdscr.refresh()

	# get user input, if any
	input = stdscr.getch() 

	# change the heading of the snake according to user input
	if input == curses.KEY_UP or input == ord('w'):
		snakeHeading = Dir.Up
	elif input == curses.KEY_DOWN or input == ord('s'):
		snakeHeading = Dir.Down
	elif input == curses.KEY_LEFT or input == ord('a'):
		snakeHeading = Dir.Left
	elif input == curses.KEY_RIGHT or input == ord('d'):
		snakeHeading = Dir.Right

	# move player's snake
	moveSnake()

	# pause the screen for just a bit
	time.sleep(0.2)

# terminate curses
curses.nocbreak(); stdscr.keypad(0); curses.echo()
curses.endwin()
