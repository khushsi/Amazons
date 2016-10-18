# CS1571 -- Assignment #3: El Juego de las Amazonas in Python 2.7
# For more information about the game itself, please refer to:
#      http://en.wikipedia.org/wiki/Game_of_the_Amazons
#
# This file provides some basic support for you to develop your automatic Amazons player.
# It gives everyone a common starting point, and it will make it easier for us to set your players
# to play against each other. Therefore, you should NOT make any changes to the provided code unless
# directed otherwise. If you find a bug, please email me.

# This implementation includes two class definitions, some utility functions,
# and a function for a human player ("human").
# The two classes are:
# - The Amazons class: the main game controller
# - The Board class: contains info about the current board configuration.
#   It is through the Board class that the game controller
#   passes information to your player function.
# More details about these two classes are provided in their class definitions

# Your part: Write an automatic player function for the Game of the Amazons.
# * your automatic player MUST have your email userID as its function name (e.g., reh23)
# * The main game controller will call your function at each turn with
#   a copy of the current board as the input argument.  
# * Your function's return value should be your next move.
#   It must be expressed as a tuple of three tuples: e.g., ((0, 3), (1,3), (8,3)) 
#    - the start location of the queen you want to move (in row, column)
#    - the queen's move-to location,
#    - the arrow's landing location.
#   If you have no valid moves left, the function should return False.

# As usual, we won't spend much time on the user interface. 
# Updates of the game board are drawn with simple ascii characters.
#
# - Below is a standard initial board configuration:
#   * The board is a 10x10 grid. (It is advisable to use a smaller board during development/debugging)
#   * Each side has 4 queens. The white queens are represented as Q's; the black queens are represented as q's
#
#      a b c d e f g h i j
#   9  . . . q . . q . . . 
#   8  . . . . . . . . . . 
#   7  . . . . . . . . . . 
#   6  q . . . . . . . . q 
#   5  . . . . . . . . . . 
#   4  . . . . . . . . . . 
#   3  Q . . . . . . . . Q 
#   2  . . . . . . . . . . 
#   1  . . . . . . . . . . 
#   0  . . . Q . . Q . . . 
#
# - During a player's turn, one of the player's queens must be moved, then an arrow must be shot from the moved queen.
# - the arrow is represented as 'x'
# - neither the queens nor their arrows can move past another queen or an arrow
#
# - The objective of the game is to minimze your opponent's queens' movement.
# - The game technically ends when one side's queens have no more legal moves,
#   but the game practically ends when the queens from the two sides have been
#   segregated. We will just count up the territories owned by each side and
#   the side with the larger territory will be declared the winner

############################################

import copy, random, re, time, sys
from warnings import catch_warnings

# The Amazons class controls the flow of the game.
# Its data include:
# * size -- size of board: assume it's <= 10
# * time_limit -- # of seconds a mchine is allowed to take (<30)
# * playerW -- name of the player function who'll play white
# * playerB -- name of the player function who'll play black
# * wqs -- initial positions of the white queens
# * bqs -- initial positions of the black queens
# * board -- current board configuration (see class def for Board)
# Its main functions are:
# * play: the main control loop of a game, which would:
#   - turn taking management: calls each auto player's minimax function (or "human")
#   - check for the validity of the player's move:
#     an auto player loses a turn if an invalid move is returned or if it didn't return a move in the alloted time  
#   - check for end game condition 
#   - declare the winner
# * update: this function tries out the move on a temporary board.
#   if the move is valid, the real board will be updated.
# * end_turn: just get the score from the board class

