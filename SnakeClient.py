import time
import os 
import socket
import sys

from struct import pack
from struct import unpack
from struct import calcsize
from select import select

import pygame
from pygame.locals import *
import pygcurse

import SnakeGame
from SnakeGame import Dir
from SnakeNet import *

# the network socket to send/receive on #
s = None
# the lobby server address #
lobbyAddr = None
# list of players that will be active during a game #
activeList = ()
# list of spectating players #
spectatingList = ()
# tells whether the player is ready to start a game or not #
isReady = False
# an instance of a running game #
game = None
# Pygcurse window object #
win = None

def init():
    global s

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def quit():
    # send QUIT message to lobby server if we're connected to one
    if lobbyAddr:
        s.sendto(pack('!BH', MessageType.LOBBY_QUIT, 3), lobbyAddr)

    s.close()
    pygame.quit()
    sys.exit()

def start():
    init()
    joinLobby()
    #TODO process lobby messages to track lobby state and print
    #TODO wait for START message
    startGame()
    quit()

def joinLobby():
    global lobbyAddr

    s.sendto(pack('!BH', MessageType.HELLO, 3), (HOST, PORT))
    #print 'Sending HELLO to server.'
    #TODO print server hostname and address. anything else?

    #FIXME allow direct connection to lobbies. if response isn't MOTD, it's a lobby

    # get MOTD
    (msg, srvaddr) = s.recvfrom(3 + MAX_MOTD_SIZE)
    print '\nMessage of the Day from server:'
    print msg[3:] + '\n'

    # get lobby info
    s.sendto(pack('!BH', MessageType.LOBBY_REQ, 3), (HOST, PORT))
    (msg, srvaddr) = s.recvfrom(MAX_MSG_SIZE)
    #TODO check size of message
    lobbyList = unpack(STRUCT_FMT_LOBBY_COUNT + STRUCT_FMT_LOBBY_LIST, msg[3:])
    print 'There are currently ' + str(lobbyList[0]) + ' lobbies:'
    for i in range(0, lobbyList[0]):
        print str(i + 1) + '. Lobby ' + str(lobbyList[1 + i * 2]) + ' on port ' + str(lobbyList[1 + i * 2 + 1])

    selection = raw_input('Which lobby would you like to join? ')

    selectedLobby = str(lobbyList[1 + (int(selection) - 1) * 2])
    selectedPort = lobbyList[1 + (int(selection) - 1) * 2 + 1]
    print 'Joining lobby number ' + selectedLobby + '.'

    # try to join lobby
    s.sendto(pack('!BH', MessageType.LOBBY_JOIN, 3), (HOST, selectedPort))

    #TODO make sure we joined successfully (listen for ACCEPT or REJECT message)

    lobbyAddr = (HOST, selectedPort)

def startGame():
    global win
    global game

    # initiate pygame and pygcurse
    os.environ['SDL_VIDEO_CENTERED'] = '1' # center window in Windows
    pygame.init()
    win = pygcurse.PygcurseWindow(WIN_WIDTH, WIN_HEIGHT, 'Snake')
    win.autoupdate = False # turn off autoupdate so window doesn't flicker

    game = SnakeGame.SnakeGame(WIN_WIDTH, WIN_HEIGHT)

    drawWindow()

    # main game loop
    while True:
        processUserInput()
        processNetMessages()

        game.tick()

        drawWindow()

        #TODO don't bother sending message more than once per tick (how to synch with server?) and only if client state changed
        # check if there is input from user
        sendNetMessages()

        # pause the screen for just a bit
        time.sleep(0.1)

def drawWindow():
    # clear the screen
    #win.erase() # this would be used instead but for a bug...
    win.fill(' ')

    # draw outside border
    #TODO

    # draw game data
    win.putchars("Score: " + str(game.snake1.length), 0, 0)

    for pos in game.snake1.body:
        # pos is a tuple (x, y)
        win.putchars('O', pos[0], pos[1], fgcolor = game.snake1.fgcolor)

    for pos in game.snakeAI.body:
        win.putchars('O', pos[0], pos[1], game.snakeAI.fgcolor)

    # draw pellet
    win.putchar('+', game.pellet.posx, game.pellet.posy, game.pellet.fgcolor)

    # actually paint the window
    win.update()

def processUserInput():
    global game

    # process input queue
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            quit()
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                game.processInput(Dir.Up)
            elif event.key == K_DOWN:
                game.processInput(Dir.Down)
            elif event.key == K_LEFT:
                game.processInput(Dir.Left)
            elif event.key == K_RIGHT:
                game.processInput(Dir.Right)

def processNetMessages():
    # NOTE: I use select because someone said it's easier than setting non-blocking mode
    readable, writable, exceptional = select([s], [], [], 0)

    while readable:
        if s in readable:
            msg, addr = s.recvfrom(MAX_MSG_SIZE)

            # only look at it if it's from the server
            if addr == lobbyAddr:
                msgType, msgLen = unpack('!BH', msg[:3])

                if msgType == MessageType.UPDATE:
                    #TODO do something
                    pass
        
        readable, writable, exceptional = select([s], [], [], 0)

def sendNetMessages():
    if game.gameStateChanged == True:
        msg = pack('!BH', MessageType.UPDATE, 3 + calcsize(STRUCT_FMT_GAME_UPDATE))
        msg += pack(STRUCT_FMT_GAME_UPDATE, game.tickNum, game.snake1.heading)
        s.sendto(msg, lobbyAddr)
        game.gameStateChanged = False
