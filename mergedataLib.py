import os
import re
import glob
import math
import PsiMarginal_fd
import datetime
import time
import shutil
import numpy             as np



def mergedata(TSIDs, file_path_data, bs, hv, FID=None):

    #Allocate Data in Variables:
    TSIDs_all = TSIDs

    for TSID in TSIDs_all:
        fpTS = os.path.join(file_path_data, TSID)

        for file in os.listdir(fpTS):
            if os.path.splitext(file)[1] == '.npy':
                x = re.split("_", file)
                if "user" in x:
                    del x[x.index("user")]
                globals()[x[0] + "_" + x[1] + "_" + x[2] + "_" + x[3]] = np.load(os.path.join(fpTS, file), encoding='latin1',  allow_pickle=True)

    #Filter out existing TSID files with given bs and hv
    TSIDs = [re.split("_", match)[0] for match in globals() if bs+'_'+hv in match]
    TSIDs = [*set(TSIDs)]
    print(TSIDs)

    #Load in data:

    stim = np.array([])
    resp = np.array([])

    if hv == 'h' or hv == 'v':
        for TSID in TSIDs:
            try:
                stim = np.append(stim, globals()[TSID+'_'+bs+'_'+hv+'_stim'])
                resp = np.append(resp, globals()[TSID+'_'+bs+'_'+hv+'_response'])
            except: pass
    if hv == 'hv':
        for TSID in TSIDs:
            stim = np.append(stim, globals()[TSID+'_'+bs+'_h_stim'])
            stim = np.append(stim, globals()[TSID+'_'+bs+'_v_stim'])
            resp = np.append(resp, globals()[TSID+'_'+bs+'_h_response'])
            resp = np.append(resp, globals()[TSID+'_'+bs+'_v_response'])

    #Set Psi Parameters:

    ntrials = len(stim)  # number of trials
    a = np.linspace(0.01, 60, 31)  # threshold/bias grid
    b = np.linspace(0.01, 10, 50)  # slope grid
    if hv == 'hv': x = globals()[TSID+'_'+bs+'_'+'h'+'_stimRange']
    else: x = globals()[TSID+'_'+bs+'_'+hv+'_stimRange']  # possible stimuli to use
    delta = 0.02  # lapse
    gamma = np.linspace(0.01, 0.99, 100) # guess


    INIT_X = stim[0]

    # initialize algorithm
    psi = PsiMarginal_fd.Psi(x, Pfunction='Weibull', nTrials=ntrials, threshold=a, slope=b, guessRate=gamma,
                          lapseRate=delta, marginalize=False, init_x=INIT_X)


    for i in range(0, ntrials):  # run for length of trials
        print ('\rTrial %d of %d' % (i+1, ntrials), end='')

        data_r = resp[i]
        if i<len(stim)-1: data_x = stim[i+1]
        psi.addData(data_r, data_x)  # update Psi with response
        while psi.xCurrent == None:  # wait until next stimuli is calculated
            pass

    psi.plot()

    if not FID:
        FID = 'TEMP'

    file_path_TEMP = os.path.join('DATA_m', FID)

    if os.path.isdir(file_path_TEMP):
        shutil.rmtree(file_path_TEMP)


    os.mkdir(file_path_TEMP)
    print("\nnew directory " + FID + " created")

#    num = 0
#    i = 0
#    n = 0

#    for file in os.listdir(file_path_TEMP):
#        if FID in os.path.splitext(file)[0]:
#            n = 1
#            x = re.split("_", file)
#            if re.search('^[0-9]+$', x[0][-1]):
#                if num <= int(x[0][-1]): num = int(x[0][-1])+1
#                i = 1

#    if n and not i:
#        num = 2

#    if num: FID = FID+str(num)


    #Safe 
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M')
    file_name_data = FID +"_"+ bs + "_" + hv +"_data_"+ timestamp +".npy"

    file_name_stim = FID +"_"+ bs + "_" + hv +"_stim_"+ timestamp +".npy"
    file_name_response = FID +"_"+ bs + "_" + hv +"_response_"+ timestamp +".npy"
    file_name_postmean = FID +"_"+ bs + "_" + hv +"_postmean_"+ timestamp +".npy"
    file_name_poststd = FID +"_"+ bs + "_" + hv +"_poststd_"+ timestamp +".npy"
    file_name_stimRange = FID +"_"+ bs + "_" + hv +"_stimRange_"+ timestamp +".npy"

    file_name_pThreshold = FID +"_"+ bs + "_" + hv +"_pThreshold_"+ timestamp +".npy"
    file_name_pSlope = FID +"_"+ bs + "_" + hv +"_pSlope_"+ timestamp +".npy"
    file_name_pLapse = FID +"_"+ bs + "_" + hv +"_pLapse_"+ timestamp +".npy"
    file_name_pGuess = FID +"_"+ bs + "_" + hv +"_pGuess_"+ timestamp +".npy"
    file_name_eThreshold = FID +"_"+ bs + "_" + hv +"_eThreshold_"+ timestamp +".npy"
    file_name_eSlope = FID +"_"+ bs + "_" + hv +"_eSlope_"+ timestamp +".npy"
    file_name_eLapse = FID +"_"+ bs + "_" + hv +"_eLapse_"+ timestamp +".npy"
    file_name_eGuess = FID +"_"+ bs + "_" + hv +"_eGuess_"+ timestamp +".npy"
    file_name_stdThreshold = FID +"_"+ bs + "_" + hv +"_stdThreshold_"+ timestamp +".npy"
    file_name_stdSlope = FID +"_"+ bs + "_" + hv +"_stdSlope_"+ timestamp +".npy"
    file_name_stdLapse = FID +"_"+ bs + "_" + hv +"_stdLapse_"+ timestamp +".npy"
    file_name_stdGuess = FID +"_"+ bs + "_" + hv +"_stdGuess_"+ timestamp +".npy"

    np.save(os.path.join(file_path_TEMP, file_name_stim), psi.stim)
    np.save(os.path.join(file_path_TEMP, file_name_response), psi.response)
    np.save(os.path.join(file_path_TEMP, file_name_postmean), psi.postmean)
    np.save(os.path.join(file_path_TEMP, file_name_poststd), psi.poststd)
    np.save(os.path.join(file_path_TEMP, file_name_stimRange), psi.stimRange)
        
    np.save(os.path.join(file_path_TEMP, file_name_pThreshold), psi.pThreshold)
    np.save(os.path.join(file_path_TEMP, file_name_pSlope), psi.pSlope)
    np.save(os.path.join(file_path_TEMP, file_name_pLapse), psi.pLapse)
    np.save(os.path.join(file_path_TEMP, file_name_pGuess), psi.pGuess)
    np.save(os.path.join(file_path_TEMP, file_name_eThreshold), psi.eThreshold)
    np.save(os.path.join(file_path_TEMP, file_name_eSlope), psi.eSlope)
    np.save(os.path.join(file_path_TEMP, file_name_eLapse), psi.eLapse)
    np.save(os.path.join(file_path_TEMP, file_name_eGuess), psi.eGuess)
    np.save(os.path.join(file_path_TEMP, file_name_stdThreshold), psi.stdThreshold)
    np.save(os.path.join(file_path_TEMP, file_name_stdSlope), psi.stdSlope)
    np.save(os.path.join(file_path_TEMP, file_name_stdLapse), psi.stdLapse)
    np.save(os.path.join(file_path_TEMP, file_name_stdGuess), psi.stdGuess)

    return ([FID], 'DATA_m')