import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.dates import DateFormatter, DayLocator, HourLocator, MinuteLocator, date2num
import os, sys
import scipy.io as spio
import numpy as np
from datetime import datetime, timedelta

def celltolist(xtickstr):
    tmp = []
    for iElement in range(0, len(xtickstr)):
        if not len(xtickstr[iElement][0]):
            tmp.append('')
        else:
            tmp.append(xtickstr[iElement][0][0])

    return tmp

def datenum_to_datetime(datenum):
    """
    Convert Matlab datenum into Python datetime.
    :param datenum: Date in datenum format
    :return:        Datetime object corresponding to datenum.
    """
    days = datenum % 1
    hours = days % 1 * 24
    minutes = hours % 1 * 60
    seconds = minutes % 1 * 60
    return datetime.fromordinal(int(datenum)) \
           + timedelta(days=int(days)) \
           + timedelta(hours=int(hours)) \
           + timedelta(minutes=int(minutes)) \
           + timedelta(seconds=round(seconds)) \
           - timedelta(days=366)

def rmext(filename):
    file, _ = os.path.splitext(filename)
    return file

def pollyxt_dwd_display_longterm_cali(tmpFile, saveFolder):
    '''
    Description
    -----------
    Display the housekeeping data from laserlogbook file.

    Parameters
    ----------
    - tmpFile: the .mat file which stores the housekeeping data.

    Return
    ------ 

    Usage
    -----
    pollyxt_dwd_display_longterm_cali(tmpFile)

    History
    -------
    2019-01-10. First edition by Zhenping

    Copyright
    ---------
    Ground-based Remote Sensing (TROPOS)
    '''

    if not os.path.exists(tmpFile):
        print('{filename} does not exists.'.format(filename=tmpFile))
        return
    
    # read data
    try:
        mat = spio.loadmat(tmpFile, struct_as_record=True)
        figDPI = mat['figDPI'][0][0]
        thisLCTime = mat['LCTime'][0][:]
        LC355Status = mat['LC355Status'][:]
        LC532Status = mat['LC532Status'][:]
        LC1064Status = mat['LC1064Status'][:]
        LC387Status = mat['LC387Status'][:]
        LC607Status = mat['LC607Status'][:]
        LC355History = mat['LC355History'][:]
        LC532History = mat['LC532History'][:]
        LC1064History = mat['LC1064History'][:]
        LC387History = mat['LC387History'][:]
        LC607History = mat['LC607History'][:]
        thisLogbookTime = mat['logbookTime'][0][:]
        flagOverlap = mat['flagOverlap'][0][:]
        flagWindowwipe = mat['flagWindowwipe'][0][:]
        flagFlashlamps = mat['flagFlashlamps'][0][:]
        flagPulsepower = mat['flagPulsepower'][0][:]
        flagRestart = mat['flagRestart'][0][:]
        flag_CH_NDChange = mat['flag_CH_NDChange'][:]
        flagCH355FR = mat['flagCH355FR'][0][:]
        flagCH532FR = mat['flagCH532FR'][0][:]
        flagCH1064FR = mat['flagCH1064FR'][0][:]
        flagCH387FR = mat['flagCH387FR'][0][:]
        flagCH607FR = mat['flagCH607FR'][0][:]
        flagCH532FR_X = mat['flagCH532FR_X'][0][:]
        else_time = mat['else_time'][:]
        else_label = mat['else_label']
        thisDepolCaliTime532 = mat['depolCaliTime532'][0][:]
        depolCaliConst532 = mat['depolCaliConst532'][0][:]
        yLim355 = mat['yLim355'][0][:]
        yLim532 = mat['yLim532'][0][:]
        yLim1064 = mat['yLim1064'][0][:]
        depolConstLim532 = mat['depolConstLim532'][0][:]
        pollyVersion = mat['campaignInfo']['name'][0][0][0]
        dataTime = mat['taskInfo']['dataTime'][0][0][0]
        location = mat['campaignInfo']['location'][0][0][0]
        startTime = mat['campaignInfo']['startTime'][0][0][0]
        version = mat['processInfo']['programVersion'][0][0][0]
    except Exception as e:
        print('%s has been destroyed' % (tmpFile))
        return

    # convert matlab datenum tp datetime 
    startTime = datenum_to_datetime(float(startTime[0]))
    dataTime = datenum_to_datetime(float(dataTime[0]))
    LCTime = [datenum_to_datetime(thisTime) for thisTime in thisLCTime]
    logbookTime = [datenum_to_datetime(thisTime) for thisTime in thisLogbookTime]
    elseTime = [datenum_to_datetime(thisElseTime) for thisElseTime in else_time]
    depolCaliTime532 = [datenum_to_datetime(thisTime) for thisTime in thisDepolCaliTime532]

    lineColor = {'overlap': '#f48f42', 'windowwipe': '#ff66ff', 'flashlamps': '#993333', 'pulsepower': '#990099', 'restart': '#ffff00', 'NDChange': '#333300', 'else': '#00ff00'}

    # display lidar constants at 355mn
    fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, figsize=(8,18), sharex=True, gridspec_kw={'height_ratios': [1, 1, 1, 1, 1, 1], 'hspace': 0.1})
    plt.subplots_adjust(top=0.96, bottom=0.05, left=0.07, right=0.98)

    # lidar constants at 355 nm
    p1 = ax1.scatter([LCTime[indx] for indx in np.arange(0, len(LCTime)) if LC355Status[indx] == 2], LC355History[LC355Status == 2], s=7, c='#0000ff', marker='o', label='lidar constant')
    # default line for create legend
    l1 = ax1.axvline(x=0, linestyle='--', color=lineColor['overlap'], label='overlap')
    l2 = ax1.axvline(x=0, linestyle='--', color=lineColor['pulsepower'], label='pulsepower')
    l3 = ax1.axvline(x=0, linestyle='--', color=lineColor['windowwipe'], label='windowwipe')
    l4 = ax1.axvline(x=0, linestyle='--', color=lineColor['restart'], label='restart')
    l5 = ax1.axvline(x=0, linestyle='--', color=lineColor['flashlamps'], label='flashlamps')
    l6 = ax1.axvline(x=0, linestyle='--', color=lineColor['NDChange'], label='NDChange')
    l7 = ax1.axvline(x=0, linestyle='--', color=lineColor['else'], label=else_label[0])

    l = ax1.legend(handles=[p1, l1, l2, l3, l4, l5, l6, l7], loc='upper left', fontsize=11)

    for iLogbookInfo in np.arange(0, len(logbookTime)):
        if flagOverlap[iLogbookInfo]:
            ax1.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['overlap'])
        if flagPulsepower[iLogbookInfo]:
            ax1.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['pulsepower'])
        if flagWindowwipe[iLogbookInfo]:
            ax1.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['windowwipe'])
        if flagRestart[iLogbookInfo]:
            ax1.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['restart'])
        if flagFlashlamps[iLogbookInfo]:
            ax1.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['flashlamps'])
        if flag_CH_NDChange[iLogbookInfo, flagCH355FR == 1]:
            ax1.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['NDChange'])

    for elseTime in else_time:
        ax1.axvline(x=elseTime, linestyle='--', color=lineColor['else'])        
    
    ax1.set_ylabel('LC @ 355nm')
    ax1.grid(False)
    ax1.set_title('Lidar constants for {instrument} at {location}'.format(instrument=pollyVersion, location=location), fontweight='bold', fontsize=12)
    ax1.set_ylim(yLim355.tolist())
    ax1.set_xlim([startTime - timedelta(days=2), dataTime + timedelta(days=2)])

    # lidar constant at 532 nm
    p1 = ax2.scatter([LCTime[indx] for indx in np.arange(0, len(LCTime)) if LC532Status[indx] == 2], LC532History[LC532Status == 2], s=7, c='#0000ff', marker='o')

    for iLogbookInfo in np.arange(0, len(logbookTime)):
        if flagOverlap[iLogbookInfo]:
            ax2.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['overlap'])
        if flagPulsepower[iLogbookInfo]:
            ax2.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['pulsepower'])
        if flagWindowwipe[iLogbookInfo]:
            ax2.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['windowwipe'])
        if flagRestart[iLogbookInfo]:
            ax2.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['restart'])
        if flagFlashlamps[iLogbookInfo]:
            ax2.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['flashlamps'])
        if flag_CH_NDChange[iLogbookInfo, flagCH532FR == 1]:
            ax2.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['NDChange'])
 
    for elseTime in else_time:
        ax2.axvline(x=elseTime, linestyle='--', color=lineColor['else'])      

    ax2.set_ylabel('LC @ 532nm')
    ax2.grid(False)
    ax2.set_ylim(yLim532.tolist())
    ax2.set_xlim([startTime - timedelta(days=2), dataTime + timedelta(days=2)])

    # lidar constant at 1064 nm
    p1 = ax3.scatter([LCTime[indx] for indx in np.arange(0, len(LCTime)) if LC1064Status[indx] == 2], LC1064History[LC1064Status == 2], s=7, c='#0000ff', marker='o')

    for iLogbookInfo in np.arange(0, len(logbookTime)):
        if flagOverlap[iLogbookInfo]:
            ax3.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['overlap'])
        if flagPulsepower[iLogbookInfo]:
            ax3.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['pulsepower'])
        if flagWindowwipe[iLogbookInfo]:
            ax3.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['windowwipe'])
        if flagRestart[iLogbookInfo]:
            ax3.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['restart'])
        if flagFlashlamps[iLogbookInfo]:
            ax3.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['flashlamps'])
        if flag_CH_NDChange[iLogbookInfo, flagCH1064FR == 1]:
            ax3.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['NDChange'])
 
    for elseTime in else_time:
        ax3.axvline(x=elseTime, linestyle='--', color=lineColor['else'])      

    ax3.set_ylabel('LC @ 1064nm')
    ax3.grid(False)
    ax3.set_ylim(yLim1064.tolist())
    ax3.set_xlim([startTime - timedelta(days=2), dataTime + timedelta(days=2)])

    # transmission ratio at 355/387 nm
    flagRamanLC = np.logical_and(LC355Status == 2, LC387Status == 2)
    p1 = ax4.scatter([LCTime[indx] for indx in np.arange(0, len(LCTime)) if flagRamanLC[indx]], LC355History[flagRamanLC] / LC387History[flagRamanLC] / 1.436, s=7, c='#0000ff', marker='o')

    for iLogbookInfo in np.arange(0, len(logbookTime)):
        if flagOverlap[iLogbookInfo]:
            ax4.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['overlap'])
        if flagPulsepower[iLogbookInfo]:
            ax4.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['pulsepower'])
        if flagWindowwipe[iLogbookInfo]:
            ax4.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['windowwipe'])
        if flagRestart[iLogbookInfo]:
            ax4.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['restart'])
        if flagFlashlamps[iLogbookInfo]:
            ax4.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['flashlamps'])
        if flag_CH_NDChange[iLogbookInfo, flagCH355FR == 1] or flag_CH_NDChange[iLogbookInfo, flagCH387FR == 1]:
            ax4.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['NDChange'])
   
    for elseTime in else_time:
        ax4.axvline(x=elseTime, linestyle='--', color=lineColor['else'])      

    ax4.set_ylabel('Ratio 355/387')
    ax4.grid(False)
    ax4.set_ylim([0, 1])
    ax4.set_xlim([startTime - timedelta(days=2), dataTime + timedelta(days=2)])

    # transmission ratio at 532/607 nm
    flagRamanLC = np.logical_and(LC532Status == 2, LC607Status == 2)
    p1 = ax5.scatter([LCTime[indx] for indx in np.arange(0, len(LCTime)) if flagRamanLC[indx]], LC532History[flagRamanLC] / LC607History[flagRamanLC] / 1.436, s=7, c='#0000ff', marker='o')

    for iLogbookInfo in np.arange(0, len(logbookTime)):
        if flagOverlap[iLogbookInfo]:
            ax5.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['overlap'])
        if flagPulsepower[iLogbookInfo]:
            ax5.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['pulsepower'])
        if flagWindowwipe[iLogbookInfo]:
            ax5.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['windowwipe'])
        if flagRestart[iLogbookInfo]:
            ax5.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['restart'])
        if flagFlashlamps[iLogbookInfo]:
            ax5.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['flashlamps'])
        if flag_CH_NDChange[iLogbookInfo, flagCH532FR == 1] or flag_CH_NDChange[iLogbookInfo, flagCH607FR == 1]:
            ax5.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['NDChange'])

    for elseTime in else_time:
        ax5.axvline(x=elseTime, linestyle='--', color=lineColor['else'])      

    ax5.set_ylabel('Ratio 532/607')
    ax5.grid(False)
    ax5.set_ylim([0, 1])
    ax5.set_xlim([startTime - timedelta(days=2), dataTime + timedelta(days=2)])
    
    # depolarization calibration constant at 532 nm
    p1 = ax6.scatter(depolCaliTime532, depolCaliConst532, s=7, c='#0000ff', marker='o')

    for iLogbookInfo in np.arange(0, len(logbookTime)):
        if flagOverlap[iLogbookInfo]:
            ax6.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['overlap'])
        if flagPulsepower[iLogbookInfo]:
            ax6.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['pulsepower'])
        if flagWindowwipe[iLogbookInfo]:
            ax6.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['windowwipe'])
        if flagRestart[iLogbookInfo]:
            ax6.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['restart'])
        if flagFlashlamps[iLogbookInfo]:
            ax6.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['flashlamps'])
        if flag_CH_NDChange[iLogbookInfo, flagCH532FR == 1] or flag_CH_NDChange[iLogbookInfo, flagCH532FR_X == 1]:
            ax6.axvline(x=logbookTime[iLogbookInfo], linestyle='--', color=lineColor['NDChange'])
   
    for elseTime in else_time:
        ax6.axvline(x=elseTime, linestyle='--', color=lineColor['else'])      

    ax6.set_ylabel('V* 532')
    ax6.set_xlabel('Date (mm-dd)')
    ax6.set_ylim(depolConstLim532.tolist())
    ax6.xaxis.set_major_formatter(DateFormatter('%m-%d'))
    ax6.grid(False)
    ax6.set_xlim([startTime - timedelta(days=2), dataTime + timedelta(days=2)])
    fig.text(0.03, 0.03, startTime.strftime("%Y"), fontsize=12)
    fig.text(0.90, 0.03, 'Version: {version}'.format(version=version), fontsize=12)

    fig.savefig(os.path.join(saveFolder, '{dataFilename}_long_term_cali_results.png'.format(dataFilename=dataTime.strftime('%Y%m%d'))), dpi=figDPI)
    plt.close()

def main():
    pollyxt_dwd_display_longterm_cali('C:\\Users\\zhenping\\Desktop\\Picasso\\tmp\\tmp.mat', 'C:\\Users\\zhenping\\Desktop\\Picasso\\recent_plots\\pollyxt_dwd\\20181214')

if __name__ == '__main__':
    # main()
    pollyxt_dwd_display_longterm_cali(sys.argv[1], sys.argv[2])