:fire::fire::fire::fire::fire::fire:

Final project using Reinforcement Learning to train an AI to play the game of Go.
See https://en.wikipedia.org/wiki/Go_(game)


:o::x::o::x:

Following scripts are of most importance:
____________________________________________________________________________________________
training.py : 
------------------

Holds the main training loop and functions asociated with mutation of networks, elimination and cloning of networks
____________________________________________________________________________________________
network.py : 
------------------

Holds the functions asociated with actual NN such as forward pass and mutate

Network class : 

Holds a NN model

TwoLayerNetX :

Different NN models (1 and 2 are Stage 1, 3 is Stage 3)

This was done so that NN models could be changed without modifing the rest of the code.
The game loop calls network class forward pass, therefore, it can play two different NN models against eachother
while calling the same functions since each network class can have its own NN model that is used for forward pass e.t.c.

____________________________________________________________________________________________
go_codercaste.py :
------------------

Holds all functions asociated with Go. Holds the main game loop. Game loop is initated by training.py and networks are passed to it.
Game loop will play the game between the two networks, using the network functions such as forward pass and update board.

!!!Once game loop recieves an array of move values
from forward pass function, it will choose the legal move with the highest value!!! 

(networks have no conception of legality of moves)

When the game is done,
score is calculated and returned along with the number of turns played.

NOTE!

This script was found online and was modified to fit with our other scritps.
As such, it is a bit messy. 
Source : http://www.codercaste.com/2013/02/22/read-set-go-how-to-create-a-go-board-game-in-python/


