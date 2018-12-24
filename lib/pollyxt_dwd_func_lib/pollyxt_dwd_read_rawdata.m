function [ data ] = polly_read_rawdata(file, config)
%polly_read_rawdata read polly data.
%   Usage:
%       data = polly_read_rawdata(file, config)
%   Inputs:
%       file: char
%           fullpath of polly data file.
%       config: struct
%           configuration. Detailed information can be found in doc/polly_config.md.
%   Outputs:
%       data: struct
%           rawSignal: array
%               signal. [Photon Count]
%           mShots: array
%               number of the laser shots for each profile.
%           mTime: array
%               datetime array for the measurement time of each profile.
%           depCalAng: array
%               angle of the polarizer in the receiving channel. (>0 means 
%               calibration process starts)
%           zenithAng: array
%               zenith angle of the laer beam.
%           hRes: float
%               spatial resolution [m]
%           mSite: char
%               measurement site.
%   History:
%       2018-12-16. First edition by Zhenping.
%   Copyright:
%       Ground-based remote sensing (TROPOS)

%% variables initialization
data = struct();
data.rawSignal = [];
data.mShots = [];
data.mTime = [];
data.depCalAng = [];
data.hRes = [];
data.zenithAng = [];
data.mSite = [];
data.deadtime = [];

if ~ exist(file, 'file')
    warning('polly data file does not exist.\n%s\n', file);
    return;
end

%% read data
try
    rawSignal = ncread(file, 'raw_signal');
    deadtime = ncread(file, 'deadtime_polynomial');
    mShots = ncread(file, 'measurement_shots');
    mTime = ncread(file, 'measurement_time');
    depCalAng = ncread(file, 'depol_cal_angle');
    hRes = ncread(file, 'measurement_height_resolution') * 0.15; % Unit: m
    zenithAng = ncread(file, 'zenithangle'); % Unit: deg
    fileInfo = ncinfo(file);
    mSite = fileInfo.Attributes(1, 1).Value;
catch
    warning('Failure in read polly data file.\n%s\n', file);
    return;
end

% filter non 30s profiles
if config.flagFilterFalseMShots
    indx = find(mShots > 500);
    if isempty(indx)
        fprintf('No profile with mshots > 500 is found.\nPlease take a look inside %s\n', file);
        return;
    else
        rawSignal = rawSignal(:, :, indx);
        deadtime = deadtime;
        mShots = mShots(indx);
        mTime = mTime(indx);
        depCalAng = depCalAng(indx);
        hRes = hRes;
        zenithAng = zenithAng;
        mSite = mSite;
    end
elseif config.flagCorrectFalseMShots
    mShots = ones(size(mShots)) * 600;
end

data.zenithAng = zenithAng;
data.hRes = hRes;
data.mSite = mSite;
data.mTime = datenum(mTime(1, :), 'yyyymmdd') + datenum(0, 1, 0, 0, 0, double(mTime(2, :)));
data.mShots = mShots;
data.depCalAng = depCalAng;
data.rawSignal = rawSignal;
data.deadtime = deadtime;

end