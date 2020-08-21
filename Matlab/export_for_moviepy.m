function export_struct = export_for_moviepy(U, cell_num)

%% export structure whisker variables 
export_struct.cell_number = cell_num;
touchOn = [find(U{cell_num}.S_ctk(9,:,:)==1)  ;find(U{cell_num}.S_ctk(12,:,:)==1)];
touchOff = [find(U{cell_num}.S_ctk(10,:,:)==1)  ;find(U{cell_num}.S_ctk(13,:,:)==1)];
export_struct.touch_matrix = nan(size(U{cell_num}.R_ntk));
for g = 1:length(touchOn)
    export_struct.touch_matrix(touchOn(g):touchOff(g)) = 1;
end

variable_names = U{cell_num}.varNames;

selected_variables = [1,3:5];
for k = 1:length(selected_variables)
    current_variable = selected_variables(k);
    export_struct.(variable_names{current_variable}) = squeeze(U{cell_num}.S_ctk(current_variable,:,:));
end

%% export structure stimulus trace
T_directory = 'C:\Users\jacheung\Dropbox\HLabBackup\Jon\DATA\TrialArrayBuilders\';
S_directory = 'C:\Users\jacheung\Dropbox\HLabBackup\Jon\DATA\SpikesData\SweepArrays\';
ST_directory = 'C:\Users\jacheung\Dropbox\HLabBackup\Jon\DATA\SpikesData\SpikeArrays\';
S_directory_backup = 'C:\Users\jacheung\Dropbox\HLabBackup\Jon\DATA\SpikesData\SweepArrays_Phil\';
ST_directory_backup =  'C:\Users\jacheung\Dropbox\HLabBackup\Jon\DATA\SpikesData\SpikeArrays_Phil\';

T_name = ['trial_array_' U{cell_num}.meta.mouseName '_' U{cell_num}.meta.sessionName '_' U{cell_num}.meta.cellName '_' U{cell_num}.meta.cellCode];  
sweep_name = ['sweepArray_' U{cell_num}.meta.mouseName '_' U{cell_num}.meta.sessionName '_' U{cell_num}.meta.cellName '_' U{cell_num}.meta.cellCode];
spikes_trials = ['spikes_trials_' U{cell_num}.meta.mouseName '_' U{cell_num}.meta.sessionName '_' U{cell_num}.meta.cellName '_' U{cell_num}.meta.cellCode];

try
    load([T_directory T_name '.mat'])
    load([S_directory sweep_name  '.mat'])
    load([ST_directory spikes_trials  '.mat'])
catch
    cell_number = regexp(T_array_list(g).name,'\d*','Match' );
    load([S_directory_backup sweep_name '_' cell_number{1}  '.mat'])
    load([ST_directory_backup spikes_trials '_' cell_number{1}  '.mat'])
end

view_window = 20;
high_pass_trace = zeros(s.sweeps{1}.sweepLengthInSamples,length(s)); 
for i = 1:length(s.sweeps)
    sts = spikes_trials.spikesTrials{i}.spikeTimes;
    raw_sts = s.sweeps{i}.spikeTimes;
    [~,st_idx] = intersect(raw_sts,sts);
    clean_spike_windows = (s.sweeps{i}.spikeTimes(st_idx)) + [-view_window:view_window];
    high_pass_trace(:,i) = s.sweeps{i}.highPassFilteredSignal;
    zero_idx = setdiff(1:length(high_pass_trace(:,i)),clean_spike_windows(:));
    high_pass_trace(zero_idx,i) = 0; 
end

% plot_samples = randsample(numel(s.sweeps),5);
% figure(380);clf
% for k = 1:numel(plot_samples)
%     figure(380);subplot(5,1,k)
%     plot(high_pass_trace(:,plot_samples(k)));
% end
[~,useTrials] = intersect(T.trialNums,T.whiskerTrialNums);
export_struct.spikes = high_pass_trace((T.whiskerTrialTimeOffset*100000)+1:end,useTrials);


