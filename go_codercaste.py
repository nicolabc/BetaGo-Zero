import numpy as np
from copy import deepcopy

## The number of spots per side of the board
## This code allows for an nxn board
boardsize = 9
## Value determining whether the player wants to quit or not
gameon = 1
## Lists of groups that have been removed from the board via capture,
## held in these varaibles in case, when all captures have been
## completed, the board resembles a previous game state and
## the move is invalid.  In that case, the groups are restored
## from these varaibles.
restore_o = []
restore_x = []
 
## Generates blank game states
def initalize():
    gs = []
    for i in range(0,boardsize):
        gs.append([])
        for j in range(0,boardsize):
            gs[i].append('-')
    return gs
 
## Provides an ascii display of the Go board
def printboard(gs):
    global boardsize
    for row in gs:
        rowprint = ''
        for element in row:
            rowprint += element
            rowprint += ' '
        print(rowprint)
 
## Returns a list of the board positions surrounding the
## passed group.
def gperm(group):
    permimeter = []
    global boardsize
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
    while i < boardsize:
        j = 0
        hit = 0
        while j < boardsize:
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
    while i < boardsize:
        j = 0
        hit = 0
        while j < boardsize:
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
    j = boardsize-1
    while i < boardsize:
        j = boardsize-1
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
    j = boardsize-1
    while i < boardsize:
        j = boardsize-1
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
 
## Returns a string that describes the game state
def readable(gs):
    readthis = ''
    readthis += '<<'
    for row in gs:
        for element in row:
            readthis += element
    readthis += '>>'
    return readthis
 
## Counts the territory captured by each player
def count():
    global gsc
    global non_groups
    global o_points
    global x_points
    global boardsize
 
    ## Creates a list of groups (non_groups) of empty positions.
    for i in range(0,boardsize):
        for j in range(0,boardsize):
            if gsc[j][i] == '-':
                new = 1
                for group in non_groups:
                    if [i,j] in gperm(group):
                        group.append([i,j])
                        new = 0
                if new == 1:
                    non_groups.append([[i,j]])
    concat('-')
 
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
        for element in gperm(group):
            if gsc[element[1]][element[0]] != 'o':
                no = 1
        if no == 0:
            o_points += len(group)
 
    for group in non_groups:
        no = 0
        for element in gperm(group):
            if gsc[element[1]][element[0]] != 'x':
                no = 1
        if no == 0:
            x_points += len(group)
 
## Checks for capture, and removes the captured pieces from the board
def capture(xoro):
    global o_groups
    global x_groups
    global gsf
    global restore_o
    global restore_x
    global edited
    if xoro == 'o':
        groups = x_groups
        otherplayer = 'o'
    else:
        groups = o_groups
        otherplayer = 'x'
 
    ## Checks to see, for each group of a particular player,
    ## whether any of the board positions in the
    ## perimeter around that group are held by the other player.
    ## If any position is not held by the other player,
    ## the group is not captured, and is safe.  Otherwise,
    ## the group is removed.  But we haven't tested this yet
    ## to see if this would return the board to a previous
    ## state, so we save the removed groups with the restore lists.
    i = 0
    while i < len(groups):
        safe = 0
        for element in gperm(groups[i]):
            if gsf[element[1]][element[0]] != otherplayer:
                safe = 1
        if safe != 1:
            edited = 1
            if xoro == 'o':
                restore_x.append(groups[i])
            else:
                restore_o.append(groups[i])
            groups.remove(groups[i])
            i -= 1 #Since we remove a group
        i += 1
 
    # Sets gsf given the new captures
    gsf = initalize()
    for group in o_groups:
        for point in group:
            gsf[point[1]][point[0]] = 'o'
    for group in x_groups:
        for point in group:
            gsf[point[1]][point[0]] = 'x'
 
## Checks to see if the new game state, created by the most recent
## move, returns the board to a previous state.  If not, then
## gsc is set as this new state, and gsp is set as what gsc was, and
## the new game state is stored in gscache.  The function returns 1
## if the move is valid, 0 otherwise.
def goodmove():
    global gscache
    global gsc
    global gsp
    global gsf
    global xoro
    if readable(gsf) not in gscache:
        gsp = []
        gsc = []
        for element in gsf:
            gsp.append(deepcopy(element))
            gsc.append(deepcopy(element))
        gscache += readable(gsf)
        return 1
    else:
        return 0
 
