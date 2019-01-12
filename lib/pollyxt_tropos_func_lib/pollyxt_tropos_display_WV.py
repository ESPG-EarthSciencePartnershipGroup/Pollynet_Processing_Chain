import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.dates import DateFormatter, DayLocator, HourLocator, MinuteLocator, date2num
from matplotlib import use
use('Agg')
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

def pollyxt_tropos_display_WV(tmpFile, saveFolder):
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
    pollyxt_tropos_display_WV(tmpFile)

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
        WVMR = mat['WVMR'][:]
        RH = mat['RH'][:]
        lowSNRMask = mat['lowSNRMask'][:]
        height = mat['height'][0][:]
        time = mat['time'][0][:]
        flagCalibrated = mat['flagCalibrated'][:][0]
        pollyVersion = mat['taskInfo']['pollyVersion'][0][0][0]
        location = mat['campaignInfo']['location'][0][0][0]
        version = mat['processInfo']['programVersion'][0][0][0]
        dataFilename = mat['taskInfo']['dataFilename'][0][0][0]
        xtick = mat['xtick'][0][:]
        xticklabel = mat['xtickstr']
    except Exception as e:
        print('%s has been destroyed' % (tmpFile))
        return

    # meshgrid
    Time, Height = np.meshgrid(time, height)
    WVMR = np.ma.masked_where(lowSNRMask != 0, WVMR)
    RH = np.ma.masked_where(lowSNRMask != 0, RH)

    # define the colormap
    cmap = plt.cm.jet
    cmap.set_bad('w', alpha=1)
    cmap.set_over('w', alpha=1)
    cmap.set_under('k', alpha=1)

    # display WVMR
    fig = plt.figure(figsize=[10, 5])
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.75])
    pcmesh = ax.pcolormesh(Time, Height, WVMR, vmin=0, vmax=10, cmap=cmap)
    ax.set_xlabel('UTC', fontweight='semibold', fontsize=14)
    ax.set_ylabel('Height (m)', fontweight='semibold', fontsize=14)

    ax.set_yticks(np.arange(0, 8001, 1000).tolist())
    ax.set_ylim([0, 8000])
    ax.set_xticks(xtick.tolist())
    ax.set_xticklabels(celltolist(xticklabel))

    ax.set_title('Water vapor mixing ratio from {instrument} at {location}'.format(instrument=pollyVersion, location=location))

    cb_ax = fig.add_axes([0.92, 0.15, 0.02, 0.75])
    cbar = fig.colorbar(pcmesh, cax=cb_ax, ticks=np.arange(0, 10.1, 2), orientation='vertical')
    cbar.ax.tick_params(direction='in', labelsize=10, pad=5)
    cbar.ax.set_title('[$g*kg^{-1}$]', fontsize=8)

    fig.text(0.05, 0.04, datenum_to_datetime(time[0]).strftime("%Y-%m-%d"), fontsize=12)
    fig.text(0.8, 0.02, 'Version: {version}\nCalibration: {status}'.format(version=version, status=flagCalibrated), fontsize=12)

    plt.tight_layout()
    fig.savefig(os.path.join(saveFolder, '{dataFilename}_WVMR.png'.format(dataFilename=rmext(dataFilename))), dpi=150)
    plt.close()

    # display RH
    fig = plt.figure(figsize=[10, 5])
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.75])
    pcmesh = ax.pcolormesh(Time, Height, RH, vmin=0, vmax=100, cmap=cmap)
    ax.set_xlabel('UTC', fontweight='semibold', fontsize=14)
    ax.set_ylabel('Height (m)', fontweight='semibold', fontsize=14)

    ax.set_yticks(np.arange(0, 8001, 1000).tolist())
    ax.set_ylim([0, 8000])
    ax.set_xticks(xtick.tolist())
    ax.set_xticklabels(celltolist(xticklabel))

    ax.set_title('Relative humidity from {instrument} at {location}'.format(instrument=pollyVersion, location=location))

    cb_ax = fig.add_axes([0.92, 0.15, 0.02, 0.75])
    cbar = fig.colorbar(pcmesh, cax=cb_ax, ticks=np.arange(0, 100.1, 20), orientation='vertical')
    cbar.ax.tick_params(direction='in', labelsize=10, pad=5)
    cbar.ax.set_title('[$\%$]', fontsize=8)

    fig.text(0.05, 0.04, datenum_to_datetime(time[0]).strftime("%Y-%m-%d"), fontsize=12)
    fig.text(0.8, 0.02, 'Version: {version}\nCalibration: {status}'.format(version=version, status=flagCalibrated), fontsize=12)

    plt.tight_layout()
    fig.savefig(os.path.join(saveFolder, '{dataFilename}_RH.png'.format(dataFilename=rmext(dataFilename))), dpi=150)
    plt.close()

def main():
    pollyxt_tropos_display_WV('C:\\Users\\zhenping\\Desktop\\Picasso\\tmp\\tmp.mat', 'C:\\Users\\zhenping\\Desktop\\Picasso\\recent_plots\\POLLYXT_TROPOS\\20180517')

if __name__ == '__main__':
    # main()
    pollyxt_tropos_display_WV(sys.argv[1], sys.argv[2])