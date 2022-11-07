import os
import re
import glob
import math
import PsiMarginal_fd
import datetime
import time
import shutil
import numpy             as np



def mergedata(TSIDs, file_path_data, bs, hv, TEMP=True):

    #Allocate Data in Variables:

    for TSID in TSIDs:
        fpTS = os.path.join(file_path_data, TSID)

        for file in os.listdir(fpTS):
            if os.path.splitext(file)[1] == '.npy':
                x = re.split("_", file)
                if "user" in x:
                    del x[x.index("user")]
                globals()[x[0] + "_" + x[1] + "_" + x[2] + "_" + x[3]] = np.load(os.path.join(fpTS, file), allow_pickle=True)

    
    #Load in data:

    if TEMP == False:
        FID = input('add file ID:')
    else:
        FID = "TEMP"

    stim = np.array([])
    resp = np.array([])

    for TSID in TSIDs:
        stim = np.append(stim, globals()[TSID+'_'+bs+'_'+hv+'_stim'])
        resp = np.append(resp, globals()[TSID+'_'+bs+'_'+hv+'_response'])

    #Set Psi Parameters:

    ntrials = len(stim)  # number of trials
    a = np.linspace(0.01, 60, 31)  # threshold/bias grid
    b = np.linspace(0.01, 10, 50)  # slope grid
    x = globals()[TSID+'_'+bs+'_'+hv+'_stimRange']  # possible stimuli to use
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

    file_path_TEMP = os.path.join('DATA_m', FID)

    #check for directory with FID
    if not os.path.isdir(file_path_TEMP):
        os.mkdir(file_path_TEMP)
        print("\nnew directory " + FID + " created")

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

def cleanup(file_path_TEMP, FID):
    shutil.rmtree(os.path.join(file_path_TEMP, FID[0]))