class Amazons:
    def __init__(self, fname):
        fin = open(fname, 'r')
        self.time_limit = int(fin.readline())
        self.size = int(fin.readline())
        self.playerW = fin.readline().strip()
        self.wqs = tuple(map(ld2rc,fin.readline().split()))
        self.playerB = fin.readline().strip()
        self.bqs  = tuple(map(ld2rc,fin.readline().split()))
        self.board = Board(self.size, self.wqs, self.bqs)

    def update(self, move):
        try:
            (src,dst,adst) = move
        except: return False

        # try out the move on a temp board        
        tmp_board = copy.deepcopy(self.board)
        if tmp_board.valid_path(src,dst):
            tmp_board.move_queen(src,dst)
            if tmp_board.valid_path(dst, adst):
                # the move is good. make the real board point to it
                tmp_board.shoot_arrow(adst)
                del self.board
                self.board = tmp_board
                return True
        # move failed. 
        del tmp_board
        return False

    def end_turn(self):
        return self.board.end_turn()

    def play(self):
        bPlay = True
        wscore = bscore = 0
        white = False
        while (bPlay):
            for p in [self.playerW, self.playerB]:
                # send player a copy of the current board
                tmp_board = copy.deepcopy(self.board)
                if(white == False):
                    white = True
                else:
                    white = False
                        
                tstart = time.clock()
                tmp_board.time_limit = tstart+self.time_limit
                tmp_board.bWhite=white
                move = eval("%s(tmp_board)"%p)
                tstop = time.clock()
                del tmp_board

                if move:
                    print p,": move:", [rc2ld(x) for x in move],"time:", tstop-tstart, "seconds"
                else: 
                    print p,"time:", tstop-tstart, "seconds"
                    # if move == False --> player resigned   
                    if self.board.bWhite:
                        (wscore, bscore) = (-1,0)
                    else: (wscore, bscore) = (0,-1)
                    bPlay = False
                    break

                # only keep clock for auto players
                if p != "human" and (tstop - tstart) > self.time_limit:
        
                    print p, ": took too long -- lost a turn"
                elif not self.update(move):
                    print p, ": invalid move", move, " lost a turn"

                # at the end of the turn, check whether the game ended
                # and update whether white is playing next
                (wscore, bscore) = self.end_turn()
                if wscore and bscore:
                    continue
                else:
                    bPlay = False
                    break
        # print final board
        self.board.print_board()
        if wscore == -1:
            print self.playerW,"(white) resigned.", self.playerB,"(black) wins"
        elif bscore == -1:
            print self.playerB,"(black) resigned.", self.playerW,"(white) wins"
        elif not wscore:
            print self.playerB,"(black) wins by a margin of",bscore
        else: print self.playerW, "(white) wins by a margin of",wscore
                
        
##############################################
# The Board class stores basic information about the game configuration.
# 
# NOTE: The amount of info stored in this class is kept to a minimal. This
# is on purpose. This is just set up as a way for the game controller to
# pass information to your automatic player. Although you cannot change
# the definition of the Board class, you are not constrained to use the
# Board class as your main state reprsentation. You can define your own
# State class and copy/transform from Board the info you need.

