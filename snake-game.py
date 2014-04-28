#!/usr/bin/python2

#TODO add copyright and license info

from os.path import basename

from SnakeNet import *

def main():
    # get program name and fork to server or client mode
    if 'snakes' == basename(sys.argv[0]):
        MainServer.start()
    elif 'snake' == basename(sys.argv[0]):
        Client.start()
    else:
        print 'Usage: This program must be called via symlink with name `snake` (client) or `snakes` (server).'

if __name__ == "__main__":
    main()
