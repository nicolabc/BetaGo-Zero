#!/usr/bin/env python

import go_codercaste as go
import random
import torch
import numpy as np
import network

#Make one network
def createNewCNN():

	return network.Network()

#Initialize networks
#returns a dictionary with networks as keys and scores as values
def InitializeNetworks(amount):
	networkDict = {}
	for i in range(0,amount):
		newNetwork = createNewCNN()
		networkDict[newNetwork] = 0.0

	return networkDict

#loads saved networks
def LoadNetworks(loadAmount,cloneFactor):
	networkdict = {}
	for i in range(0,loadAmount):
		net = network.Network()
		
		net.mynet.load_state_dict(torch.load("saves2/net"+str(i)+".pth"))
		net.mynet.eval()

		
		networkdict[net] = 0.0
		
		for g in range(0,cloneFactor):
			cloneModel = net.clone()
			networkdict[cloneModel] = 0.0
	return networkdict

def LoadValidationNet():
	net = network.Network()
	net.mynet = network.TwoLayerNet()
	net.mynet.load_state_dict(torch.load("saves2/net0.pth"))
	net.mynet.eval()

	return net

#Play a game between two networks
#returns 1,0 of 1 won and 0,1 if 2 won
def PlayOneGame(network1,network2,pringProgress):

	network1.initForMatch(True)
	network2.initForMatch(False)
	#plays one game, call here, get results 
	#print("PLAYING : ",network1.name," VS ",network2.name)
	n1won,n2won = go.playFullGame(network1,network2,pringProgress)
	'''
	if(n1won>n2won):
		n1won = 1
		n2won = 0
	else:
		n1won = 0
		n2won = 1
	'''
	return n1won,n2won
	
#Plays all networks against one another
#each network plays against another two times, one for each color config
#score are recorded in networkDict
def PlayAll(networkdict):
	
	networks = networkdict.keys()
	for net1 in networks:
		for net2 in networks:
			if net1 != net2:
				n1won,n2won = PlayOneGame(net1,net2,False)
				networkdict[net1]+=n1won
				networkdict[net2]+=n2won
	return networkdict

def PlayAllValidation(networkdict,validationNet):
	networks = networkdict.keys()
	average = 0
	for net in networks:
		n1won,n2won = PlayOneGame(net,validationNet,False)
		networkdict[net]+=n1won
		average+=n1won
		n1won,n2won = PlayOneGame(validationNet,net,False)
		networkdict[net]+=n2won
		average+=n2won

	#computes average
	average = average/(2.0*len(networkdict))
	f= open("validation.txt","a+")
	f.write(str(average)+'\n')
	f.close()

	print("_______________AVERAGE_______________")
	print(average)
	print("_____________________________________")

	#return networkdict

#Eliminates 50% of the networks
#those chosen to be eliminated are based on a formula
#so that most of the highest are chosen but some of the weakest survive as well

def PerformElimination(networkdict):
	#sort by highest first
	networks = list(networkdict.keys())	
	keydict = dict(zip(networks, networkdict.values()))
	networks.sort(key=keydict.get)
	networks.reverse()
	#select 50% so that top 50% are most likely
	probabilities = [0]*len(networks)
	for i in range(0,len(networks)):
		probabilities[i] = random.randint(len(networks)-i,len(networks))
	
	newNetworks = [networks[0]]*((int)(len(networks)/2))
	count = 0
	threshold = len(networks)
	while(count < len(newNetworks)):
		threshold -= 1
		index = 0
		while(index<len(networks) and count < len(newNetworks)):
			if(probabilities[index]>threshold):
				
				del probabilities[index]
				newNetworks[count] = networks[index]
				count+=1
				del networks[index]
				
								
				
			index+=1
		
	newNetworkDict = {}
	for net in newNetworks:
		newNetworkDict[net] = 0.0
	
	return newNetworkDict

		
		
def PerformCloning(networkdict):
	
	newNetworkDict = {}
	for net in networkdict.keys():	
		newNetworkDict[net] = 0.0
		newNetworkDict[net.clone()] = 0.0
	
	return newNetworkDict

def PerformMutation(networkdict):
	for net in networkdict.keys():
		net.mutate()
	return networkdict

#TESTING

#board = np.empty((9,9))
#print(board)
#print(newNet.forwardPass(board))
#print(createNewCNN().mutate())
'''
net2 = network.Network()
		
net2.mynet.load_state_dict(torch.load("saves2/net"+str(0)+".pth"))
net2.mynet.eval()

net1 = network.Network()
net1.mynet = network.TwoLayerNet()
net1.historyLen = 3
net1.featuresDim = 7
net1.mynet.load_state_dict(torch.load("saves/net0.pth"))

n1,n2=PlayOneGame(net1,net2,True)
won1 = n1
won2 = n2
n2,n1=PlayOneGame(net2,net1,True)
won1 += n1
won2 += n2

print("RESULT")
print(won1, "  ", won2)
'''

thisdict = InitializeNetworks(10)

#thisdict = LoadNetworks(5,0)
#print(len(thisdict))

networks = list(thisdict.keys())
print("SAMPLE")
PlayOneGame(networks[0],networks[1],True)
print("SAMPLE")
PlayOneGame(networks[1],networks[0],True)

#thisdict = PerformMutation(thisdict)
print("NAMES")
for net in thisdict.keys():
	print(net.name)

epoch = 0
grandEpoch = 0
print("TRAINING")

validationNet = LoadValidationNet()

while(epoch < 20):
	
	thisdict = PlayAll(thisdict)
	#PlayAllValidation(thisdict,validationNet)
	print("CURRENT EPOCH ",grandEpoch)
	print("SCORES ")
	for net in thisdict.keys():
		print(net.name, " score: ",thisdict[net])
	print("__________________")

	if(epoch >= 5):
		PlayAllValidation(thisdict,validationNet)
		print("SAMPLE")
		networks = list(thisdict.keys())	
		keydict = dict(zip(networks, thisdict.values()))
		networks.sort(key=keydict.get)
		networks.reverse()
		PlayOneGame(networks[0],validationNet,True)
		print("SAMPLE")
		PlayOneGame(validationNet,networks[0],True)
		epoch = 0
		for i in range(0,len(networks)):
			torch.save(networks[i].mynet.state_dict(), "saves3/net"+str(i)+".pth")

	thisdict = PerformElimination(thisdict)
	thisdict = PerformCloning(thisdict)
	thisdict = PerformMutation(thisdict)
	epoch += 1
	grandEpoch+=1
	print(epoch)
	print("____NAMES Post____")
	for net in thisdict.keys():
		print(net.name)
	print("__________________")



print("NAMES Post")
for net in thisdict.keys():
	print(net.name)




