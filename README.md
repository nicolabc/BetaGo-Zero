# Go

Final project in TDT4265 - Computer Vison and Deep Learning at NTNU using Deep Reinforcement Learning with Genetic Algorithm to train an AI to play the game of Go on a 9x9 board. The rules used in the implementation is Chinese rules, also known as area rules
See the [wikipage](https://en.wikipedia.org/wiki/Go_(game)) for more info

<a href="url"><img src="https://www.schaakengo.nl/images/productimages/big/beuken-vineer-9x9-2-.jpg" height="450" width="450" ></a>

> Please have a look at the PDF files [TDT4265_Final_project_proposal.pdf](TDT4265_Final_project_proposal.pdf) and [Learning to play Go - Final presentation.pdf](https://github.com/nicolabc/Go/blob/master/Learning%20to%20play%20Go%20-%20Final%20presentation.pdf) to see our final results

You may read the other suggested final projects for the course [here](https://www.overleaf.com/read/xgqfysbtbcpd)

## Motivation
The motivation behind the project is the recent advancement of AI using Reinforcement Learning, and specially the AlphaGo and AlphaGo Zero created by Google DeepMind. The [documentary](https://www.youtube.com/watch?v=8tq1C8spV_g) also contributed to the motivation behind the project. Read more about Google DeepMind's AlphaGo Zero project [here](https://deepmind.com/blog/alphago-zero-learning-scratch/)

## Module description
Environment: `Python3` `Pytorch`
Following scripts are of most importance:
____________________________________________________________________________________________
### training.py : 
------------------

Holds the main training loop and functions asociated with mutation of networks, elimination and cloning of networks
____________________________________________________________________________________________
### network.py : 
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
### go_codercaste.py :
------------------

Holds all functions asociated with Go. Holds the main game loop. Game loop is initated by training.py and networks are passed to it.
Game loop will play the game between the two networks, using the network functions such as forward pass and update board.

!!!Once game loop recieves an array of move values
from forward pass function, it will choose the legal move with the highest value!!! 

(networks have no conception of legality of moves)

When the game is done,
score is calculated and returned along with the number of turns played.

>NOTE!
This script go_codercaste.py was found online and was heavily modified to fit with our other scritps.
As such, it is a bit messy. 
Source: http://www.codercaste.com/2013/02/22/read-set-go-how-to-create-a-go-board-game-in-python/

## Contact

Nicolas B. Carbone – [@LinkedIn](https://www.linkedin.com/in/nicolas-blystad-carbone-b46378150/) – nicolasbcarbone@gmail.com

Distributed under the MIT license. See ``LICENSE`` for more information.

## Credits
Credits goes to my partner for the project [Seva Karpov](https://www.facebook.com/seva.karpov.7) - [GitHub](https://github.com/SevaKarpov)