# The Board class contains the following data:
#  * config: the board configuration represented as a list of lists.
#    The assumed convention is (row, column) so config[0][1] = "b0"
#  * bWhite: binary indicator -- True if it's white's turn to play
#  * time_limit: deadline for when a move must be returned by
# The Board class supports the following methods:
#  * print_board: prints the current board configuration
#  * valid_path: takes two location tuples (in row, column format) and returns 
#    whether the end points describe a valid path (for either the queen or the arrow)
#  * move_queen: takes two location tuples (in row, column format)
#    and updates the board configuration to reflect the queen moving
#    from src to dst
#  * shoot_arrow: takes one location tuple (in row, column format)
#    and updates the board configuration to include the shot arrow
#  * end_turn: This function does some end of turn accounting: update whose
#    turn it is and determine whether the game ended
#  * count_areas: This is a helper function for end_turn. It figures out
#    whether we can end the game
class Board:
    def __init__(self, size, wqs, bqs):
        self.time_limit = None
        self.bWhite = True
        self.config = [['.' for c in range(size)] for r in range(size)]
        for (r,c) in wqs:
            self.config[r][c] = 'Q'
        for (r,c) in bqs:
            self.config[r][c] = 'q'
            
    def print_board(self):
        size = len(self.config)
        print ("     Black")
        tmp = "  "+" ".join(map(lambda x: chr(x+ord('a')),range(size)))
        print (tmp)
        for r in range(size-1, -1, -1):
            print r, " ".join(self.config[r]), r
        print (tmp)
        print ("     White\n")

    def valid_path(self, src, dst):
        (srcr, srcc) = src
        (dstr, dstc) = dst        

        srcstr = rc2ld(src)
        dststr = rc2ld(dst)

        symbol = self.config[srcr][srcc]
        if (self.bWhite and symbol != 'Q') or (not self.bWhite and symbol != 'q'):
            print "invalid move: cannot find queen at src:",srcstr
            return False

        h = dstr-srcr
        w = dstc-srcc
        if h and w and abs(h/float(w)) != 1: 
            print("invalid move: not a straight line")
            return False
        if not h and not w:
            print("invalid move: same start-end")
            return False

        if not h:
            op = (0, int(w/abs(w)))
        elif not w:
            op = (int(h/abs(h)),0)
        else:
            op = (int(h/abs(h)),int(w/abs(w)))

        (r,c) = (srcr,srcc)
        while (r,c) != (dstr, dstc):
            (r,c) = (r+op[0], c+op[1])
            if (self.config[r][c] != '.'):
                print "invalid move: the path is not cleared between",srcstr,dststr
                return False
        return True

    def move_queen(self, src, dst):
        self.config[dst[0]][dst[1]] = self.config[src[0]][src[1]]
        self.config[src[0]][src[1]] = '.'

    def shoot_arrow(self, dst):
        self.config[dst[0]][dst[1]] = 'x'

    def end_turn(self):
        # count up each side's territories
        (w,b) = self.count_areas()
        # if none of the queens of either side can move, the player who just
        # played wins, since that player claimed the last free space.
        if b == w and b == 0:
            if self.bWhite: w = 1
            else: b = 1
        # switch player
        self.bWhite = not self.bWhite
        return (w,b)

    # adapted from standard floodfill method to count each player's territories
    # - if a walled-off area with queens from one side belongs to that side
    # - a walled-off area with queens from both side is neutral
    # - a walled-off area w/ no queens is deadspace
    def count_areas(self):
        # replace all blanks with Q/q/n/-
        def fill_area(replace):
            count = 0
            for r in range(size):
                for c in range(size):
                    if status[r][c] == '.':
                        count+=1
                        status[r][c] = replace
            return count
        
        # find all blank cells connected to the seed blank at (seedr, seedc) 
        def proc_area(seedr,seedc):
            symbols = {} # keeps track of types of symbols encountered in this region
            connected = [(seedr,seedc)] # a stack for df traversal on the grid
            while connected:
                (r, c) = connected.pop()
                status[r][c] = '.'
                for ops in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                    (nr, nc) = (r+ops[0], c+ops[1])
                    if nr < 0 or nr >= size or nc < 0 or nc >= size:
                        continue
                    # if it's a new blank, need to process it; also add to seen
                    if self.config[nr][nc] == '.' and status[nr][nc] == '?':
                        status[nr][nc] = '.'
                        connected.append((nr,nc))
                    # if it's a queen or an arrow; just mark as seen
                    elif self.config[nr][nc] != '.': 
                        status[nr][nc] = 'x'
                        symbols[self.config[nr][nc]] = 1

            if 'Q' in symbols and not 'q' in symbols: # area belongs to white
                return (fill_area('Q'), 0, 0)
            elif 'q' in symbols and not 'Q' in symbols: #area belongs to black
                return (0, fill_area('q'),0)
            elif 'q' in symbols and 'Q' in symbols: # area is neutral
                return (0, 0, fill_area('n'))
            else: # deadspace -- still have to fill but don't return its area value
                fill_area('-')
                return (0,0,0)

        size = len(self.config)
        # data structure for keeping track of seen locations
        status = [['?' for i in range(size)] for j in range(size)]
        wtot = btot = ntot = 0
        for r in range(size):
            for c in range(size):            
                # if it's an empty space and we haven't seen it before, process it
                if self.config[r][c] == '.' and status[r][c] == '?':
                    (w,b,n) = proc_area(r,c)
                    wtot += w
                    btot += b
                    ntot += n
                # if it's anything else, but we haven't seen it before, just mark it as seen and move on
                elif status[r][c] == '?':
                    status[r][c] = 'x'
                    
        if ntot == 0: # no neutral space left -- should end game
            if wtot > btot:
                return (wtot-btot, 0)
            else: return (0, btot-wtot)
        else: return (wtot+ntot, btot+ntot)

# utility functions:
# ld2rc -- takes a string of the form, letter-digit (e.g., "a3")
# and returns a tuple in (row, column): (3,0)
# rc2ld -- takes a tuple of the form (row, column) -- e.g., (3,0)
# and returns a string of the form, letter-digit (e.g., "a3")

def ld2rc(raw_loc):
    return (int(raw_loc[1]), ord(raw_loc[0])-ord('a'))
def rc2ld(tup_loc):
    return chr(tup_loc[1]+ord('a'))+str(tup_loc[0])

# get next move from a human player
# The possible return values are the same as an automatic player:
# Usually, the next move should be returned. It must be specified in the following format:
# [(queen-start-row, queen-start-col), (queen-end-row,queen-end-col), (arrow-end-row, arrow-end-col)]
# To resign from the game, return False

