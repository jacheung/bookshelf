function export_struct = export_for_moviepy(U, cell_num)

%% export structure whisker variables 
export_struct.cell_number = cell_num;
export_struct.spikes = squeeze(U{cell_num}.R_ntk);
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

downsampled_trace = zeros(U{cell_num}.t,length(s));
for i = 1:length(s.sweeps)
    sts = spikes_trials.spikesTrials{i}.spikeTimes;
    raw_sts = s.sweeps{i}.spikeTimes;
    [~,st_idx] = intersect(raw_sts,sts);
    clean_spike_windows = (s.sweeps{i}.spikeTimes(st_idx));
    
    max_response = s.sweeps{i}.highPassFilteredSignal(clean_spike_windows);
    min_response = min(s.sweeps{i}.highPassFilteredSignal(clean_spike_windows+[0:5]),[],2);
    
    spike_times = round(T.trials{(i)}.spikesTrial.spikeTimes/10-T.whiskerTrialTimeOffset*1000);
  
    filtered_max = max_response(spike_times>0 & spike_times <=U{cell_num}.t);
    filtered_min = min_response(spike_times>0 & spike_times <=U{cell_num}.t);
    spike_times = spike_times(spike_times>0 & spike_times <=U{cell_num}.t); 
    
    downsampled_trace(spike_times,i) = filtered_max;
    downsampled_trace(spike_times+1,i) = filtered_min;
 
end

% plot_samples = randsample(numel(s.sweeps),3);
% figure(380);clf
% for k = 1:numel(plot_samples)
%     figure(380);subplot(3,1,k)
%     plot(downsampled_trace(:,plot_samples(k)));
% end

[~,useTrials] = intersect(T.trialNums,T.whiskerTrialNums);
export_struct.spikes_trace = downsampled_trace(:,useTrials);
% export_struct.spikes = high_pass_trace((T.whiskerTrialTimeOffset*100000)+1:end,useTrials);


