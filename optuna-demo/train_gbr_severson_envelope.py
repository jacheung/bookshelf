import os
import pandas as pd
# Project Imports
from molicel_cycle_life_prediction.dataset.p_series_discharge_cpd_dataset import PSeriesDischargeCPDDataset
from molicel_cycle_life_prediction.feature_generator.severson_and_envelope_feature_generator import SeversonNatureAndEnvelopeFeatureGenerator

# Model building
from sklearn.ensemble import GradientBoostingRegressor
import numpy as np
import optuna

data_path = '/Users/jcheung/Library/CloudStorage/OneDrive-SharedLibraries-BEYONDLIMITS,INC/' \
                       'Molicel - General/06 Results/IPYNB_input_files/Raw_files_csvs/P42/all/'

# Dataset: PSeriesDischargeCPDDataset
discharge_class = PSeriesDischargeCPDDataset()
data_file_paths = [data_path+x for x in os.listdir(data_path)]
discharge = discharge_class.load_data(data_filepaths=data_file_paths, para_filepaths=[])
df = discharge[0]

# Feature Generator:
sn = SeversonNatureAndEnvelopeFeatureGenerator()
output, output_meta = sn.generate_features(df)
feature_df = pd.DataFrame(output, columns=output_meta['column_headers'])

# train test split
train_path = '/Users/jcheung/Library/CloudStorage/OneDrive-SharedLibraries-BEYONDLIMITS,INC/' \
                       'Molicel - General/06 Results/IPYNB_input_files/Raw_files_csvs/P42/train'
test_path = '/Users/jcheung/Library/CloudStorage/OneDrive-SharedLibraries-BEYONDLIMITS,INC/' \
                       'Molicel - General/06 Results/IPYNB_input_files/Raw_files_csvs/P42/test'
train_files = os.listdir(train_path)
test_files = os.listdir(test_path)
X_df = pd.DataFrame(output, columns=output_meta['column_headers'])
Y_df = pd.DataFrame(output_meta['Y_values'], columns=output_meta['Y_headers'])
train_X = X_df[X_df['File Name'].isin(train_files)].drop(columns='File Name').astype(float)
train_Y = Y_df[Y_df['File Name'].isin(train_files)].drop(columns=['File Name', 'Cyc#']).astype(float)
test_X = X_df[X_df['File Name'].isin(test_files)].drop(columns='File Name').astype(float)
test_Y = Y_df[Y_df['File Name'].isin(test_files)].drop(columns=['File Name', 'Cyc#']).astype(float)

# clean up empty values/nan values
lookup_df = pd.read_csv('/Users/jcheung/src/molicel-li-ion-cycle-life-prediction/inference_missing_lookup.csv').astype(float).set_index('Cyc#')
dirty_columns = test_X.columns[test_X.isna().sum() > 0]
for cols in dirty_columns:
    dirty_indices = [idx for idx, x in enumerate(test_X[cols].isna()) if x]
    for idx in dirty_indices:
        dirty_idx_cyc = test_X['Cyc#'].iloc[idx]
        fill_value = lookup_df.loc[dirty_idx_cyc, cols]
        test_X[cols].iloc[idx] = fill_value


def objective(trial):
    """
    optuna objective function for GBR tuning
    parameter breakdown: https://www.analyticsvidhya.com/blog/2016/02/complete-guide-parameter-tuning-gradient-boosting-gbm-python/
    """

    param={
        'n_estimators': trial.suggest_int('n_estimators', 10, 100),
        'learning_rate': trial.suggest_float('learning_rate', 0.001, 0.3, log=True),
        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 10, 150),
        'max_depth': trial.suggest_int('max_depth', 20, 150)
    }
    model = GradientBoostingRegressor(loss='quantile', random_state=123,
                                      validation_fraction=0.2, n_iter_no_change=5, **param)
    model.fit(train_X, train_Y.values.ravel())
    pred_y = model.predict(test_X)
    rmse = np.sqrt(np.mean((pred_y-test_Y.values)**2))
    return rmse


if __name__ == "__main__":
    try:
        print('loading study...')
        study = optuna.load_study(study_name='severson-envelope-gbr_v1',
                                  storage='postgresql://localhost/optunadb')
    except KeyError:
        print('no study found. building from scratch...')
        study = optuna.create_study(study_name='severson-envelope-gbr_v1',
                                    storage='postgresql://localhost/optunadb',
                                    pruner=optuna.pruners.HyperbandPruner(),
                                    direction='minimize')
    study.optimize(objective, n_trials=32)