def human(board):

    board.print_board()

    if board.bWhite:
        print("You're playing White (Q)")
    else:
        print("You're playing Black (q)")

    print("Options:")
    print('* To move, type "<loc-from> <loc-to>" (e.g., "a3-d3")')
    print('* To resign, type "<return>"')
    while True: # loop to get valid queen move from human
        while True: # loop to check for valid input syntax first
            raw_move = raw_input("Input please: ").split()
            if not raw_move: # human resigned
                return False
            # if they typed "a3-d3"
            elif re.match("^[a-j][0-9]\-[a-j][0-9]$",raw_move[0]):
                break
            else: print str(raw_move),"is not a valid input format"
        (src, dst) = map(ld2rc, raw_move[0].split('-'))
        if board.valid_path(src, dst):
            board.move_queen(src, dst)
            break 

    board.print_board()
    print("Options:")
    print('* To shoot, type "<loc-to>" (e.g., "h3")')
    print('* To resign, type "<return>"')
    while True: # loop to get valid move from human
        while True: # loop to check for valid syntax first
            raw_move = raw_input("Input please: ")
            if not raw_move:
                return False
            if re.match("^[a-j][0-9]$",raw_move):
                break
            else: print raw_move,"is not a valid input"
        adst = ld2rc(raw_move)
        if board.valid_path(dst,adst):
            return (src,dst,adst)

###################### Your code between these two comment lines ####################################
import numpy as np
import Queue
import random
import signal
from Queue import PriorityQueue
##############################################
# The Board class stores basic information about the game configuration.
# 
# NOTE: The amount of info stored in this class is kept to a minimal. This
# is on purpose. This is just set up as a way for the game controller to
# pass information to your automatic player. Although you cannot change
# the definition of the Board class, you are not constrained to use the
# Board class as your main state reprsentation. You can define your own
# State class and copy/transform from Board the info you need.

# The Board class contains the following data:
#  * config: the board configuration represented as a list of lists.
#    The assumed convention is (row, column) so config[0][1] = "b0"
#  * bWhite: binary indicator -- True if it's white's turn to play
#  * time_limit: deadline for when a move must be returned by
# The Board class supports the following methods:
#  * print_board: prints the current board configuration
#  * valid_path: takes two location tuples (in row, column format) and returns 
#    whether the end points describe a valid path (for either the queen or the arrow)
#  * move_queen: takes two location tuples (in row, column format)
#    and updates the board configuration to reflect the queen moving
#    from src to dst
#  * shoot_arrow: takes one location tuple (in row, column format)
#    and updates the board configuration to include the shot arrow
#  * end_turn: This function does some end of turn accounting: update whose
#    turn it is and determine whether the game ended
#  * count_areas: This is a helper function for end_turn. It figures out
#    whether we can end the game
def kmt81handler(signum, frame):    
    raise Exception("EOP")

class kmt81MyBoardClass:
    prime = 1
    level = 100
    exploresucc = 20
    
    def __init__(self, board):
        
        self.bWhite = board.bWhite
        self.isWhite=board.bWhite
        if(self.bWhite == True):
            self.isWhite = True
        if(self.isWhite == True):
            self.quene='Q'
        else:
            self.queue='q'
        self.config = board.config
        self.nextgoodmove = None
        self.bymove=None
        self.hsize = len(board.config[1])
        self.vsize = len(board.config[0])
        
        self.currentmypos = []
        self.currenttheirpos = []
        self.populateVariables()
                
    def populateVariables(self):
        whiteindex = np.where(np.array(self.config) == "Q")
        blackindex = np.where(np.array(self.config) == "q")
        self.whitequene = zip(whiteindex[0],whiteindex[1])
        self.blackquene = zip(blackindex[0],blackindex[1])
        
        if(self.bWhite == True):
            self.currentmypos = zip(whiteindex[0],whiteindex[1])
            self.currenttheirpos = zip(blackindex[0],blackindex[1])
        else:
            self.currenttheirpos = zip(whiteindex[0],whiteindex[1])
            self.currentmypos = zip(blackindex[0],blackindex[1])
            
    def print_board(self):
        size = len(self.config)
        print ("     Black")
        tmp = "  "+" ".join(map(lambda x: chr(x+ord('a')),range(size)))
        print (tmp)
        for r in range(size-1, -1, -1):
            print r, " ".join(self.config[r]), r
        print (tmp)

    def valid_path(self, src, dst):
        (srcr, srcc) = src
        (dstr, dstc) = dst        
#         print src
#         print dst
        srcstr = rc2ld(src)
        dststr = rc2ld(dst)
