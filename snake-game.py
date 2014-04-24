#!/usr/bin/python2

#TODO add copyright and license info

import time
import sys
import os 
import socket

import pygame
from pygame.locals import *
import pygcurse

from Snake import *

HOST = '' # any network interface
PORT = 11845 #FIXME allow port config from command line

def main():
    # get program name and fork to server or client mode
    #FIXME this only works when you explicitly run python interpreter and not the script file
    if 'snakes' == sys.argv[0]:
        doServerStuff()
    if 'snake' == sys.argv[0]:
        doClientStuff()

def doServerStuff():
    # NOTE: https://docs.python.org/2/library/socketserver.html#module-SocketServer
    #       says something about using threads because Python networking may be slow

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
    #s.listen(5) # argument is size of connection backlog
    print 'Game has started. Waiting for messages...'

    #FIXME need to come up with network message scheme
    # wait for connection
    while 1:
        data, addr = s.recvfrom(1024)
        print data

def doClientStuff():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((HOST, PORT))

    # these dimension units are in text cells, not pixels
    WIN_WIDTH, WIN_HEIGHT = 60, 35

    # instantiate players' snakes
    snake1 = Snake(15, 15, Dir.Right, 4)
    snakeAI = SnakeAI(30, 30, Dir.Right, 4)

    pellet = Pellet(WIN_WIDTH - 1, WIN_HEIGHT - 1, 'yellow') 

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
        for pos in snake1.body:
            # pos is a tuple (x, y)
            win.putchars('O', pos[0], pos[1], fgcolor = snake1.fgcolor)

        for pos in snakeAI.body:
            win.putchars('O', pos[0], pos[1], snakeAI.fgcolor)

        # draw pellet
        win.putchar('+', pellet.posx, pellet.posy, pellet.fgcolor)

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
            pellet = Pellet(WIN_WIDTH - 1, WIN_HEIGHT - 1, fgcolor = 'yellow')
            snake1.grow()
            s.sendall('Player 1 score:' + str(snake1.length))

        # (SnakeAI) check if player's head is on a pellet. If so, consume it and create a new one
        elif snakeAI.headX == pellet.posx and snakeAI.headY == pellet.posy:
            snakeAI.length += 1
            pellet = Pellet(WIN_WIDTH - 1, WIN_HEIGHT - 1, 'yellow')
            snakeAI.grow()
            s.sendall('SnakeAI score:' + str(snakeAI.length))

        # check if any snakes are colliding with any other snakes
        #if snake1.isColl((snake1.headX, snake1.headY)): # previous use of Snake.isColl()
        if snake1.isColl(snake1):
            print 'snake1 bit itself'     
        elif snake1.isColl(snakeAI):
            print 'snake1 ran into the other snake'     

        if snakeAI.isColl(snakeAI):
            print 'snakeAI bit itself'
        elif snakeAI.isColl(snake1):
            print 'snakeAI ran into the other snake'     

        #TODO check if any snakes have hit the edge
        #if ...

def initClient():
    pass

if __name__ == "__main__":
    main()
