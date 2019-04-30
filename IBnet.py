from __future__ import print_function
import numpy as np
import sys
import os, pickle
from collections import defaultdict, OrderedDict

import simplebinmi
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
sns.set_style('darkgrid')

import torch
import torch.nn as nn
import torch.optim as optim

from model import Model
from base_options import BaseOption
import utils
import datetime


class SaveActivations:
    def __init__(self):
        self._opt = BaseOption().parse()
        # check device
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") # device setup
        print("device: ",self.device)


        # dataset
        if self._opt.dataset == "mnist":
            train_data, test_data = utils.get_mnist()
            self.train_set = torch.utils.data.DataLoader(train_data, batch_size=self._opt.batch_size, shuffle=True, num_workers=self._opt.num_workers)
            self.test_set = torch.utils.data.DataLoader(test_data, batch_size=4, shuffle=True, num_workers=self._opt.num_workers)

            print("MNIST experiment")

            ######################################################
            # to do add initialize model method for mnist dataset#
            ######################################################
        elif self._opt.dataset == "IBNet":
            train_data = utils.CustomDataset('2017_12_21_16_51_3_275766', train=True)
            test_data = utils.CustomDataset('2017_12_21_16_51_3_275766', train=False)
            self.train_set = torch.utils.data.DataLoader(train_data, batch_size=self._opt.batch_size, shuffle=True, num_workers=self._opt.num_workers)
            self.test_set = torch.utils.data.DataLoader(test_data, batch_size=self._opt.batch_size, shuffle=True, num_workers=self._opt.num_workers)
            self.initialize_model()
            print("IBnet experiment")
        else:
            raise RuntimeError('Do not have {name} dataset, Please be sure to use the existing dataset'.format(name = dataset))

        # construct saving directory
        save_root_dir = self._opt.save_root_dir
        dataset = self._opt.dataset
        time = datetime.datetime.today().strftime('%m_%d_%H_%M')
        model = ''.join(list(map(lambda x:str(x) + '_', self.model.layer_dims)))
        self.path_to_dir = save_root_dir + '/' + dataset + '_Time_' + time + '_Model_' + model + '/'
        if not os.path.exists(self.path_to_dir):
            os.makedirs(self.path_to_dir)



    def initialize_model(self):
        # weight initialization
        def weights_init(m):
            if isinstance(m, nn.Linear):
                nn.init.xavier_normal_(m.weight.data)
                nn.init.constant_(m.bias.data, 0)
        # model construction
        self.model = Model()
        self.model.apply(weights_init)
        # optimizer 
        self.optimizer = optim.SGD(self.model.parameters(), lr=self._opt.lr, momentum=self._opt.momentum)
        # loss
        self.criterion = nn.CrossEntropyLoss() # loss

    def training_model(self):
        print('Begin training...')
        self.model.to(self.device)

        # main loop for training
        for i in range(0, self._opt.max_epoch):
            # set to train
            self.model.train()
            running_loss = 0.0
            running_acc = 0.0
            # batch training
            for j , (inputs, labels) in enumerate(self.train_set):
                inputs = inputs.to(self.device)
                labels = labels.to(self.device)
                # set to learnable
                with torch.set_grad_enabled(True):
                    outputs = self.model(inputs)
                    loss = self.criterion(outputs, labels)
                    _, preds = torch.max(outputs, 1)

                    self.optimizer.zero_grad()

                    loss.backward()

                    self.optimizer.step()

                    # logging for std mean and L2N
                    if self.needLog(i):
                        if self._opt.std:
                            self.std(i)
                        if self._opt.mean:
                            self.mean(i)
                        if self._opt.l2n:
                            self.l2n(i)
                # acc and loss calculation
                running_loss += loss * inputs.size(0)
                corrects = torch.sum(preds == labels.data).double()
                running_acc += corrects
                sys.stdout.flush()
                print('\repoch:{epoch} Loss: {loss:.6f} acc:{acc:.6f}'.format(epoch=i+1, loss=loss, acc=corrects), end="")
            epoch_loss = running_loss / len(self.train_set)
            epoch_acc = running_acc.double() / len(self.train_set)
            print("")
            print('------------------summary epoch {epoch} ------------------------'.format(epoch = i+1))
            print('Loss {loss:.6f} acc:{acc:.6f}'.format( loss=epoch_loss, acc=epoch_acc))
            print('----------------------------------------------------------------')

            
            break

            # saving model
            # uncomment to save model

            # save_full_path = self.generate_save_fullpath(i + 1)
            # torch.save({
            # 'epoch':i,
            # 'model_state_dict': self.model.state_dict(),
            # 'optimizer_state_dict': self.optimizer.state_dict(),
            # }, save_full_path)

    def needLog(self, epoch):
        # Only log activity for some epochs.  Mainly this is to make things run faster.
        if epoch < 20:       # Log for all first 20 epochs
            return True
        elif epoch < 100:    # Then for every 5th epoch
            return (epoch % 5 == 0)
        elif epoch < 2000:    # Then every 10th
            return (epoch % 20 == 0)
        else:                # Then every 100th
            return (epoch % 100 == 0)

    def mean(self, epoch):
        pass
        # for name, param in self.model.named_parameters():
        #     print(name.weight.grad)
        # to do implement gradient mean
    
    def std(self, epoch):
        pass
        # to do implement gradient standard deviation

    def l2n(self, epoch):
        pass
        # to do implement weights' L2 normalization
    
    def generate_save_fullpath(self, epoch):
        suffix = '.pth'
        fullpath = self.path_to_dir + 'model_epoch_' + str(epoch) + suffix
        return fullpath



    # def do_report(self, epoch):
    #     # Only log activity for some epochs.  Mainly this is to make things run faster.
    #     if epoch < 20:       # Log for all first 20 epochs
    #         return True
    #     elif epoch < 100:    # Then for every 5th epoch
    #         return (epoch % 5 == 0)
    #     elif epoch < 2000:    # Then every 10th
    #         return (epoch % 20 == 0)
    #     else:                # Then every 100th
    #         return (epoch % 100 == 0)
        
    #     reporter = loggingreporter.LoggingReporter(cfg=self.cfg, 
    #                                         trn=self.trn, 
    #                                         tst=self.tst, 
    #                                         do_save_func=self.do_report)