## Checks if any groups contain the same point;
## if so, joins them into one group
def concat(xoro):
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
 
## Adds point xy to a group if xy is in the
## perimeter of an existing group, or creates
## new group if xy is not a part of any existing group.
def addpoint(xy,xoro):
    global o_groups
    global x_groups
    if xoro == 'o':
        groups = o_groups
    else:
        groups = x_groups
    new = 1
    for group in groups:
        if xy in gperm(group):
            group.append(xy)
            new = 0
    if new == 1:
        groups.append([xy])
 
## Lets the player select a move.
def selectmove(xoro):
    global boardsize
    global gsf
    hold = 1
    while hold == 1:
 
        minihold = 1
        while minihold == 1:
            pp = input('Place or pass (l/a)? ')
            if pp == 'a':
                return 'pass'
            elif pp == 'l':
                minihold = 0
                ## This try...except ensures that the user
                ## inputs only numbers
                error = 0
                try:
                    x = int(input('x: '))
                except ValueError:
                    error = 1
                try:
                    y = int(input('y: '))
                except ValueError:
                    error = 1
                if error == 1:
                    minihold = 1
                    print('invalid')
            else:
                print('invalid')
        ## Ensures that the input is on the board
        if (x > boardsize) | (x < 0) | (y > boardsize) | (y < 0):
            print('invalid')
        elif gsc[y][x] != '-':
            print('invalid')
        else:
            hold = 0
    ## Places the piece on the 'future' board, the board
    ## used to test if a move is valid
    if xoro == 'o':
        gsf[y][x] = 'o'
    else:
        gsf[y][x] = 'x'
 
    return [x,y]
 
## The 'turn,' in which a player makes a move,
## the captures caused by that piece are made,
## the validity of the move is checked, and
## the endgame status is checked.
def turn():
    global xoro
    global notxoro
    global player1_pass
    global player2_pass
    global gameover
    global gscache
    global gsc
    global gsp
    global gsf
    global o_groups
    global x_groups
    global non_groups
    hold = 1
    while hold == 1:
        print()
        print('place for '+xoro)
        ## By calling selectmove(), the player
        ## is given the option of whether to place
        ## a piece or to pass, and where to place
        ## that piece.
        xy = selectmove(xoro)
        if xy == 'pass':
            if xoro == 'o':
                player1_pass = 1
            else:
                player2_pass = 1
            hold = 0
        ## If the player doesn't pass...
        else:
            player1_pass = 0
            player2_pass = 0
            prev_o_groups = deepcopy(o_groups)
            prev_x_groups = deepcopy(x_groups)
            prev_non_groups = deepcopy(non_groups)
            ## The new piece is added to its group,
            ## or a new group is created for it.
            addpoint(xy,xoro)
            ## Groups that have been connected by
            ## the this placement are joined together
            
            concat(xoro)
            minihold = 1
            ## Edited is a value used to check
            ## whether any capture is made.  capture()
            ## is called as many times as until no pieces
            ## are capture (until edited does not change
            ## to 1)
            edited = 0

            #stonesInCurrentBoard = sum(i.count(xoro) for i in gsf)
            

            while minihold == 1:
                restore_o = []
                restore_x = []
                capture(xoro)
                
                if edited == 0:
                    minihold = 0
                    edited = 0
                else:
                    edited = 0
            #Check wether the newly placed stone will result in no liberties for the group --> suicide. Continue if no suicide move
            if (checkForSuicide(xoro) == 0):
            ## Checks to see if the move, given all the
            ## captures it causes, would return the board
            ## to a previous game state.
                """
                stonesInFutureBoard = sum(i.count(xoro) for i in gsf)
                
                print(stonesInFutureBoard)
                print(stonesInCurrentBoard)
                ifstonesInFutureBoard >= stonesInCurrentBoard:
                """ 
                if goodmove() == 1:
                    #This means that the move increases the number of the player's stone
                    #Don't concatenate this if with the if above. Will cause suicide to fail.  
                    hold = 0
                        
                ## If the move is invalid, the captured groups need
                ## to be returned to the board, so we use
                ## the groups stored in the restore lists to
                ## restore the o_ and x_groups lists.
                else:
                    print('invalid move - returns board to a previous state')
                    """for group in restore_o:
                        o_groups.append(group)
                    for group in restore_x:
                        x_groups.append(group)"""
                    o_groups = deepcopy(prev_o_groups)
                    x_groups = deepcopy(prev_x_groups)
                    non_groups = deepcopy(prev_non_groups)
                    gsf = deepcopy(gsc)
            else:
                print('invalid move - suicide')
                o_groups = deepcopy(prev_o_groups)
                x_groups = deepcopy(prev_x_groups)
                non_groups = deepcopy(prev_non_groups)
                gsf = deepcopy(gsc)

    if (player1_pass == 1) & (player2_pass == 1):
        gameover = 1

