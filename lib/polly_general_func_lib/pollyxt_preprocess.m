function data = pollyxt_preprocess(data, config)
%POLLYXT_PREPROCESS deadtime correction, background correction, first-bin shift,
%mask for low-SNR and mask for depolarization-calibration process.
%Usage:
%   data = pollyxt_preprocess(data, config)
%Inputs:
%   data: struct
%       rawSignal: array
%           signal. [Photon Count]
%       mShots: array
%           number of the laser shots for each profile.
%       mTime: array
%           datetime array for the measurement time of each profile.
%       depCalAng: array
%           angle of the polarizer in the receiving channel. (>0 means 
%           calibration process starts)
%       zenithAng: array
%           zenith angle of the laer beam.
%       repRate: float
%           laser pulse repetition rate. [s^-1]
%       hRes: float
%           spatial resolution [m]
%       mSite: string
%           measurement site.
%   config: struct
%       configuration. Detailed information can be found in doc/polly_config.md.
%Outputs:
%   data: struct
%       rawSignal: array
%           signal. [Photon Count]
%       mShots: array
%           number of the laser shots for each profile.
%       mTime: array
%           datetime array for the measurement time of each profile.
%       depCalAng: array
%           angle of the polarizer in the receiving channel. (>0 means 
%           calibration process starts)
%       zenithAng: array
%           zenith angle of the laer beam.
%       repRate: float
%           laser pulse repetition rate. [s^-1]
%       hRes: float
%           spatial resolution [m]
%       mSite: string
%           measurement site.
%       signal: array
%           Background removed signal
%       bg: array
%           background
%       height: array
%           height. [m]
%       lowSNRMask: array
%           If SNR less SNRmin, mask is set true. Otherwise, false
%       depCalMask: array
%           If polly was doing depolarization calibration, depCalMask is set
%           true. Otherwise, false.
%       fogMask: array
%           If it is foggy which means the signal will be very weak, 
%           fogMask will be set true. Otherwise, false
%History:
%   2018-12-16. First edition by Zhenping.
%   2019-07-10. Add mask for laser shutter due to approaching airplanes.
%   2019-08-27. Add mask for turnoff of PMT at 607 and 387nm.
%   2021-01-19. Add keyword of 'flagForceMeasTime' to align measurement time.
%   2021-01-20. Re-sample the profiles into temporal resolution of 30-s.
%Copyright:
%   Ground-based remote sensing (tropos)

global campaignInfo

if isempty(data.rawSignal)
    return;
end

