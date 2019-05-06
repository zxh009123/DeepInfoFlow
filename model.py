import torch
import torch.nn as nn
import torch.optim as optim
import copy

class Model(nn.Module):
    def __init__(self, dims, train = True):
        super(Model,self).__init__()
        self.layer_dims = dims
        self.D = nn.ModuleList([])
        self.A = nn.ModuleList([])
        self._train = train
        self.construct_model_by_name('relu')


    def construct_model_by_name(self, name):
        depth = len(self.layer_dims) - 1
        numOfActiv = depth - 1

        if name == 'tanh':
            for i in range(depth):
                # setattr(self, 'Dense' + str(i), nn.Linear(self.layer_dims[i], self.layer_dims[i + 1]))
                if numOfActiv > 0:
                    # setattr(self, 'Activ' + str(i), nn.Tanh())
                    numOfActiv -= 1
                    self.A.append(nn.Tanh())
                self.D.append(nn.Linear(self.layer_dims[i], self.layer_dims[i + 1]))



        elif name == 'relu':
            for i in range(depth):
                # setattr(self, 'Dense' + str(i), nn.Linear(self.layer_dims[i], self.layer_dims[i + 1]))
                if numOfActiv > 0:
                    # setattr(self, 'Activ' + str(i), nn.ReLU())
                    numOfActiv -= 1
                    self.A.append(nn.ReLU())
                self.D.append(nn.Linear(self.layer_dims[i], self.layer_dims[i + 1]))
 

    def forward(self, x):
        if len(x.shape) > 2:
            print('dsfds')
            x = x.reshape(x.shape[0], -1)
        # if self._train:
        for i in range(len(self.layer_dims) - 1):
            dense = self.D[i]
            x = dense(x)
            if i < len(self.A):
                activ = self.A[i]
                x = activ(x)
        return x
        # else:
        #     outputs = []
        #     for i in range(len(self.layer_dims) - 1):
        #         dense = self.D[i]
        #         x = dense(x)
        #         if i < len(self.A):
        #             activ = self.A[i]
        #             x = activ(x) 
        #         outputs.append(x)
        #     return outputs


if __name__ == '__main__':
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") # device setup
    print(device)
    model = Model()
    print (model)
    model.apply(weights_init)
    model.to(device)
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
    
    #example forward
    dummy_x = torch.randn(5, 12) #feature
    dummy_y = torch.randint(0,1,(5,2)) #label
    dummy_x = dummy_x.to(device)
    dummy_y = dummy_y.to(device)
    result = model.forward(dummy_x) #inference
    print(result)

    criterion = nn.CrossEntropyLoss()# loss
    #example backprop
    loss = criterion(result, torch.max(dummy_y, 1)[1]) #calculate loss


    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(loss)




