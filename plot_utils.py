import matplotlib
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from cycler import cycler
import numpy as np
import datetime
import os

np.random.seed()

# matplotlib.use("TKAgg")
'''NOTE
Seem for conda env, one must create a file `matplotlibrc` at the directory `~/.matplotlib`,
and add the following content in this file:
                                            backend : TKAgg
see for reference: https://github.com/matplotlib/matplotlib/issues/13414
'''

class PlotFigure:
    def __init__(self, opt, model_name):
        self.name = 'Plot_Utils'
        self._opt = opt

        # NOTE we save figures in two places: the plot_root and results/model_path
        # check existence of plot_root
        self.plot_dir = opt.plot_dir
        if not os.path.exists(opt.plot_dir):
            os.mkdir(opt.plot_dir)

        self.model_name = model_name
        tmp_dir = os.path.join('./results', model_name)
        self.model_path = os.path.join(tmp_dir, 'plots')
        if not os.path.exists(self.model_path):
            os.mkdir(self.model_path)

##NOTE old code for plot MI plane
    # def plot_MI_plane_1(self, MI_X_T, MI_Y_T):
    #     '''
    #     plot evolution of mutual information for each layer at different eporchs
    #     '''
    #     fig = plt.figure(figsize=(7,7))#, facecolor='#edf0f8')
    #     # f, ax = plt.subplots(1,1)
    #     ax = fig.add_subplot(1,1,1)

    #     # set colormap and font
    #     sm = plt.cm.ScalarMappable(cmap='gnuplot', 
    #                                norm=plt.Normalize(vmin=0, vmax=self._opt.max_epoch))
    #     sm._A = []
    #     csfont = {'fontname':'Times New Roman'}
        
    #     Lepoch = MI_X_T.keys()
    #     for epoch in Lepoch:
    #         ax.plot(MI_X_T[epoch], MI_Y_T[epoch], c=sm.to_rgba(epoch), alpha=0.1, zorder=1)
    #         ax.scatter(MI_X_T[epoch], MI_Y_T[epoch], s=40, facecolor=sm.to_rgba(epoch), zorder=2)

    #     ax.set_title('Information Plane', fontsize = 26, y=1.04, **csfont)
    #     ax.set_xlabel('$\mathcal{I}(X;T)$', fontsize = 22)
    #     ax.set_ylabel('$\mathcal{I}(Y;T)$', fontsize = 22)
    #     # ax.set_xlim(left = 0.)
    #     # ax.set_ylim(bottom = 0.)
    #     ax.set_aspect(1. / ax.get_data_ratio())
    #     ax.set_facecolor('#edf0f8')
    #     ax.grid(color='w', linestyle='-.', linewidth = 1)
    #     ax.tick_params(labelsize = 13)

    #     # cbaxes = fig.add_axes([1.0, 0.125, 0.03, 0.8]) 
    #     fig.colorbar(sm, label='Epoch', fraction=0.0454, pad=0.05)#, cax=cbaxes)

    #     # set dir for mean_std; saving figure
    #     self._save_fig(fig, 'InfoPlan_original')