#Returns 1 if the move in gsf will result in suicide (no free liberties). Else return 0 if legal move
def checkForSuicide(xoro):
    global o_groups
    global x_groups
    global gsf
    global restore_o
    global restore_x
    global edited
    if xoro == 'x':
        groups = x_groups
        otherplayer = 'o'
    else:
        groups = o_groups
        otherplayer = 'x'

    for group in groups:
                safe = 0
                for element in gperm(group):
                    if gsf[element[1]][element[0]] != otherplayer:
                        safe = 1
                if safe != 1:
                    """if xoro == 'o':
                        restore_x.append(group)
                    else:
                        restore_o.append(group)
                    groups.remove(group)"""
                    return 1 #Suicide == True
    return 0    #Suicide == False

## Called to start a game
def main():
    ## Either 'o' or 'x', determines who's turn it is
    global xoro
    ## The opposite of xoro, determines who's turn it is not
    global notxoro
    ## Game State Current, the current layout of the board
    ## This value is two-dimensional list, the higher dimension being
    ## lists representing the rows and the lower dimension being
    ## strings representing individual positions on the board.
    ## These strings are either '-', 'o', or 'x'
    global gsc
    ## 0 or 1, determins whether the current game is ongoing or ended
    global gameover
    ## Game State Future, same setup as gsc, used for testing the
    ## waters of a new move, to see if that move is valid, before
    ## gsc is edited to reflect that move
    global gsf
    ## Two-dimensional lists, the higher dimension being groups, the
    ## lower dimension being lists of board positions in a particular
    ## group
    global o_groups
    global x_groups
    ## Groups of empty positions
    global non_groups
    ## String containing all the game states encountered in a particular
    ## game, used to check validity of moves
    global gscache
    ## 0 or 1, for whether the player has passed their turn or not
    global player1_pass
    global player2_pass
    ## Integer value reflecting the score of a player
    global o_points
    global x_points
 
    ## Creates a blank game state - a blank board
    gsc = initalize()
    gsf = deepcopy(gsc)
    ## Sets initial values
    o_groups = []
    x_groups = []
    non_groups = []
    gscache = ''
    player1_pass = 0
    player2_pass = 0
    gameover = 0
    o_points = 0
    x_points = 0
 
    ## Gives players turns until the end of the game
    ## (that is, until both players pass, one after
    ## the other)
    while gameover != 1:
 
        ## Set it as o-player's turn
        xoro = 'o'
        notxoro = 'x'
        print()
        printboard(gsc)
 
        turn()
        if gameover == 1:
            break
 
        ## Sets it as x-player's turn
        xoro = 'x'
        notxoro = 'o'
        print()
        printboard(gsc)
 
        turn()
 
    ## Counts the score of both players
    count()
    print()
    print('final board:')
    print()
    printboard(gsc)
    print()
    print('o points: ',str(o_points))
    print('x points: ',str(x_points))
    ## Determines the winner
    if o_points > x_points:
        print('o wins')
    elif x_points > o_points:
        print('x wins')
    else:
        print('tie')

