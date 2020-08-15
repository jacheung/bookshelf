function export_struct = export_for_moviepy(U, cell_num)

export_struct.cell_number = cell_num;
export_struct.spikes = squeeze(U{cell_num}.R_ntk(:,:,:));
touchOn = [find(U{cell_num}.S_ctk(9,:,:)==1)  ;find(U{cell_num}.S_ctk(12,:,:)==1)];
touchOff = [find(U{cell_num}.S_ctk(10,:,:)==1)  ;find(U{cell_num}.S_ctk(13,:,:)==1)];
export_struct.touch_matrix = nan(size(export_struct.spikes));
for g = 1:length(touchOn)
    export_struct.touch_matrix(touchOn(g):touchOff(g)) = 1;
end

variable_names = U{cell_num}.varNames;

selected_variables = [1,3:5];
for k = 1:length(selected_variables)
    current_variable = selected_variables(k);
    export_struct.(variable_names{current_variable}) = squeeze(U{cell_num}.S_ctk(current_variable,:,:));
end