% re-sample the temporal grid to 30 s (if it's not 30-s).
nInt = round(600 / nanmean(data.mShots(1, :), 2));   % number of integral profiles

if nInt > 1
    warning('MShots for single profile is not 600... Please check!!!');

    % if shots of single profile is less than 600

    nProf_int = floor(size(data.mShots, 2) / nInt);
    mShots_int = NaN(size(data.mShots, 1), nProf_int);
    mTime_int = NaN(1, nProf_int);
    rawSignal_int = NaN(size(data.rawSignal, 1), size(data.rawSignal, 2), nProf_int);
    depCalAng_int = NaN(nProf_int, 1);

    for iProf_int = 1:nProf_int
        profIndx = ((iProf_int - 1) * nInt + 1):(iProf_int * nInt);
        mShots_int(:, iProf_int) = nansum(data.mShots(:, profIndx), 2);
        mTime_int(iProf_int) = data.mTime(1) + datenum(0, 1, 0, 0, 0, double(600 / data.repRate * (iProf_int - 1)));
        rawSignal_int(:, :, iProf_int) = repmat(nansum(data.rawSignal(:, :, profIndx), 3), 1, 1, 1);
        if ~ isempty(data.depCalAng)
            depCalAng_int(iProf_int) = data.depCalAng(profIndx(1));
        end
    end

    data.rawSignal = rawSignal_int;
    data.mTime = mTime_int;
    data.mShots = mShots_int;
    data.depCalAng = depCalAng_int;
end

% re-locate measurement time forcefully.
if config.flagForceMeasTime
    data.mTime = data.filenameStartTime + ...
                 datenum(0, 1, 0, 0, 0, double(1:size(data.mTime, 2)) * 30);
end

if (max(config.max_height_bin + config.first_range_gate_indx - 1) > ...
   size(data.rawSignal, 2))
    warning(['%s_config.max_height_bin or %s_config.first_range_gate_indx ', ...
             'is out of range.\nTotal number of range bin is %d.\n', ...
             '%s_config.max_height_bin is %d\n', ...
             '%s_config.first_range_gate_indx is %s\n'], ...
             config.pollyVersion, ...
             size(data.rawSignal, 2), ...
             config.max_height_bin, ...
             config.first_range_gate_indx);
    fprintf(['Set the %s_config.max_height_bin and ', ...
             '%s_config.first_range_gate_indx to be default value.\n'], ...
             config.pollyVersion);
    config.max_height_bin = 251;
    config.first_range_gate_indx = ones(1, size(data.rawSignal, 1));
end

%% deadtime correction
rawSignal = data.rawSignal;
MShots = repmat(...
        reshape(data.mShots, size(data.mShots, 1), 1, size(data.mShots, 2)), ...
        [1, size(data.rawSignal, 2), 1]);

if config.flagDTCor
    PCR = data.rawSignal ./ MShots * 150.0 ./ data.hRes;   % [MHz]

    % polynomial correction with parameters saved in netcdf file
    if config.dtCorMode == 1
        for iChannel = 1:size(data.rawSignal, 1)
            PCR_Cor = polyval(data.deadtime(iChannel, end:-1:1), ...
                              PCR(iChannel, :, :));
            rawSignal(iChannel, :, :) = PCR_Cor / (150.0 / data.hRes) .* ...
                                        MShots(iChannel, :, :);
        end

    % nonparalyzable correction
    elseif config.dtCorMode == 2
        for iChannel = 1:size(data.rawSignal, 1)
            PCR_Cor = PCR(iChannel, :, :) ./ ...
                      (1.0 - config.dt(iChannel) * 1e-3 * PCR(iChannel, :, :));
            rawSignal(iChannel, :, :) = PCR_Cor / (150.0 / data.hRes) .* ...
                                        MShots(iChannel, :, :);
        end

    % user defined deadtime.
    % Regarding the format of dt, please go to /doc/polly_config.md
    elseif config.dtCorMode == 3
        if isfield(config, 'dt')
            for iChannel = 1:size(data.rawSignal, 1)
                PCR_Cor = polyval(config.dt(iChannel, end:-1:1), ...
                                  PCR(iChannel, :, :));
                rawSignal(iChannel, :, :) = PCR_Cor / (150.0 / data.hRes) .* ...
                    MShots(iChannel, :, :);
            end
        else
            warning(['User defined deadtime parameters were not found. ', ...
                     'Please go back to check the configuration ', ...
                     'file for the %s at %s.'], ...
                     campaignInfo.name, campaignInfo.location);
            warning(['In order to continue the current processing, ', ...
                     'deadtime correction will not be implemented. ', ...
                     'Be careful!']);
        end

    % No deadtime correction
    elseif config.dtCorMode == 4
        fprintf(['Deadtime correction was turned off. ', ...
                 'Be careful to check the signal strength.\n']);
    else
        error(['Unknow deadtime correction setting! ', ...
               'Please go back to check the configuration ', ...
               'file for %s at %s. For dtCorMode, only 1-4 is allowed.'], ...
               campaignInfo.name, campaignInfo.location);
    end
end

%% Background Substraction
bg = repmat(mean(...
    rawSignal(:, config.bgCorRangeIndx(1):config.bgCorRangeIndx(2), :), 2), ...
    [1, config.max_height_bin, 1]);
data.signal = NaN(size(rawSignal, 1), ...
                  config.max_height_bin, size(rawSignal, 3));
for iChannel = 1:size(rawSignal, 1)
    data.signal(iChannel, :, :) = rawSignal(...
        iChannel, ...
        config.first_range_gate_indx(iChannel):(config.max_height_bin + config.first_range_gate_indx(iChannel) - 1), :) - bg(iChannel, :, :);
end
data.bg = bg;

%% height (first bin height correction)
data.height = double((0:(size(data.signal, 2)-1)) * data.hRes * ...
    cos(data.zenithAng / 180 * pi) + config.first_range_gate_height);   % [m]
data.alt = double(data.height + campaignInfo.asl);   % geopotential height
% distance between range bin and system.
data.distance0 = double(data.height ./ cos(data.zenithAng / 180 * pi));

%% mask for low SNR region
SNR = polly_SNR(data.signal, data.bg);
data.lowSNRMask = false(size(data.signal));
for iChannel = 1: size(data.signal, 1)
    data.lowSNRMask(iChannel, SNR(iChannel, :, :) < ...
                    config.mask_SNRmin(iChannel)) = true;
end

%% depol cal time and mask
maskDepCalAng = config.maskDepCalAng;   % mask for postive and negative
                                        % calibration angle. 'none' means
                                        % invalid profiles with different
                                        % depol_cal_angle
[data.depol_cal_ang_p_time_start, data.depol_cal_ang_p_time_end, ...
 data.depol_cal_ang_n_time_start, data.depol_cal_ang_n_time_end, ...
 depCalMask] = polly_depolCal_time(data.depCalAng, data.mTime, ...
                                   config.init_depAng, maskDepCalAng);
data.depCalMask = transpose(depCalMask);

%% mask for laser shutter
flagChannel532FR = config.isFR & config.is532nm & config.isTot;
flagChannel355FR = config.isFR & config.is355nm & config.isTot;
if any(flagChannel532FR)
    flagChannel4Shutter = flagChannel532FR;
    data.shutterOnMask = polly_isLaserShutterOn(...
        squeeze(data.signal(flagChannel4Shutter, :, :)));
elseif any(flagChannel355FR)
    flagChannel4Shutter = flagChannel355FR;
    data.shutterOnMask = polly_isLaserShutterOn(...
        squeeze(data.signal(flagChannel4Shutter, :, :)));
else
    warning('No suitable channel to determine the shutter status');
    data.shutterOnMask = false(size(data.mTime));
end

%% mask for fog profiles
data.fogMask = false(1, size(data.signal, 3));
is_channel_532_FR_Tot = config.isFR & config.is532nm & config.isTot;
data.fogMask(transpose(squeeze(sum(data.signal(is_channel_532_FR_Tot, 40:120, :), 2)) <= config.minPC_fog) & (~ data.shutterOnMask)) = true;

%% mask for PMT607 off
flagChannel607 = config.isFR & config.is607nm;
data.mask607Off = polly_is607Off(squeeze(data.signal(flagChannel607, :, :)));

%% mask for PMT1058 off
flagChannel1058 = config.isFR & config.is1058nm;
data.mask1058Off = polly_is607Off(squeeze(data.signal(flagChannel1058, :, :)));

%% mask for PMT387 off
flagChannel387 = config.isFR & config.is387nm;
data.mask387Off = polly_is387Off(squeeze(data.signal(flagChannel387, :, :)));

%% mask for PMT407 off
flagChannel407 = config.isFR & config.is407nm;
data.mask407Off = polly_is407Off(squeeze(data.signal(flagChannel407, :, :)));

end
