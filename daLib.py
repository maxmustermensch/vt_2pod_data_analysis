#!/usr/bin/env python
# coding: utf-8

# In[9]:

import os
import re
import glob
import math
import numpy             as np
import matplotlib.pyplot as plt
from pandas              import DataFrame
from datetime            import datetime
from scipy.interpolate   import make_interp_spline
from scipy.optimize      import curve_fit
from matplotlib          import rcParams

threshold = np.linspace(0.01, 60, 31)  #not used
slope = np.linspace(0.01, 10, 50)      #not used
gamma = np.linspace(0.01, 0.99, 100)   #used for prob o gamma
delta = 0.02                           #not used

class da:
    def __init__(self, TSIDs, file_path):
        self.TSIDs = TSIDs
        self.file_path = file_path

        #Allocate Data in Variables:

        for self.TSID in self.TSIDs:
            self.fpTS = os.path.join(self.file_path, self.TSID)

            for self.file in os.listdir(self.fpTS):
                if os.path.splitext(self.file)[1] == '.npy':
                    self.x = re.split("_", self.file)
                    if "user" in self.x:
                        del self.x[self.x.index("user")]
                    globals()[self.x[0] + "_" + self.x[1] + "_" + self.x[2] + "_" + self.x[3]] = np.load(os.path.join(self.fpTS, self.file), allow_pickle=True)


        
    #Function: True Values Proportion Correct over StimRange:

    def propcortrue(self, bs, hv):
        StimRespALL = np.zeros(shape=[len(self.TSIDs), len(globals()[self.TSIDs[0]+'_'+bs+'_'+hv+'_stim']), 2])

        t = 0
        for TSID in self.TSIDs:

            stim = globals()[TSID+'_'+bs+'_'+hv+'_stim']
            resp = globals()[TSID+'_'+bs+'_'+hv+'_response']

            StimResp = np.zeros(shape=[len(stim), 2])
            for i in range(0,len(stim)):
                StimResp[i] = [stim[i], resp[i]]

            StimRespALL[t] = StimResp

            t=t+1

        StimRange = globals()[TSID+'_'+bs+'_'+hv+'_stimRange']

        StimRespCounter = np.zeros(shape=[3, len(StimRange)])
        StimRespCounter[2] = StimRange

        for a in StimRespALL:
            for b in a:

                x = np.where(StimRespCounter[2] == b[0])
                StimRespCounter[0][x] = StimRespCounter[0][x]+b[1]
                StimRespCounter[1][x] = StimRespCounter[1][x]+1

        #________________________________________________


        plt.rc('font', size=14)
        fig = plt.figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        plt.tight_layout()

        x_values = StimRespCounter[2]
        y_values = np.round_(StimRespCounter[0]/StimRespCounter[1], 2)


        ax.plot(x_values, y_values, color='k', linestyle='-')


        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        #plt.savefig(TSID + '_Prob_o_Gamma')

        plt.show()

        #

        #dispData = DataFrame([StimRespCounter[2], 
        #                         StimRespCounter[0], 
        #                         StimRespCounter[1],
        #                         np.round_(StimRespCounter[0]/StimRespCounter[1], 2)]).T
        #dispData.style.hide_index()
        #print(dispData)

    #Function: Get mean of Param:

    def getmean(self, bs, hv, param):
        
        matches = [match for match in globals() if bs+'_'+hv+'_'+param in match]
        
        if globals()[matches[0]].shape == (): length = 1 #Einzelne Werte sind in den .npy files nicht als array gespeichert
                                                         #und haben deshalb eine Dimension geringer!!! 
        else: length = len(globals()[matches[0]])
        
        collect = np.empty(shape=[0, length])

        for m in matches:
            if globals()[m].shape == (): globals()[m] = np.array([globals()[m]])
                
            collect = np.append(collect, [globals()[m]], axis = 0)

        mean = np.mean(collect, axis=0)

        return(mean)


    #Function: Probability over Gamma 1TS

    def pguessogam(self, bs, hv):

        rcParams.update({'figure.autolayout': True})

        plt.rc('font', size=14)
        fig = plt.figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        plt.tight_layout()
        
        x_values = gamma
        y_values = self.getmean(bs, hv, 'pGuess')


        ax.plot(x_values, y_values, color='k', linestyle='-')
        
        plt.title(bs + "-" + hv)
        plt.xlabel(r'$\gamma$')
        plt.ylabel('Relative probability')

        plt.yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        #plt.savefig(TSID + '_Prob_o_Gamma')

        plt.show()

        print(self.getmean(bs, hv, 'eGuess'))
        #print(round(gamma[np.argmax(globals()[bs+"_"+hv+"_pGuess"])], 2))

