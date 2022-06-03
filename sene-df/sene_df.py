import pandas as pd
import json

import_path = '/Users/jcheung/Documents/GitHub/bookshelf/sene-df/measurements.csv'
export_path = '/Users/jcheung/Documents/GitHub/bookshelf/sene-df/'

pants_df = pd.DataFrame()
jacket_df = pd.DataFrame()
SBNY = None
df = pd.read_csv(import_path, header=None)
for row in range(0, df.shape[0]):
    try:
        # try to load json structure, if this doesn't pass then it means it's an SBNY number row
        json_dict = json.loads(df.iloc[row][0].replace("'", '"'))

        # ensure we have an SBNY number before proceeding
        if not SBNY:
            raise Exception(f'No SBNY key found for this row {row}')
        # if we have SBNY number then stitch that together with code to build an identifier
        index = f'{SBNY}_{str(json_dict["code"])}'

        # find all rs keys to process. Based on string of rs package into the proper dataframe.
        # so far we only have pant and jacket.
        rs_keys = [k for k in json_dict["rs"].keys()]
        for key in rs_keys:
            json_dict['rs'][key]['SBNY_code'] = index
            # .strip applied to string because string feature is corrupted with spaces... should fix this Mark
            if key.strip() == 'Pant':
                pants_df = pd.concat([pants_df, pd.DataFrame([json_dict['rs'][key]])])
            elif key.strip() == 'Jacket':
                jacket_df = pd.concat([jacket_df, pd.DataFrame([json_dict['rs'][key]])])
            else:
                raise Exception('non-existent key defined for rs')
        SBNY = None
    except json.decoder.JSONDecodeError:
        SBNY = df.iloc[row][0]
        print(f'Processing SBNY: {df.iloc[row][0]}')

# set indices via identifier tag
jacket_df.set_index('SBNY_code', inplace=True)
pants_df.set_index('SBNY_code', inplace=True)

# export file
jacket_df.to_csv(export_path + 'jackets_df.csv')
pants_df.to_csv(export_path + 'pants_df.csv')