from collections import namedtuple
from copy import copy

from .array import Array, ArrayError
from .location import Location


class BoardError(Exception):
    pass


class Board(Array):
    """
    Stores board locations.  Provides methods to carry out game logic.
    """
    BLACK = Location('black')
    WHITE = Location('white')
    EMPTY = Location('empty')

    TURNS = (
        BLACK,
        WHITE,
    )

    State = namedtuple('State', ['board', 'turn', 'score'])

    def __init__(self, width):
        super(Board, self).__init__(width, width, self.EMPTY)

        # Turn counter
        self._turn = self.BLACK

        # Player scores
        self._score = {
            self.BLACK: 0,
            self.WHITE: 0,
        }

        # Game history
        self._history = []
        self._redo = []

    @property
    def turn(self):
        """
        Gets the current turn.
        """
        return repr(self._turn)

    @property
    def score(self):
        """
        Gets the current score.
        """
        return {
            'black': self._score[self.BLACK],
            'white': self._score[self.WHITE],
        }

    @property
    def _next_turn(self):
        """
        Gets color of next turn.
        """
        return self.TURNS[self._turn is self.BLACK]

    def move(self, x, y):
        """
        Makes a move at the given location for the current turn's color.
        """
        # Check if coordinates are occupied
        if self[x, y] is not self.EMPTY:
            #raise BoardError('Cannot move on top of another piece!')
            return

        # Store history and make move
        self._push_history()
        self[x, y] = self._turn

        # Check if any pieces have been taken
        taken = self._take_pieces(x, y)

        # Check if move is suicidal.  A suicidal move is a move that takes no
        # pieces and is played on a coordinate which has no liberties.
        legal = True
        
        if taken == 0:
            legal = self._check_for_suicide(x, y)

        # Check if move is redundant.  A redundant move is one that would
        # return the board to the state at the time of a player's last move.

        if(legal):

            legal = self._check_for_ko()
        if(legal):

            self._flip_turn()
        self._redo = []

    def _check_for_suicide(self, x, y):
        """
        Checks if move is suicidal.
        """
        if self.count_liberties(x, y) == 0:
            self._pop_history()
            #raise BoardError('Cannot play on location with no liberties!')
            return False
        return True
            

    def _check_for_ko(self):
        """
        Checks if board state is redundant.
        """
        try:
            if self._array == self._history[-2][0]:
                self._pop_history()
                #raise BoardError('Cannot make a move that is redundant!')
                return False
            return True
        except IndexError:
            # Insufficient history...let this one slide
            return True
            pass
        return True

    def _take_pieces(self, x, y):
        """
        Checks if any pieces were taken by the last move at the specified
        coordinates.  If so, removes them from play and tallies resulting
        points.
        """
        scores = []
        for p, (x1, y1) in self._get_surrounding(x, y):
            # If location is opponent's color and has no liberties, tally it up
            if p is self._next_turn and self.count_liberties(x1, y1) == 0:
                score = self._kill_group(x1, y1)
                scores.append(score)
                self._tally(score)
        return sum(scores)

    def _flip_turn(self):
        """
        Iterates the turn counter.
        """
        self._turn = self._next_turn
        return self._turn

    @property
    def _state(self):
        """
        Returns the game state as a named tuple.
        """
        return self.State(self.copy._array, self._turn, copy(self._score))

    def _load_state(self, state):
        """
        Loads the specified game state.
        """
        self._array, self._turn, self._score = state

    def _push_history(self):
        """
        Pushes game state onto history.
        """
        self._history.append(self._state)

    def _pop_history(self):
        """
        Pops and loads game state from history.
        """
        current_state = self._state
        try:
            self._load_state(self._history.pop())
            return current_state
        except IndexError:
            return None

    def undo(self):
        """
        Undoes one move.
        """
        state = self._pop_history()
        if state:
            self._redo.append(state)
            return state
        else:
            raise BoardError('No moves to undo!')

    def redo(self):
        """
        Re-applies one move that was undone.
        """
        try:
            self._push_history()
            self._load_state(self._redo.pop())
        except IndexError:
            self._pop_history()
            raise BoardError('No undone moves to redo!')

    def _tally(self, score):
        """
        Adds points to the current turn's score.
        """
        self._score[self._turn] += score

    def _get_none(self, x, y):
        """
        Same thing as Array.__getitem__, but returns None if coordinates are
        not within array dimensions.
        """
        try:
            return self[x, y]
        except ArrayError:
            return None

    def _get_surrounding(self, x, y):
        """
        Gets information about the surrounding locations for a specified
        coordinate.  Returns a tuple of the locations clockwise starting from
        the top.
        """
        coords = (
            (x, y - 1),
            (x + 1, y),
            (x, y + 1),
            (x - 1, y),
        )
        return filter(lambda i: bool(i[0]), [
            (self._get_none(a, b), (a, b))
            for a, b in coords
        ])

    def _get_group(self, x, y, traversed):
        """
        Recursively traverses adjacent locations of the same color to find all
        locations which are members of the same group.
        """
        loc = self[x, y]

        # Get surrounding locations which have the same color and whose
        # coordinates have not already been traversed
        locations = [
            (p, (a, b))
            for p, (a, b) in self._get_surrounding(x, y)
            if p is loc and (a, b) not in traversed
        ]

        # Add current coordinates to traversed coordinates
        traversed.add((x, y))

        # Find coordinates of similar neighbors
        if locations:
            return traversed.union(*[
                self._get_group(a, b, traversed)
                for _, (a, b) in locations
            ])
        else:
            return traversed

    def get_group(self, x, y):
        """
        Gets the coordinates for all locations which are members of the same
        group as the location at the given coordinates.
        """
        if self[x, y] not in self.TURNS:
            raise BoardError('Can only get group for black or white location')

        return self._get_group(x, y, set())

    def _kill_group(self, x, y):
        """
        Kills a group of black or white pieces and returns its size for
        scoring.
        """
        if self[x, y] not in self.TURNS:
            raise BoardError('Can only kill black or white group')

        group = self.get_group(x, y)
        score = len(group)

        for x1, y1 in group:
            self[x1, y1] = self.EMPTY

        return score

    def _get_liberties(self, x, y, traversed):
        """
        Recursively traverses adjacent locations of the same color to find all
        surrounding liberties for the group at the given coordinates.
        """
        loc = self[x, y]

        if loc is self.EMPTY:
            # Return coords of empty location (this counts as a liberty)
            return set([(x, y)])
        else:
            # Get surrounding locations which are empty or have the same color
            # and whose coordinates have not already been traversed
            locations = [
                (p, (a, b))
                for p, (a, b) in self._get_surrounding(x, y)
                if (p is loc or p is self.EMPTY) and (a, b) not in traversed
            ]

            # Mark current coordinates as having been traversed
            traversed.add((x, y))

            # Collect unique coordinates of surrounding liberties
            if locations:
                return set.union(*[
                    self._get_liberties(a, b, traversed)
                    for _, (a, b) in locations
                ])
            else:
                return set()

    def get_liberties(self, x, y):
        """
        Gets the coordinates for liberties surrounding the group at the given
        coordinates.
        """
        return self._get_liberties(x, y, set())

    def count_liberties(self, x, y):
        """
        Gets the number of liberties surrounding the group at the given
        coordinates.
        """
        return len(self.get_liberties(x, y))

    def count_score(self,size):
        """
        Computes the final score for each player
        """
        """liberties = 0
        a = set()
        for i in range(0,size):
            for j in range(0, size):
                #liberties += self.count_liberties(j,i)
                #print(liberties)
                
                #a = set.update(self.get_liberties(j,i))
                #print(self.get_liberties(j,i))
                temp = self.count_liberties(j,i)
                print(temp)
                if temp > 1: #The question is why we get 1 liberty when there are no stones placed...
                    liberties += temp
        
        print(liberties)
        """
        global non_groups
        global o_points
        global x_points
    
        ## Creates a list of groups (non_groups) of empty positions.
        for i in range(0,size):
            for j in range(0,size):
                if self[j][i] == '.':
                    new = 1
                    for group in non_groups:
                        if [i,j] in self.gperm(group,size):
                            group.append([i,j])
                            new = 0
                    if new == 1:
                        non_groups.append([[i,j]])
        self.concat('.')
    
        o_points = 0
        x_points = 0
    
        ## Gives a point to the each player for every pebble they have
        ## on the board.
        for group in o_groups:
            o_points += len(group)
        for group in x_groups:
            x_points += len(group)
    
        ## The permimeter of these empty positions is here considered,
        ## and if every position in the permimeter of a non_group is
        ## one player or the other, that player gains a number of points
        ## equal to the length of that group (the number of positions
        ## that their pieces enclose).
        for group in non_groups:
            no = 0
            for element in self.gperm(group,size):
                if self[element[1]][element[0]] != 'o':
                    no = 1
            if no == 0:
                o_points += len(group)
    
        for group in non_groups:
            no = 0
            for element in self.gperm(group,size):
                if self[element[1]][element[0]] != '*':
                    no = 1
            if no == 0:
                x_points += len(group)
        """
        The logic is: area + number of pieces = total score
        (For the respective color)"""
        return x_points,o_points
        

        #return liberties, 0
    ## Returns a list of the board positions surrounding the
    ## passed group.
    def gperm(self,group,size):
        permimeter = []
        size
        hit = 0
        loss = 0
        ## Adds permimeter spots below
        ## Works by looking from top to bottom, left to right,
        ## at each posisition on the board.  When a posistion
        ## is hit that is in the given group, I set hit = 1.
        ## Then, at the next position that is not in that group,
        ## or if the end of the column is reached, I set loss = 1.
        ## That point is the first point below a point in that group,
        ## so it is part of the permieter of that group.
        i = 0
        j = 0
        while i < size:
            j = 0
            hit = 0
            while j < size:
                if [i,j] in group:
                    hit = 1
                elif (hit == 1) & ([i,j] not in group):
                    loss = 1
                if (hit == 1) & (loss == 1):
                    permimeter.append([i,j])
                    hit = 0
                    loss = 0
                j += 1
            i += 1
        ## Adds permimeter spots to the right
        i = 0
        j = 0
        while i < size:
            j = 0
            hit = 0
            while j < size:
                if [j,i] in group:
                    hit = 1
                elif (hit == 1) & ([j,i] not in group):
                    loss = 1
                if (hit == 1) & (loss == 1):
                    permimeter.append([j,i])
                    hit = 0
                    loss = 0
                j += 1
            i += 1
        ## Adds permimeter spots above
        i = 0
        j = size-1
        while i < size:
            j = size-1
            hit = 0
            while j >= 0:
                if [i,j] in group:
                    hit = 1
                elif (hit == 1) & ([i,j] not in group):
                    loss = 1
                if (hit == 1) & (loss == 1):
                    permimeter.append([i,j])
                    hit = 0
                    loss = 0
                j -= 1
            i += 1
        ## Adds permimeter spots to the left
        i = 0
        j = size-1
        while i < size:
            j = size-1
            hit = 0
            while j >= 0:
                if [j,i] in group:
                    hit = 1
                elif (hit == 1) & ([j,i] not in group):
                    loss = 1
                if (hit == 1) & (loss == 1):
                    permimeter.append([j,i])
                    hit = 0
                    loss = 0
                j -= 1
            i += 1
        return permimeter
    ## Checks if any groups contain the same point;
    ## if so, joins them into one group
    def concat(self,xoro):
        global o_groups
        global x_groups
        global non_groups
        if xoro == 'o':
            groups = o_groups
        elif xoro == 'x':
            groups = x_groups
        else:
            groups = non_groups
        i = 0
        ## currentgroups and previousgroups are used to compare the number
        ## of groups before this nest of whiles to the number after.  If
        ## The number is the same, then nothing needed to be concatinated,
        ## and we can move on.  If the number is different, two groups
        ## were concatinated, and we need to run through this nest again
        ## to see if any other groups need to be joined together.
        currentgroups = len(groups)
        previousgroups = currentgroups + 1
        ## Checks if the positions contained in any group are to be
        ## found in any other group.  If so, all elements of the second are
        ## added to the first, and the first is deleted.
        while previousgroups != currentgroups:
            while i < len(groups)-1:
                reset = 0
                j = i + 1
                while j < len(groups):
                    k = 0
                    while k < len(groups[i]):
                        if groups[i][k] in groups[j]:
                            for element in groups[j]:
                                if element not in groups[i]:
                                    groups[i].append(element)
                            groups.remove(groups[j])
                            reset = 1
                        if reset == 1:
                            break
                        k += 1
                    j += 1
                if reset == 1:
                    i = -1
                i += 1
            previousgroups = currentgroups
            currentgroups = len(groups)