def playFullGame(net1,net2):
    """
    Plays an entire game for network architecture 1 and 2 
    and returns a value stating which network won
    """
    komi = 5.5
    ## Either 'o' or 'x', determines who's turn it is
    global xoro
    ## The opposite of xoro, determines who's turn it is not
    global notxoro
    ## Game State Current, the current layout of the board
    ## This value is two-dimensional list, the higher dimension being
    ## lists representing the rows and the lower dimension being
    ## strings representing individual positions on the board.
    ## These strings are either '-', 'o', or 'x'
    global gsc
    ## 0 or 1, determins whether the current game is ongoing or ended
    global gameover
    ## Game State Future, same setup as gsc, used for testing the
    ## waters of a new move, to see if that move is valid, before
    ## gsc is edited to reflect that move
    global gsf
    ## Two-dimensional lists, the higher dimension being groups, the
    ## lower dimension being lists of board positions in a particular
    ## group
    global o_groups
    global x_groups
    ## Groups of empty positions
    global non_groups
    ## String containing all the game states encountered in a particular
    ## game, used to check validity of moves
    global gscache
    ## 0 or 1, for whether the player has passed their turn or not
    global player1_pass
    global player2_pass
    ## Integer value reflecting the score of a player
    global o_points
    global x_points
 
    ## Creates a blank game state - a blank board
    gsc = initalize()
    gsf = initalize()
    ## Sets initial values
    o_groups = []
    x_groups = []
    non_groups = []
    gscache = ''
    player1_pass = 0
    player2_pass = 0
    gameover = 0
    o_points = 0
    x_points = 0
 
    ## Gives players turns until the end of the game
    ## (that is, until both players pass, one after
    ## the other)
    while gameover != 1:
 
        ## Set it as o-player's turn
        xoro = 'o'
        notxoro = 'x'
        printboard(gsc)

        isLegalMove = 0
        nrOfTries = 0
        print()
        print("o is thinking [...]")
        while(isLegalMove==0):              
            #While a move selected is illegal, choose another one
            moves = net1.forwardPass(gsc) #Pass the board through the network. Moves is an 82-length array corresponding to which move to make
            myMove = moves #np.argmax(moves) <-- Change to this when changed to list
            xy = unflatten(myMove)          #Returns list in [x,y]-coordinates
            isLegalMove = checkIfLegal(xy)
            nrOfTries += 1
            if nrOfTries > 50:
                xy = [0,boardsize] #The agent selects pass
                break
        print('o selects: ',xy)
        networkTurn(xy)                 #Place the turn at [x,y]
        net1.updateBoard(gsc)           #Updates the board history

        if gameover == 1:
            break
 
        ## Sets it as x-player's turn
        xoro = 'x'
        notxoro = 'o'
        printboard(gsc)

        isLegalMove = 0
        nrOfTries = 0
        print()
        print("x is thinking [...]")
        while(isLegalMove==0):
            moves = net2.forwardPass(gsc) #Pass the board through the network. Moves is an 82-length array corresponding to which move to make
            myMove = moves#np.argmax(moves)  <-- Change to this when changed to list
            xy = unflatten(myMove)          #Returns list in [x,y]-coordinates
            isLegalMove = checkIfLegal(xy)
            nrOfTries += 1
            if nrOfTries > 50:
                xy = [0,boardsize] #The agent selects pass
                print("Too many tries, pass")
                break
        networkTurn(xy)
        print('x selects: ',xy)
        net2.updateBoard(gsc)           #Updates the board history
 
    ## Counts the score of both players
    count()
    print()
    print('final board:')
    print()
    printboard(gsc)
    print()
    print('o points: ',str(o_points))
    print('x points: ',str(x_points))
    ## Determines the winner
    if o_points > x_points-komi:
        print('o wins')
    elif x_points-komi > o_points:
        print('x wins')
    else:
        print('tie')


    return [x_points-komi,o_points]

def unflatten(i):
    x = i % boardsize    # % is the "modulo operator", the remainder of i / boardsize;
    y = int(i / boardsize)    # where "/" is an integer division
    return [x,y]