#         print srcstr
#         print dststr

        symbol = self.config[srcr][srcc]
#         print symbol
#         print self.isWhite 
        if ( symbol != 'Q' and  symbol != 'q'):
            #print "invalid move: cannot find queen at src:",srcstr
            return False

        h = dstr-srcr
        w = dstc-srcc
        if h and w and abs(h/float(w)) != 1: 
            #print("invalid move: not a straight line")
            return False
        if not h and not w:
            #print("invalid move: same start-end")
            return False

        if not h:
            op = (0, int(w/abs(w)))
        elif not w:
            op = (int(h/abs(h)),0)
        else:
            op = (int(h/abs(h)),int(w/abs(w)))

        (r,c) = (srcr,srcc)
        while (r,c) != (dstr, dstc):
            (r,c) = (r+op[0], c+op[1])
            if (self.config[r][c] != '.'):
             #   print "invalid move: the path is not cleared between",srcstr,dststr
                return False
        return True

    def move_queen(self, src, dst):
        self.config[dst[0]][dst[1]] = self.config[src[0]][src[1]]
        self.config[src[0]][src[1]] = '.'

    def shoot_arrow(self, dst):
        self.config[dst[0]][dst[1]] = 'x'

    def end_turn(self):
        # count up each side's territories
        (w,b) = self.count_areas()

        # if none of the queens of either side can move, the player who just
        # played wins, since that player claimed the last free space.
        if b == w and b == 0:
            if self.bWhite: w = 1
            else: b = 1
        # switch player
        self.bWhite = not self.bWhite
        return (w,b)

    # adapted from standard floodfill method to count each player's territories
    # - if a walled-off area with queens from one side belongs to that side
    # - a walled-off area with queens from both side is neutral
    # - a walled-off area w/ no queens is deadspace
    def count_areas(self):
        # replace all blanks with Q/q/n/-
        def fill_area(replace):
            count = 0
            for r in range(size):
                for c in range(size):
                    if status[r][c] == '.':
                        count+=1
                        status[r][c] = replace
            return count
        
        # find all blank cells connected to the seed blank at (seedr, seedc) 
        def proc_area(seedr,seedc):
            symbols = {} # keeps track of types of symbols encountered in this region
            connected = [(seedr,seedc)] # a stack for df traversal on the grid
            while connected:
                (r, c) = connected.pop()
                status[r][c] = '.'
                for ops in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                    (nr, nc) = (r+ops[0], c+ops[1])
                    if nr < 0 or nr >= size or nc < 0 or nc >= size:
                        continue
                    # if it's a new blank, need to process it; also add to seen
                    if self.config[nr][nc] == '.' and status[nr][nc] == '?':
                        status[nr][nc] = '.'
                        connected.append((nr,nc))
                    # if it's a queen or an arrow; just mark as seen
                    elif self.config[nr][nc] != '.': 
                        status[nr][nc] = 'x'
                        symbols[self.config[nr][nc]] = 1

            if 'Q' in symbols and not 'q' in symbols: # area belongs to white
                return (fill_area('Q'), 0, 0)
            elif 'q' in symbols and not 'Q' in symbols: #area belongs to black
                return (0, fill_area('q'),0)
            elif 'q' in symbols and 'Q' in symbols: # area is neutral
                return (0, 0, fill_area('n'))
            else: # deadspace -- still have to fill but don't return its area value
                fill_area('-')
                return (0,0,0)

        size = len(self.config)
        # data structure for keeping track of seen locations
        status = [['?' for i in range(size)] for j in range(size)]
        wtot = btot = ntot = 0
        for r in range(size):
            for c in range(size):            
                # if it's an empty space and we haven't seen it before, process it
                if self.config[r][c] == '.' and status[r][c] == '?':
                    (w,b,n) = proc_area(r,c)
                    wtot += w
                    btot += b
                    ntot += n
                # if it's anything else, but we haven't seen it before, just mark it as seen and move on
                elif status[r][c] == '?':
                    status[r][c] = 'x'
                    
        if ntot == 0: # no neutral space left -- should end game
            if wtot > btot:
                return (wtot-btot, 0)
            else: return (0, btot-wtot)
        else: return (wtot+ntot, btot+ntot)
        
        