##

    def plot_MI_plane(self, MI_X_T, MI_Y_T, IS_LAYERWISE_PLOT = True):
        '''
        plot evolution of mutual information for each layer at different eporchs
        MI_X_T & MI_Y_T: dictionary, key -> #epoch, value -> List of len Nlayers 
        '''
        Nlayers = len(MI_X_T[0])
        Lepoch = MI_X_T.keys()

        # set colormap
        sm = plt.cm.ScalarMappable(cmap='gnuplot', 
                                   norm=plt.Normalize(vmin=0, vmax=self._opt.max_epoch))
        sm._A = []
        
        ## plot MI in info plane, containing all layers
        fig_ = plt.figure(figsize=(7,7))
        ax_ = fig_.add_subplot(1,1,1)

        for epoch in Lepoch:
            ax_.plot(MI_X_T[epoch], MI_Y_T[epoch], c=sm.to_rgba(epoch), alpha=0.1, zorder=1)
            ax_.scatter(MI_X_T[epoch], MI_Y_T[epoch], s=40, facecolor=sm.to_rgba(epoch), zorder=2)

        # ax setting
        self._commom_ax_setting_MI_plane(ax_)
        # ax_.set_xlim(left = 0.)
        # ax_.set_ylim(bottom = 0.)
        
        # set color bar
        fig_.colorbar(sm, label='Epoch', fraction=0.0454, pad=0.05)

        # saving figure (single figure containing all layers)
        self._save_fig(fig_, 'InfoPlan_original')

        ## plot MI in info plane, one figure for each layer
        if IS_LAYERWISE_PLOT:

            ax_xrange = ax_.get_xlim()
            ax_yrange = ax_.get_ylim()

            fig = plt.figure(figsize=(20,18), constrained_layout=False)
            gs = GridSpec(3, int(Nlayers/3) + 1, figure=fig, wspace=0.15, hspace=0.25)

            # plotting
            L = -1
            termin = False
            for i in range(3):
                if termin:
                    break
                for j in range(3):
                    L += 1
                    if L >= Nlayers:
                        termin = True
                        break

                    ax = fig.add_subplot(gs[i, j])
                    for epoch in Lepoch:
                        ax.scatter(MI_X_T[epoch][L], MI_Y_T[epoch][L], s=40, facecolor=sm.to_rgba(epoch))

                    # ax setting (note must set_x(y)lim before self._commom_ax_setting_MI_plane)
                    ax.set_xlim(ax_xrange)
                    ax.set_ylim(ax_yrange)
                    self._commom_ax_setting_MI_plane(ax, layer_idx = L)

            fig.subplots_adjust(left = 0.05, bottom=0.05, top=0.95, right=0.9)
            cbaxes = fig.add_axes([0.9, 0.05, 0.03, 0.9]) #rect = l,b,w,h
            fig.colorbar(sm, label='Epoch', cax=cbaxes)

            # saving figure
            self._save_fig(fig, 'InfoPlan')

    def _commom_ax_setting_MI_plane(self, ax, layer_idx = -1):
        # set font
        csfont = {'fontname':'Times New Roman'}

        if layer_idx == -1:
            ax.set_title('Information Plane'+" ("+self._opt.activation+")", fontsize = 26, y=1.04, **csfont)
        else:
            ax.set_title('Information Plane (layer'+str(layer_idx+1)+" "+self._opt.activation+")", fontsize = 26, **csfont)
        ax.set_xlabel('$\mathcal{I}(X;T)$', fontsize = 22)
        ax.set_ylabel('$\mathcal{I}(Y;T)$', fontsize = 22)
        ax.set_aspect(1. / ax.get_data_ratio())
        ax.set_facecolor('#edf0f8')
        ax.grid(color='w', linestyle='-.', linewidth = 1)
        ax.tick_params(labelsize = 13)

## NOTE old plot mean std code for single mean_std figure, 2019-05-24
    # def plot_mean_std(self, Lepoch, mu, sigma):
    #     '''
    #     plot the variation of mean and standard devidation for each layer with respect to epoch

    #     Lepoch    --- array of recorded epochs; of dim (Nepoch,)
    #     mu, sigma --- mean & standard deviation; of dim (Nlayers, feature_dim)
    #     '''
    #     Nlayers = mu.shape[1]

    #     fig = plt.figure(figsize=(9,7))
    #     ax = fig.add_subplot(1,1,1)
    #     legend_mean = []
    #     legend_std  = []
    #     layer_mark = ['layer'+str(i+1) for i in range(Nlayers)]
        
    #     # set color and font
    #     csfont = {'fontname':'Times New Roman'}
    #     colors = ['b', 'r', 'g', 'c', 'm', 'y', 'orange', 'darkgreen']
        
    #     for L in range(Nlayers):
    #         legend_mean += ax.plot(Lepoch, mu[:,L], c = colors[L] ,ls='-')
    #         legend_std  += ax.plot(Lepoch, sigma[:,L], c = colors[L], ls='-.')
    
    #     # ax settings
    #     ax.set_title(self._opt.activation)
    #     fig.subplots_adjust(right = 0.86)
    #     ax.set_xscale('log')
    #     ax.set_yscale('log')
    #     ax.set_ylim(bottom=1.e-5)
    #     ax.set_xlabel('number of epochs', fontsize=22, **csfont)
    #     ax.set_ylabel('Means and Standard Deviations', fontsize=22, **csfont)
    #     ax.set_facecolor('#edf0f8')
    #     ax.grid(color='w', linestyle='-.', linewidth=1)
    #     ax.tick_params(labelsize=13)
    #     leg_mean = ax.legend(legend_mean, layer_mark,  bbox_to_anchor=[1.15, 1], title='Mean')
    #     leg_std  = ax.legend(legend_std, layer_mark,  bbox_to_anchor=[1.15, 0.6], title='STD')
    #     ax.add_artist(leg_mean)
    #     ax.add_artist(leg_std)

    #     # set dir for mean_std; saving figure
    #     self._save_fig(fig, 'Mean_and_STD')
