#!/usr/bin/python2

#TODO add copyright and license info

import time
import sys
import os 
from os.path import basename
import socket

import pygame
from pygame.locals import *
import pygcurse

from Snake import *

#FIXME allow host and port config from command line. what if port is appended to hostname?
HOST = '' # any network interface
PORT = 11845

def main():
    # get program name and fork to server or client mode
    if 'snakes' == basename(sys.argv[0]):
        doMainServerStuff()
    if 'snake' == basename(sys.argv[0]):
        doClientStuff()

def doMainServerStuff():
    connectNum = 1

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5) # argument is size of connection backlog
    print 'Server has started on port ' + str(PORT) + '. Waiting for clients...'

    # wait for connection
    while 1:
        (clientsocket, address) = s.accept()
        pid = os.fork()
        if (0 == pid):
            #FIXME test that we can open the port first! (main server must not be in charge of connectNum--but we have to use a mutex if we increment it here in lobby server)
            print 'Client connected. Sending to game lobby ' + str(connectNum) + '.'

            # before moving to new socket, tell client lobby port
            clientsocket.send(str(PORT + connectNum))
            clientsocket.shutdown(socket.SHUT_RDWR)
            clientsocket.close()
            s.close()

            # NOTE: we have to open a new listening socket so client sees an open connection
            # bind socket to UDP port
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind((HOST, PORT + connectNum))

            doLobbyServerStuff(s, connectNum)
            print 'Lobby server ' + str(connectNum) + ' is closing.'
            break #FIXME find cleaner way for lobby servers to break loop?
        else:
            connectNum = connectNum + 1
            continue

def doLobbyServerStuff(s, clientNo):
    # NOTE: https://docs.python.org/2/library/socketserver.html#module-SocketServer
    #       says something about using threads because Python networking may be slow

    # wait for connection
    #FIXME this needs to die eventually; add flag
    while 1:
        #TODO process whole network queue
        data, addr = s.recvfrom(1024)
        # need to verify sender address? session could easily be clobbered if not
        print data

def doClientStuff():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print 'Connected to server.'

    #FIXME get lobby info
    lobbyPort = int(s.recv(8))
    print 'Joining lobby number ' + str(lobbyPort)

    # move to UDP port for game
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.connect((HOST, lobbyPort))

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
    #FIXME client should go back to lobby after game is over
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
            s.sendto('Player 1 score:' + str(snake1.length), (HOST, lobbyPort))
        # (SnakeAI) check if player's head is on a pellet. If so, consume it and create a new one
        elif snakeAI.headX == pellet.posx and snakeAI.headY == pellet.posy:
            snakeAI.length += 1
            pellet = Pellet(WIN_WIDTH - 1, WIN_HEIGHT - 1, 'yellow')
            snakeAI.grow()
            s.sendto('SnakeAI score:' + str(snakeAI.length), (HOST, lobbyPort))

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

if __name__ == "__main__":
    main()