#     def max_valueab(self, board,level,alpha,beta):
#         node=None
#         state = copy.deepcopy(board)
#         if(board.isWhite == True):
#             state.queue='Q'
#         else:
#             state.queue='q'
#             
#         if(( state.isTerminal() == True) or (level == 0) ) :
#             return (state,state.Utility())
#         
#         children = state.getSuccessor(state.queue)
#         
#         value = float("-inf")        
#         tmp_level = level-1
#         for child in children:
#             #child.print_board()
#             (newsucc,retval) = self.min_valueab(child,tmp_level,alpha,beta)
#             value = max(value, retval)
#             if value >= beta:
#                 return (node,value)
# 
#             if(value < retval):
#                 node =child
#             
#             alpha=max(alpha,value)
#         return (node,value)
        
    def max_value(self, board,level):
        node=None
        state = copy.deepcopy(board)
        if(board.isWhite == True):
            state.queue='Q'
        else:
            state.queue='q'
            
        if(( state.isTerminal() == True) or (level == 0) ) :
            return (state,state.Utility())

        children = state.getSuccessor(state.queue)
        
        value = float("-inf")        
        tmp_level = level-1
        for child in children:
            #child.print_board()
            (newsucc,retval) = self.min_value(child,tmp_level)
            if(value < retval):
                node =child
            value = max(value, retval)
        return (node,value)
    
#     def min_valueab(self, board,level,alpha,beta):
#         node=None
# 
#         state = copy.deepcopy(board)
#         if(board.isWhite == True):
#             state.queue='Q'
#         else:
#             state.queue='q'
#             
#         if(( state.isTerminal() == True) or (level == 0) ) :
#             return (state,state.Utility())
# 
#         children = state.getSuccessor(state.queue)        
#         
#         value = float("inf")
#         tmp_level = level-1
#         for child in children:
#             (newsucc,retval) = self.max_valueab(child,tmp_level,alpha,beta)
#             value = min(value, retval)
#             if value <= alpha:
#                 return (node,value)
#             if(value > retval):                
#                 node = child
#             
#             beta=min(beta,value)
#         return (node,value)

    
    def min_value(self, board,level):
        node = None
        state = copy.deepcopy(board)
        if(board.isWhite == True):
            state.queue='q'
        else:
            state.queue='Q'

        if(( state.isTerminal() == True) or (level == 0) ):
            return (state,state.Utility())

        children = state.getSuccessor(state.queue)        
        
        value = float("inf")
        tmp_level = level-1
        for child in children:
            (newsucc,retval) = self.max_value(child,tmp_level)
            if(value > retval):                
                node = child
            value = min(value, retval)
        return (node,value)

    def isTerminal(self):
        wscore,bscore = self.end_turn()
        if wscore and bscore:
            return False
        else:
            return True
    
    def Utility(self):
        (wscore,bscore) = self.count_areas()
        if(self.isWhite == True):
            return wscore - bscore
        else:
            return bscore - wscore
        
    
    def getPrimeSuccesors(self,symbol):
        
        
        boards=[]        
        currentboard=np.array(self.config)
        if(symbol == 'Q'):
            srcnodes = copy.deepcopy(self.whitequene)
            startnodes = copy.deepcopy(self.blackquene)
        else:
            srcnodes = copy.deepcopy(self.blackquene)
            startnodes = copy.deepcopy(self.whitequene)
        
        blankindext = np.where(np.array(currentboard) == ".")
        blankindex = zip(blankindext[0],blankindext[1])
        primeplaces = []
        
        loop = True
        count = 0
        
        while(loop):
            for (i,j) in startnodes:
                
                for (l,k) in startnodes:
                    if (i,k) != (l,k):
                        primeplaces.append((i,k))
                        primeplaces.append((l,j))
                
                primeplaces.append((i-1,j-1))
                primeplaces.append((i+1,j+1))
                primeplaces.append((i-1,j+1))
                primeplaces.append((i+1,j-1))
                
                primeplaces.append((i-1,j))    
                primeplaces.append((i,j-1))
                primeplaces.append((i,j+1))
                primeplaces.append((i+1,j))

            primeplacest = list(set(primeplaces).intersection(blankindex))
            blankindex = primeplacest
            arrowindex = primeplacest
    
            for dst in blankindex:
                for src in srcnodes:
                    tmp_board = copy.deepcopy(self)
                    if tmp_board.valid_path(src,dst):
                        tmp_board.move_queen(src,dst)
                        for m,n in arrowindex:                
                            adst=(m,n)
                            if adst != dst and tmp_board.valid_path(dst, adst):
                                tmp_arrow_board = copy.deepcopy(tmp_board)                             
                                tmp_arrow_board.bymove =[src,dst,adst]
                                tmp_arrow_board.shoot_arrow(adst)
                                boards.append(copy.deepcopy(tmp_arrow_board))
                                
