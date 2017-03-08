import curses
import curses.ascii

# the address of the main server to connect to
SERVER_ADDR = ('127.0.0.1', 11845)

# how often to advance the game state
STEP_TIME = 0.1

############ KEY BINDINGS ############

KEYS_LOBBY_QUIT = (ord('Q'), ord('q'), curses.ascii.ESC)
KEYS_LOBBY_REFRESH = (ord('R'), ord('r'))
KEYS_LOBBY_READY = (ord('X'), ord('x'))
#KEYS_LOBBY_1PLAYER = (ord('Y'), ord('y'))

KEYS_GAME_QUIT = (curses.ascii.ESC, )

KEYS_MV_LEFT = (ord('H'), ord('h'), curses.KEY_LEFT)
KEYS_MV_DOWN = (ord('J'), ord('j',), curses.KEY_DOWN)
KEYS_MV_UP = (ord('K'), ord('k',), curses.KEY_UP)
KEYS_MV_RIGHT = (ord('L'), ord('l',), curses.KEY_RIGHT)

################ DEBUG ###############

PRINT_DEBUG = True
PRINT_ERROR = True
PRINT_NETMSG = False