##

    def plot_mean_std(self, Lepoch, mu, sigma):
        '''
        plot the variation of mean and standard devidation for each layer with respect to epoch

        Lepoch    --- array of recorded epochs; of dim (Nepoch,)
        mu, sigma --- mean & standard deviation; of dim (Nlayers, feature_dim)
        '''

        Nlayers = mu.shape[1]

        fig = plt.figure(figsize=(18,14), constrained_layout=True)
        gs = GridSpec(2, 2, figure=fig, wspace=0.0, hspace=0.0)

        # intial legend setting
        legend_mean = []
        legend_std  = []
        layer_mark = ['layer'+str(i+1) for i in range(Nlayers)]
        
        # set color
        colors = ['b', 'r', 'g', 'c', 'm', 'y', 'orange', 'darkgreen']

        # plotting
        # 1- mixed mean and std
        ax1 = fig.add_subplot(gs[0, 0])
        for L in range(Nlayers):
            ax1.plot(Lepoch, mu[:,L], c = colors[L] ,ls='-')
            ax1.plot(Lepoch, sigma[:,L], c = colors[L], ls='-.')

        ax1.set_ylim(bottom=1.e-5)
        self._commom_ax_setting_mean_std(ax1, "Mean and STD", show_xlabel=False)

        # 2- mean
        ax2 = fig.add_subplot(gs[0, 1])
        for L in range(Nlayers):
            legend_mean += ax2.plot(Lepoch, mu[:,L], c = colors[L] ,ls='-')

        ax2.set_ylim(ax1.get_ylim())
        self._commom_ax_setting_mean_std(ax2, "Mean", show_ylabel=False)

        # 3- std
        ax3 = fig.add_subplot(gs[1, 0])
        for L in range(Nlayers):
            legend_std  += ax3.plot(Lepoch, sigma[:,L], c = colors[L], ls='-.')

        ax3.set_ylim(ax1.get_ylim())
        self._commom_ax_setting_mean_std(ax3, "STD")        

        # set legend
        fig.legend(legend_mean, layer_mark, bbox_to_anchor = [0.75, 0.38], 
                   title="Mean", title_fontsize = 17, fontsize = 17)
        fig.legend(legend_std,  layer_mark, bbox_to_anchor=[0.85, 0.38],  
                   title="STD",  title_fontsize = 17, fontsize = 17)

        # set dir for mean_std; saving figure
        self._save_fig(fig, 'Mean_and_STD')
    
    def _commom_ax_setting_mean_std(self, ax, title_name, show_xlabel=True, show_ylabel=True):
        # set font
        csfont = {'fontname':'Times New Roman'}

        ax.set_title(title_name+" ("+self._opt.activation+")", fontsize=20, **csfont)
        if show_xlabel:
            ax.set_xlabel('number of epochs', fontsize=22, **csfont)
        if show_ylabel:
            ax.set_ylabel('Means and Standard Deviations', fontsize=22, **csfont)

        ax.set_xscale('log')
        ax.set_yscale('log')

        ax.set_facecolor('#edf0f8')
        ax.grid(color='w', linestyle='-.', linewidth = 1)
        ax.tick_params(labelsize = 13)


    def plot_svd(self, Lepoch, svd):
        '''
        plot for both original and normalized versions
        '''
        self._func_plot_svd(Lepoch, np.array(svd[0]), "_original")
        self._func_plot_svd(Lepoch, np.array(svd[1]), "_normalized")


    def _func_plot_svd(self, Lepoch, weight_svd, nameflag):
        '''
        plot the variation of singular value for the averaged weight of each layer with respect to epoch

        Lepoch    --- array of recorded epochs; of dim (Nepoch,)
        svd       --- list, [[svd_w] [svd_grad]]; [svd_w] = [ [ svd_w_layer_1, ... svd_w_layer_n ]_epoch_1, ... ]
        '''
        Nlayers = len(weight_svd[0])

        fig = plt.figure(figsize=(25,20), constrained_layout=True)
        gs = GridSpec(3, int(Nlayers/3) + 1, figure=fig, wspace=0.0, hspace=0.0)

        # set color and font
        colors = ['b', 'r', 'g', 'c', 'm', 'y', 'orange', 'darkgreen']
        cy = cycler('color', colors)
        csfont = {'fontname':'Times New Roman'}

        # initialize legend settting
        # legend_svd_w = []
        # layer_mark = ['layer'+str(i+1) for i in range(Nlayers)]

        # plotting
        L = -1
        termin = False
        for i in range(3):
            if termin:
                break
            for j in range(3):
                L += 1
                if L >= Nlayers:
                    termin = True
                    break
                svd_val = list(weight_svd[:,L])
                ax = fig.add_subplot(gs[i, j])
                ax.plot(Lepoch, svd_val ,ls='-', marker='o', ms = 4)
    
                # ax settings
                ax.set_prop_cycle(cy)
                ax.set_title('layer'+str(L+1)+' ('+self._opt.activation+')', fontsize=20, **csfont)
                ax.set_xscale('log')
                ax.set_ylim(bottom = 0.)
                if i == 2:
                    ax.set_xlabel('number of epochs', fontsize = 22, **csfont)
                if j == 0:
                    ax.set_ylabel('Singular Values', fontsize = 22, **csfont)
                ax.set_facecolor('#edf0f8')
                ax.grid(color='w', linestyle='-.', linewidth = 1)
                ax.tick_params(labelsize = 13)
        
        # set legend
        # leg_svd_w = ax.legend(legend_svd_w, layer_mark,  bbox_to_anchor=[1.15, 1], title='svd_w')
        # ax.add_artist(leg_svd_w)

        # set dir for mean_std; saving figure
        self._save_fig(fig, 'SingularValues'+nameflag)


    def _save_fig(self, fig, fig_name):
        # save in model_path
        fig_name_eps = os.path.join(self.model_path, "{}.eps".format(fig_name))
        fig.savefig(fig_name_eps, format='eps')

        fig_name_jpg = os.path.join(self.model_path, "{}.jpg".format(fig_name))
        fig.savefig(fig_name_jpg, format='jpeg')

        # save in plot_root
        fig_name_eps = os.path.join(self.plot_dir, "{}_{}.eps".format(fig_name, self.model_name))
        fig.savefig(fig_name_eps, format='eps')

        fig_name_jpg = os.path.join(self.plot_dir, "{}_{}.jpg".format(fig_name, self.model_name))
        fig.savefig(fig_name_jpg, format='jpeg')




def main():
    '''test run
    '''
    # test data for plot_MI_plane
    x = {0: np.array([0.51842304, 0.92556737, 0.36004445, 0.11063085, 0.89165   ]),
         1: np.array([0.52649129, 0.45103952, 0.63225806, 0.0176416,  0.94888   ])
    }  
    y = {0: np.array([0.63147293, 0.59704809, 0.67011044, 0.01976542, 0.95609   ]),
         1: np.array([0.63147293, 0.59704809, 0.67011044, 0.01976542, 0.95609   ])
    }

    # test data for plot_MI_plane
    Lepoch = np.array([1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,200,300,400,500,600,700,800,900])
    mu = np.random.rand(1, Lepoch.shape[0])
    sigma = np.random.rand(1, Lepoch.shape[0])

    C = type('type_C', (object,), {})
    opt = C()

    opt.plot_dir = './plots'
    opt.max_epoch = 10
    model_name = 'testdrawing'
    # opt.timestamp = '19050310'
    pltfig = PlotFigure(opt, model_name)
    pltfig.plot_MI_plane(x,y)
    # pltfig.plot_mean_std(Lepoch, mu, sigma)
    

if __name__ == "__main__":
    main()