#                                 print tmp_arrow_board.Utility()
                                del tmp_arrow_board
                    del tmp_board
#             print len(boards)
            if(len(boards) > 20 or count != 0):
                loop = False
            else:
                count = count +1
                startnodes = copy.deepcopy(primeplaces)
                
        return boards 
    
    def getSuccessor(self,symbol):
        boards = []
        self.populateVariables()
        
        if(symbol=='Q'):
            opp_symbol='q'
        else:
            opp_symbol='Q'
        
        if(kmt81MyBoardClass.prime == 1):
            boards = self.getPrimeSuccesors(symbol)
            
            pq = PriorityQueue()
           # oppways = self.oppqueenWays(symbol)
            for b in boards:
                ways = b.countWays(opp_symbol) #+oppways[b[0]]
                pq.put(b,ways)
                
            boards = []
            max_childs = kmt81MyBoardClass.exploresucc
            
            #print pq
            size = pq.qsize()
            
            for i in range(size):
                if max_childs > 0:
                    boards.append(pq.get())
                    max_childs = max_childs-1
            
            if(len(boards) > 0):
                return boards
            
        currentboard=np.array(self.config)
        if(symbol == 'Q'):
            srcnodes = copy.deepcopy(self.whitequene)
        else:
            srcnodes = copy.deepcopy(self.blackquene)
             
        blankindext = np.where(np.array(currentboard) == ".")
        blankindex = zip(blankindext[0],blankindext[1])
        
        arrowindex =  srcnodes
        if(len(blankindex) == 1):
            arrowindex += blankindex
        elif(len(blankindex) > 1):
            arrowindex += zip(blankindex[0],blankindex[1]) 

#         start=time.time()
        for dst in blankindex:
            for src in srcnodes:
                tmp_board = copy.deepcopy(self)
                if tmp_board.valid_path(src,dst):
                    tmp_board.move_queen(src,dst)
                    for m,n in arrowindex:                
                        adst=(m,n)
                        if adst != dst and tmp_board.valid_path(dst, adst):
                            tmp_arrow_board = copy.deepcopy(tmp_board)                             
                            tmp_arrow_board.bymove =[src,dst,adst]
                            tmp_arrow_board.shoot_arrow(adst)
                            boards.append(copy.deepcopy(tmp_arrow_board))                            
                            del tmp_arrow_board
                del tmp_board
    #         print("--- %s seconds ---" % (time.time() - start))
        return boards
    
    def countWays(self,symbol):
        ways=0
        mways=0
        oppways = dict()
        #print symbol
        oursymbol = 'q'
        opp_queens = np.where(np.array(self.config) == symbol)
        qPos = zip(opp_queens[0],opp_queens[1])
        
        if(symbol == 'q'):
            oursymbol = 'Q'
            
        our_queens = np.where(np.array(self.config) == oursymbol)
        QPos = zip(our_queens[0],our_queens[1])

        #print qPos
        
        for q in qPos :
            #print ways
            ways = ways + self.countDots(q)
        
        for q in QPos :
            #print ways
            mways = mways + self.countDots(q)
        
        
        return mways - ways 

    def oppqueenWays(self,symbol):
        oppways = dict()
        #print symbol
        
        opp_queens = np.where(np.array(self.config) == symbol)
        qPos = zip(opp_queens[0],opp_queens[1])
        our_queens = np.where(np.array(self.config) == symbol)
        QPos = zip(our_queens[0],our_queens[1])

        #print qPos
        
        for q in qPos :
            oppways[q] = self.countDots(q)        
        
        return oppways
    
    def countDots(self,pos):
        dots=0
        ulimit = self.hsize -1
        llimit = 0
        boardArr = np.array(self.config)
        # upper left
        if pos[0]<ulimit and pos[1]>llimit:
            if boardArr[pos[0]+1][pos[1]-1]=='.' :
                dots=dots+1
        
        # up
        if pos[0]<ulimit:
            if boardArr[pos[0]+1][pos[1]]=='.':
                dots=dots+1
                
        # upper right
        if pos[0]<ulimit and pos[1]<ulimit:
            if boardArr[pos[0]+1][pos[1]+1]=='.':
                dots=dots+1
                
        # left
        if pos[1]>llimit:
            if boardArr[pos[0]][pos[1]-1]=='.':
                dots=dots+1
                
        # right
        if pos[1]<ulimit:
            if boardArr[pos[0]][pos[1]+1]=='.':
                dots=dots+1
                
        # lower left
        if pos[0]>llimit and pos[1]>llimit:
            if boardArr[pos[0]-1][pos[1]-1]=='.':
                dots=dots+1
                
        # down
        if pos[0]>llimit:
            if boardArr[pos[0]-1][pos[1]]=='.':
                dots=dots+1
                
        # lower right
        if pos[0]> llimit and pos[1]<ulimit:
            if boardArr[pos[0]-1][pos[1]+1]=='.':
                dots=dots+1

        return dots                      
    

    def getRandomSuccessor(self,symbol):
        boards = []
        randomnode=None
        self.populateVariables()
            
        currentboard=np.array(self.config)
        if(symbol == 'Q'):
            srcnodes = copy.deepcopy(self.whitequene)
        else:
            srcnodes = copy.deepcopy(self.blackquene)
             
        blankindext = np.where(np.array(currentboard) == ".")
        blankindex = zip(blankindext[0],blankindext[1])
        
        arrowindex =  srcnodes
        if(len(blankindex) == 1):
            arrowindex += blankindex
        elif(len(blankindex) > 1):
            arrowindex += zip(blankindex[0],blankindex[1]) 