class ComputeMI:
    def __init__(self):
        self.trn, self.tst = utils.get_IB_data('2017_12_21_16_51_3_275766')
        self.FULL_MI = True
        self.infoplane_measure = 'upper'
        self.DO_SAVE        = True    # Whether to save plots or just show them
        self.DO_LOWER       = (self.infoplane_measure == 'lower')   # Whether to compute lower bounds also
        self.DO_BINNED      = (self.infoplane_measure == 'bin')     # Whether to compute MI estimates based on binning
        self.MAX_EPOCHS = 10000      # Max number of epoch for which to compute mutual information measure
        self.NUM_LABELS = 2
        # self.MAX_EPOCHS = 1000
        self.COLORBAR_MAX_EPOCHS = 10000
        self.ARCH = '12-10-7-5-4-3-2'
        self.DIR_TEMPLATE = '%%s_%s'%self.ARCH
        self.noise_variance = 1e-3                    # Added Gaussian noise variance
        self.binsize = 0.07                           # size of bins for binning method
        self.nats2bits = 1.0/np.log(2) # nats to bits conversion factor
        self.PLOT_LAYERS    = None
        self.measures = OrderedDict()
        self.init_measures()

    def init_measures(self):
        
        self.measures['tanh'] = {}
        self.measures['relu'] = {}
        # self.measures['softsign'] = {}
        # self.measures['softplus'] = {}


    def get_entropy_bound(self):
        # Klayer_activity = K.placeholder(ndim=2)  # Keras placeholder 
        # entropy_func_upper = K.function([Klayer_activity,], [kde.entropy_estimator_kl(Klayer_activity, noise_variance),])
        # entropy_func_lower = K.function([Klayer_activity,], [kde.entropy_estimator_bd(Klayer_activity, noise_variance),])
        return entropy_func_upper, entropy_func_lower

    def get_saved_labelixs_and_labelprobs(self):
        saved_labelixs = {}
        y = self.tst.y
        Y = self.tst.Y
        if self.FULL_MI:
            full = utils.construct_full_dataset(self.trn, self.tst)
            y = full.y
            Y = full.Y
        for i in range(self.NUM_LABELS):
            saved_labelixs[i] = y == i
        labelprobs = np.mean(Y, axis=0)

        return saved_labelixs, labelprobs

    def computeMI(self):
        entropy_func_upper, entropy_func_lower = self.get_entropy_bound()
        saved_labelixs, labelprobs = self.get_saved_labelixs_and_labelprobs()
        
        for activation in self.measures.keys():
            cur_dir = 'rawdata/' + self.DIR_TEMPLATE % activation
            if not os.path.exists(cur_dir):
                print("Directory %s not found" % cur_dir)
                continue
            # Load files saved during each epoch, and compute MI measures of the activity in that epoch
            print('*** Doing %s ***' % cur_dir)
            for epochfile in sorted(os.listdir(cur_dir)):
                if not epochfile.startswith('epoch'):
                    continue
                fname = cur_dir + "/" + epochfile
                with open(fname, 'rb') as f:
                    d = pickle.load(f)
                epoch = d['epoch']
                if epoch in self.measures[activation]: # Skip this epoch if its already been processed
                    continue                      # this is a trick to allow us to rerun this cell multiple times)
                if epoch > self.MAX_EPOCHS:
                    continue
                print("Doing", fname)
                num_layers = len(d['data']['activity_tst'])
                if self.PLOT_LAYERS is None:
                    self.PLOT_LAYERS = []
                    for lndx in range(num_layers):
                        #if d['data']['activity_tst'][lndx].shape[1] < 200 and lndx != num_layers - 1:
                        self.PLOT_LAYERS.append(lndx)
                cepochdata = defaultdict(list)
                for lndx in range(num_layers):
                    activity = d['data']['activity_tst'][lndx]
                    # Compute marginal entropies
                    h_upper = entropy_func_upper([activity,])[0]
                    if self.DO_LOWER:
                        h_lower = entropy_func_lower([activity,])[0]
                    # Layer activity given input. This is simply the entropy of the Gaussian noise
                    hM_given_X = kde.kde_condentropy(activity, self.noise_variance)
                    # Compute conditional entropies of layer activity given output
                    hM_given_Y_upper=0.
                    for i in range(self.NUM_LABELS):
                        hcond_upper = entropy_func_upper([activity[saved_labelixs[i],:],])[0]
                        hM_given_Y_upper += labelprobs[i] * hcond_upper
                    if self.DO_LOWER:
                        hM_given_Y_lower=0.
                        for i in range(self.NUM_LABELS):
                            hcond_lower = entropy_func_lower([activity[saved_labelixs[i],:],])[0]
                            hM_given_Y_lower += labelprobs[i] * hcond_lower
                    cepochdata['MI_XM_upper'].append( self.nats2bits * (h_upper - hM_given_X) )
                    cepochdata['MI_YM_upper'].append( self.nats2bits * (h_upper - hM_given_Y_upper) )
                    cepochdata['H_M_upper'  ].append( self.nats2bits * h_upper )
                    pstr = 'upper: MI(X;M)=%0.3f, MI(Y;M)=%0.3f' % (cepochdata['MI_XM_upper'][-1], cepochdata['MI_YM_upper'][-1])
                    
                    if self.DO_LOWER:  # Compute lower bounds
                        cepochdata['MI_XM_lower'].append(self.nats2bits * (h_lower - hM_given_X) )
                        cepochdata['MI_YM_lower'].append(self.nats2bits * (h_lower - hM_given_Y_lower) )
                        cepochdata['H_M_lower'  ].append(self.nats2bits * h_lower )
                        pstr += ' | lower: MI(X;M)=%0.3f, MI(Y;M)=%0.3f' % (cepochdata['MI_XM_lower'][-1], cepochdata['MI_YM_lower'][-1])

                    if self.DO_BINNED: # Compute binned estimates
                        binxm, binym = simplebinmi.bin_calc_information2(saved_labelixs, activity, self.binsize)
                        cepochdata['MI_XM_bin'].append( self.nats2bits * binxm )
                        cepochdata['MI_YM_bin'].append( self.nats2bits * binym )
                        pstr += ' | bin: MI(X;M)=%0.3f, MI(Y;M)=%0.3f' % (cepochdata['MI_XM_bin'][-1], cepochdata['MI_YM_bin'][-1])
                    print('- Layer %d %s' % (lndx, pstr) )
                self.measures[activation][epoch] = cepochdata

if __name__ == "__main__":
    test = SaveActivations()
    test.training_model()
