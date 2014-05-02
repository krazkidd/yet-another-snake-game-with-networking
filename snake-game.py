#!/usr/bin/python2

#TODO add copyright and license info

import sys

from os.path import basename

import SnakeClient
import SnakeServer

def main():
    # get program name and fork to server or client mode
    if 'snakes' == basename(sys.argv[0]):
        SnakeServer.MainServer.start()
    elif 'snake' == basename(sys.argv[0]):
        SnakeClient.start()
    else:
        print 'Usage: This program must be called via symlink with name `snake` (client) or `snakes` (server).'

if __name__ == "__main__":
    main()
