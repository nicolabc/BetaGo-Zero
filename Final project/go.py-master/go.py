#!/usr/bin/env python

import argparse
import sys

from go import Board, BoardError, View, clear, getch


def main():
    # Get arguments
    parser = argparse.ArgumentParser(description='Starts a game of go in the terminal.')
    parser.add_argument('-s', '--size', type=int, default=19, help='size of board')

    args = parser.parse_args()

    if args.size < 7 or args.size > 19:
        sys.stdout.write('Board size must be between 7 and 19!\n')
        sys.exit(0)

    # Initialize board and view
    size = 9
    board = Board(size)
    view = View(board)
    err = None

    #board.move(3,3)
    #view.redraw()
    #board.move(4,4)
    #view.redraw()
    #board.move(1,1)
    #board.move(1,1)
    view.redraw()
    
    # User actions
    def move():
        """
        Makes a move at the current position of the cursor for the current
        turn.
        """
        board.move(*view.cursor)
        view.redraw()

    def undo():
        """
        Undoes the last move.
        """
        board.undo()
        view.redraw()

    def redo():
        """
        Redoes an undone move.
        """
        board.redo()
        view.redraw()

    def passing():
        """
        Pass the turn to the next player
        """
        board._push_history()   #Add move to history
        board._flip_turn()      #Toggle turn
        view.redraw()

    def count():
        """
        Count the final score of the game
        """
        a = board.count_score(size)
        sys.stdout.write('Final score is: %s' % a)
        sys.stdout.write('\n')
        exit()

    
    def exit():
        """
        Exits the game.
        """
        sys.exit(0)

    

    # Action keymap
    KEYS = {
        'w': view.cursor_up,
        's': view.cursor_down,
        'a': view.cursor_left,
        'd': view.cursor_right,
        ' ': move,
        'u': undo,
        'r': redo,
        'p': passing,
        'c': count,
        '\x1b': exit,
    }

    # Main loop
    while True:
        # Print board
        clear()            #Clears the board
        sys.stdout.write('{0}\n'.format(view))
        sys.stdout.write('Black: {black} <===> White: {white}\n'.format(**board.score))
        sys.stdout.write('{0}\'s move... '.format(board.turn))
        sys.stdout.write('\n')

        if err:
            sys.stdout.write('\n' + err + '\n')
            err = None

        # Get action key
        c = getch()
        
        try:
            # Execute selected action
            KEYS[c]()
        except BoardError as be:
            # Board error (move on top of other piece, suicidal move, etc.)
            #err = be.message
            pass

        except KeyError:
            # Action not found, do nothing
            pass


if __name__ == '__main__':
    main()