#         start=time.time()
        for dst in blankindex:
            for src in srcnodes:
                tmp_board = copy.deepcopy(self)
                if tmp_board.valid_path(src,dst):
                    tmp_board.move_queen(src,dst)
                    for m,n in arrowindex:                
                        adst=(m,n)
                        if adst != dst and tmp_board.valid_path(dst, adst):
                            tmp_arrow_board = copy.deepcopy(tmp_board)                             
                            tmp_arrow_board.bymove =[src,dst,adst]
                            tmp_arrow_board.shoot_arrow(adst)
                            boards.append(copy.deepcopy(tmp_arrow_board))
                            del tmp_arrow_board
                del tmp_board
    #     print("--- %s seconds ---" % (time.time() - start))
        rnum = random.randint(0,len(boards)-1)
        if(len(boards) > 0):
            randomnode = boards[rnum] 
        return  randomnode

    
#     def minmax_ab_decision(self): 
#         ct =0
#         signal.signal(signal.SIGALRM, kmt81handler)
#         signal.alarm( 14 )    
#         
#         node = [(0,0),(0,0),(0,0)]
#         value = 0    
#         try:    
#             start = time.time()
#             level = kmt81MyBoardClass.level
#             
#             for i in range(level):
#                 print i
#                 (node,value) = self.max_valueab(self,i+1,float("-inf"),float("+inf"))
#                 print node.print_board()
#                 print value
#         except:
#             ct=1   
#         finally:
#            signal.alarm(0)
#            return (node,value)
#         return (node,value)    

                                  
    def minmax_decision(self):
        ct =0
        signal.signal(signal.SIGALRM, kmt81handler)
        signal.alarm( 14 )    
        node = [(0,0),(0,0),(0,0)]
        value = 0    
        try:    
#             start = time.time()
            level = kmt81MyBoardClass.level
            
            for i in range(level):
                (node,value) = self.max_value(self,i+1)
    #         print node.bymove        
        except:
            ct=1   
        finally:
           signal.alarm(0)
           return (node,value)
        return (node,value)    
    
    
def kmt81(board):    
    myBoard = kmt81MyBoardClass(board)
    #myBoard.print_board()        
    (node,value) = myBoard.minmax_decision()
    return node.bymove
    


def kmt82(board):    
    myBoard = kmt81MyBoardClass(board)
    #myBoard.print_board()
    (node,value) = myBoard.minmax_decision()
    return node.bymove

def Random(board):    
    myBoard = kmt81MyBoardClass(board)
    #myBoard.print_board()
    if(myBoard.isWhite == True):
        symbol='Q'
    else:
        symbol='q'
    node = myBoard.getRandomSuccessor(symbol)
    if(node is not None ):
        return node.bymove
    return [(0,0),(0,0),(0,0)]
    
#     if(myBoard.isWhite == True):
#         symbol='Q'
#     else:
#         symbol='q'
# 
#     node = myBoard.getRandomSuccessor(symbol)
#     if(node is not None ):
#         return node.bymove
#     return [(0,0),(0,0),(0,0)]

###################### Your code between these two comment lines ####################################

def main():

    if len(sys.argv) == 2:
        fname = sys.argv[1]
    else:
        fname = raw_input("setup file name?")        
    game = Amazons(fname)
    game.play()
    

if __name__ == "__main__":
    main()
    