## The 'turn,' in which a network makes a move,
## the captures caused by that piece are made,
## the validity of the move is checked, and
## the endgame status is checked.
def networkTurn(xy):
    global xoro
    global notxoro
    global player1_pass
    global player2_pass
    global gameover
    global nrIllegalMoves
    hold = 1
    while hold == 1:
        #print()
        #print('place for '+xoro)
        ## By calling selectmove(), the player
        ## is given the option of whether to place
        ## a piece or to pass, and where to place
        ## that piece.
        #xy = selectmove(xoro)
        if xy[1] == boardsize: #If the y coordinate is boardsize, then we know that this is the nxn+1 move, which is pass
            if xoro == 'o':
                player1_pass = 1
            else:
                player2_pass = 1
            hold = 0
        ## If the player doesn't pass...
        else:
            player1_pass = 0
            player2_pass = 0
            ## The new piece is added to its group,
            ## or a new group is created for it.
            addpoint(xy,xoro)
            ## Groups that have been connected by
            ## the this placement are joined together
            concat(xoro)
            minihold = 1
            ## Edited is a value used to check
            ## whether any capture is made.  capture()
            ## is called as many times as until no pieces
            ## are capture (until edited does not change
            ## to 1)
            edited = 0
            while minihold == 1:
                restore_o = []
                restore_x = []
                capture(xoro)
                capture(notxoro)
                if edited == 0:
                    minihold = 0
                    edited = 0
                else:
                    edited = 0
            hold = 0
            """## Checks to see if the move, given all the
            ## captures it causes, would return the board
            ## to a previous game state.
            if goodmove() == 1:
                hold = 0
            ## If the move is invalid, the captured groups need
            ## to be returned to the board, so we use
            ## the groups stored in the restore lists to
            ## restore the o_ and x_groups lists.
            else:
                #print('invalid move - that returns to board to a previous state')
                nrIllegalMoves+=1
                printboard(gsc)
                print(nrIllegalMoves)
                for group in restore_o:
                    o_groups.append(group)
                for group in restore_x:
                    x_groups.append(group)"""
    if (player1_pass == 1) & (player2_pass == 1):
        gameover = 1

# Check if the move xy is legal
def checkIfLegal(xy):
    
    x,y = xy
    if y == boardsize: #The network chose to pass, this is a legal move by definition
        return 1

    if gsc[y][x] != '-': #If the move tries to put a stone on a nonempty region, this is by definition againts the rules
        return 0

    if xoro == 'o':
        gsf[y][x] = 'o'
    else:
        gsf[y][x] = 'x'
    
    ## Checks to see if the move, given all the
    ## captures it causes, would return the board
    ## to a previous game state.
    if goodmove() == 1:
        stonesInFutureBoard = sum(i.count(xoro) for i in gsf)
        stonesInCurrentBoard = sum(i.count(xoro) for i in gsc)
        print(stonesInFutureBoard)
        print(stonesInCurrentBoard)
        if stonesInFutureBoard < stonesInCurrentBoard: #This means that the move reduces the number of the player's stone.
            for group in restore_o:
                o_groups.append(group)
            for group in restore_x:
                x_groups.append(group)
            return 0
        return 1
    ## If the move is invalid, the captured groups need
    ## to be returned to the board, so we use
    ## the groups stored in the restore lists to
    ## restore the o_ and x_groups lists.
    else:
        #print('invalid move - that returns to board to a previous state')
        #nrIllegalMoves+=1
        #printboard(gsc)
        #print(nrIllegalMoves)
        for group in restore_o:
            o_groups.append(group)
        for group in restore_x:
            x_groups.append(group)
        return 0

class Network:
    def __init__(self, boardsize):
        self.size = boardsize

    def forwardPass(self,board):
        return np.random.randint(0,(self.size)*(self.size)+1)
    def updateBoard(self,board):
        return -1


global nrIllegalMoves
## Finally something that is not a function!
## This while loop will start new games for as
## long as the user choses to.
while gameon == 1:
    global nrIllegalMoves
    nrIllegalMoves = 0
    #print(np.random.randint(0,boardsize*boardsize+1))
    net1 = Network(boardsize)
    net2 = Network(boardsize)
    #playFullGame(net1,net2)
    main()
    hold = 1
    while hold == 1:
        yn = input('play again (y/n)? ')
        if yn == 'n':
            gameon = 0
            hold = 0
        elif yn == 'y':
            hold = 0
        else:
            print('invalid')
