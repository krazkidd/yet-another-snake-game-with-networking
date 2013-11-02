#!/usr/bin/python2

import curses
import time
from Snake import *

# initiate curses
stdscr = curses.initscr() # get window object for whole screen
curses.noecho() # turn off character echo
curses.cbreak() # get input after every keypress
stdscr.keypad(1) # return special keys as single chars
stdscr.nodelay(True)
curses.curs_set(0) # make cursor invisible

# instantiate player's snake
snake = Snake()
#snake2 = Snake()

# main game loop
while True:
	# clear the screen
	stdscr.erase()

	# draw outside border
	stdscr.border()

	# draw snake
	stdscr.addch(snake.headY, snake.headX, 'O', curses.COLOR_RED)
	#stdscr.addch(snake2.headY, snake2.headX, 'O', curses.COLOR_GREEN)

	stdscr.refresh()

	# get user input, if any
	input = stdscr.getch() 

	# change the heading of the snake according to user input
	if input == curses.KEY_UP or input == ord('w'):
		snake.heading = Dir.Up
	elif input == curses.KEY_DOWN or input == ord('s'):
		snake.heading = Dir.Down
	elif input == curses.KEY_LEFT or input == ord('a'):
		snake.heading = Dir.Left
	elif input == curses.KEY_RIGHT or input == ord('d'):
		snake.heading = Dir.Right

	# pause the screen for just a bit
	time.sleep(0.2)
	
	# move player's snake
	snake.move()
	#snake2.move()
	#Snake.move(snake) # an alternative way to call a particular object's method

# terminate curses
curses.nocbreak(); stdscr.keypad(0); curses.echo()
curses.endwin()