#Function: Mean Performance: Proportion correct over Point separation (mm)

    def propcorosep(self, bs, hv, hline=None, spline=False, tozero=False):
        
        plt.rc('font', size=14)
        fig = plt.figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        
        x_values = globals()[self.TSIDs[0]+"_"+bs+"_"+hv+"_stimRange"]
        y_values = self.getmean(bs, hv, 'postmean')  
        y_std_lo = self.getmean(bs, hv, 'postmean')  - self.getmean(bs, hv, 'poststd')
        y_std_up = self.getmean(bs, hv, 'postmean')  + self.getmean(bs, hv, 'poststd')
            
        X_Y_spline = make_interp_spline(x_values, y_values)
        Y_STD_LO_spline = make_interp_spline(x_values, y_std_lo)
        Y_STD_UP_spline = make_interp_spline(x_values, y_std_up)
        
        if spline:
            
            X_ = np.linspace(x_values.min(), x_values.max(), 500)
            Y_ = X_Y_spline(X_)
            Y_STD_LO = Y_STD_LO_spline(X_)
            Y_STD_UP = Y_STD_UP_spline(X_)
            
            if tozero:
                X_ = np.linspace(0, x_values.max(), 500)
                Y_ = X_Y_spline(X_)
                Y_STD_LO = Y_STD_LO_spline(X_)
                Y_STD_UP = Y_STD_UP_spline(X_)
                
        else:
            X_ = x_values
            Y_ = y_values
            Y_STD_LO = y_std_lo
            Y_STD_UP = y_std_up
        
        ax.plot(X_, Y_, color='k', linestyle='-')
        plt.fill_between(X_, Y_STD_LO, Y_STD_UP, alpha=0.15, facecolor='k')

        plt.title("MEAN " + bs + "-" + hv)
        plt.xlabel('Point separation (mm)')
        plt.ylabel('Proportion correct')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.xticks(np.arange(0, 64, 10))
        plt.xlim(0, 64)
        plt.yticks(np.arange(0.5, 1.05, 0.1))
        plt.ylim(0.5, 1.05)
        plt.grid()
        
        if hline: plt.axhline(hline, color='k', linestyle='--')

        plt.show()

        return(X_Y_spline)

#Function: Compare Thresholds of two different Bodysites/Alignments:

    def thrshcompare(self, bs1, hv1, bs2, hv2, dop, values):
        
        plt.rc('font', size=14)
        fig = plt.figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        linestyles = [(0,()), 
                      (0, (10, 3)), 
                      (0, (3, 2, 1, 2)), 
                      (0, (4, 1, 1, 1, 1, 1)), 
                      (0, (5, 5)), 
                      (0, (5, 1))]
        
        x_values_1 = 9.5
        y_values_1 = np.empty(len(values))
        std1 = np.empty(len(values))
        
        x_values_2 = 29.5
        y_values_2 = np.empty(len(values))
        std2 = np.empty(len(values)) 
        
        stimRange1 = globals()[self.TSIDs[0]+"_"+bs1+"_"+hv1+"_stimRange"]
        stimRange2 = globals()[self.TSIDs[0]+"_"+bs2+"_"+hv2+"_stimRange"]


        if dop == "d":      
            plt.yticks(np.arange(0.4, 1.05, 0.1))
            plt.ylim(0.4, 1.05)
                
            spline_y_1 = make_interp_spline(stimRange1, self.getmean(bs1, hv1, 'postmean'))
            spline_y_2 = make_interp_spline(stimRange2, self.getmean(bs2, hv2, 'postmean'))

        if dop == "p":        
            plt.yticks(np.arange(0, 49, 10))
            plt.ylim(0, 49)
            
            spline_y_1 = make_interp_spline(self.getmean(bs1, hv1, 'postmean'), stimRange1)
            spline_y_2 = make_interp_spline(self.getmean(bs2, hv2, 'postmean'), stimRange2)

        
        i=0
        for v in values:
            y_values_1[i] = spline_y_1(v)
            y_values_2[i] = spline_y_2(v)
            
            i=i+1
        
        #Get STD at value
        
        for i in range(0, len(values)):
            
            if dop == "d":   
                index_std1 = int((np.abs(self.getmean(bs1, hv1, 'postmean') - y_values_1[i])).argmin())
                std1[i] = self.getmean(bs1, hv1, 'poststd')[index_std1]
                
                index_std2 = int((np.abs(self.getmean(bs2, hv2, 'postmean') - y_values_2[i])).argmin())
                std2[i] = self.getmean(bs2, hv2, 'poststd')[index_std2]

            if dop == "p":
                std1 = np.zeros(len(values))
                std2 = np.zeros(len(values))


            plt.errorbar(x_values_1+i%2, y_values_1[i], yerr=std1[i], 
                         fmt = 'o',  markersize=6, color = 'k', ecolor = 'k', elinewidth = 1, capsize=5)
            plt.errorbar(x_values_2+i%2, y_values_2[i], yerr=std2[i], 
                         fmt = 'o',  markersize=6, color = 'k', ecolor = 'k', elinewidth = 1, capsize=5)
            ax.plot([x_values_1+i%2, x_values_2+i%2],[y_values_1[i], y_values_2[i]], 
                    linestyle=(linestyles[i]), color = 'k', label = values[i])


        plt.title(bs1 + "-" + hv1 + " vs " + bs2 + "-" + hv2)
        #plt.xlabel('Orientation')
        plt.ylabel('Proportion correct')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks([10, 30], [hv1, hv2])
        plt.xlim(0, 40)
        plt.legend()

        plt.show()