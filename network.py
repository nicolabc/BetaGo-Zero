import random
import utils2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import copy

boardsize = 9
learningRate = 0.5

class Network:
	
	
	def __init__(self):

		self.size = boardsize
		self.mynet = TwoLayerNet()
		
		self.name = chr(random.randint(65,90))
		self.name = ""+self.name
		self.historyLen = 3
		self.featuresDim = self.historyLen*2+1
		self.features = np.empty([1, self.featuresDim,9,9])

	def forwardPass(self,board):
		#split board into feature layers
		
		#first, move previous back
		for i in range(1,self.historyLen):
			self.features[0][(self.historyLen-i)*2] = copy.deepcopy(self.features[0][(self.historyLen-i-1)*2])
			self.features[0][(self.historyLen-i)*2+1] = copy.deepcopy(self.features[0][(self.historyLen-i-1)*2+1])
		
		
		for x in range(0,9):
			for y in range(0,9):
				if(board[x][y] == "o"):
					self.features[0][0][x][y] = 1
					self.features[0][1][x][y] = 0
				elif(board[x][y] == "x"):
					self.features[0][0][x][y] = 0
					self.features[0][1][x][y] = 1
				else:
					self.features[0][0][x][y] = 0
					self.features[0][1][x][y] = 0

		
		
		cuda0 = torch.device('cuda:0')
		self.features = torch.tensor(self.features,dtype=torch.float,device=cuda0,requires_grad=False)
		
						
		
		return self.mynet.forward(self.features)
	def updateBoard(self,board):
		
		for i in range(1,self.historyLen):
			self.features[0][(self.historyLen-i)*2] = copy.deepcopy(self.features[0][(self.historyLen-i-1)*2])
			self.features[0][(self.historyLen-i)*2+1] = copy.deepcopy(self.features[0][(self.historyLen-i-1)*2+1])
		
		0.5
		
		for x in range(0,9):
			for y in range(0,9):
				if(board[x][y] == "o"):
					self.features[0][0][x][y] = 1
					self.features[0][1][x][y] = 0
				elif(board[x][y] == "x"):
					self.features[0][0][x][y] = 0
					self.features[0][1][x][y] = 1
				else:
					self.features[0][0][x][y] = 0
					self.features[0][1][x][y] = 0

		return -1
	
	def clone(self):
		network = Network()
		network.mynet = copy.deepcopy(self.mynet)
		network.name = self.name+network.name
		return network
	def mutate(self):
		self.mynet.mutate(learningRate)
	
		
	def initForMatch(self,asBlack):
		self.mynet = utils2.to_cuda(self.mynet)
		self.features = np.zeros([1, self.featuresDim,9,9])
		if(asBlack):
			print("IS BLACK")
			self.features[0][self.featuresDim-1] = 1
		
	
class TwoLayerNet(nn.Module):
	def __init__(self):
		"""
		In the constructor we instantiate two nn.Linear modules and assign them as
		member variables.

		D_in: input dimension
		H: dimension of hidden layer
		D_out: output dimension


		"""
		num_filters1 = 32
		self.featuresDim = 3*2+1
		super(TwoLayerNet, self).__init__()
		self.conv1 = nn.Sequential(
            		nn.Conv2d(in_channels = self.featuresDim,out_channels=num_filters1,kernel_size=3,stride=1,padding=1),
			nn.ReLU(),
			#nn.MaxPool2d(kernel_size=2, stride=2, padding=0),
			nn.BatchNorm2d(num_filters1)
            
        	)
		self.conv2 = nn.Sequential(
            		nn.Conv2d(in_channels = num_filters1,out_channels=num_filters1*2,kernel_size=3,stride=1,padding=1),
			nn.ReLU(),
			#nn.MaxPool2d(kernel_size=2, stride=2, padding=0),
			nn.BatchNorm2d(num_filters1*2)
            
        	)
		self.conv3 = nn.Sequential(
            		nn.Conv2d(in_channels = num_filters1*2,out_channels=num_filters1*4,kernel_size=3,stride=1,padding=1),
			nn.ReLU(),
			nn.MaxPool2d(kernel_size=2, stride=2, padding=0),
			nn.BatchNorm2d(num_filters1*4)
            
        	)
		
		self.conv4 = nn.Sequential(
            		nn.Conv2d(in_channels = num_filters1*4,out_channels=num_filters1*8,kernel_size=3,stride=1,padding=1),
			nn.ReLU(),
			nn.MaxPool2d(kernel_size=2, stride=2, padding=0),
			nn.BatchNorm2d(num_filters1*8)
            
        	)
		
		self.postConvDim = num_filters1*8*2*2
		outputdim = 82
		self.classifier = nn.Sequential(
            		nn.Linear(self.postConvDim,outputdim*1),
					nn.ReLU(),
            		nn.Linear(outputdim*1,outputdim*1),
					nn.ReLU(),
            		nn.Linear(outputdim*1,outputdim*1),
					nn.ReLU(),
            		nn.Linear(outputdim*1, outputdim),
        	)

		#initializiation
		for name, param in self.named_parameters():
			#print(list(param.data.size()))
			torch.nn.init.uniform_(param, a=-1, b=1)

		

	def forward(self, x):
		"""
		In the forward function we accept a Variable of input data and we must 
		return a Variable of output data. We can use Modules defined in the 
		constructor as well as arbitrary operators on Variables.
		"""
		with torch.no_grad():
			x = self.conv1(x)
			x = self.conv2(x)
			x = self.conv3(x)
			x = self.conv4(x)
			x = x.view(-1,self.postConvDim)
			
			y_pred = self.classifier(x)	

			return y_pred.cpu().numpy()
	
	def mutate(self,learningRate):
		model = self
		cuda0 = torch.device('cuda:0')
		for name, param in model.named_parameters():
			#print(list(param.data.size()))
			shape = param.data.size()
			adding = (torch.rand(shape)*2-1)*learningRate
			adding = torch.tensor(adding,device=cuda0,requires_grad = False)	
			param.data += adding

		


