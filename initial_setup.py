import numpy
import pandas as pd
import dk_utilities
import json
import os
import warnings
warnings.filterwarnings("ignore")
pd.options.display.max_columns=999

with open(r'config.json') as f:
    config = json.load(f)

#generate file structure
try:
    os.makedirs('./data/raw_data')
    os.mkdir('./data/results')
except:
    pass

# rotogurus
if not os.path.exists('./data/raw_data/dk_all_games.csv'):
    all_games = dk_utilities.rotogurus_scrape(config)
    
all_games.to_csv(r'data/raw_data/dk_all_games.csv',index=False)  

#split the data to build a model for testing
all_games = pd.read_csv('./data/raw_data/dk_all_games.csv')
(hist_raw, hist_hist) = dk_utilities.split_data(config, all_games, 'test')
hist_raw.to_csv('./data/raw_data/build_model_raw_data_testing.csv', index = False)     
hist_hist.to_csv('./data/raw_data/build_model_historical_data_testing.csv', index = False)

#split the data to build a model for play
all_games = pd.read_csv('./data/raw_data/dk_all_games.csv')
(hist_raw, hist_hist) = dk_utilities.split_data(config, all_games, 'play')
hist_hist.to_csv('./data/raw_data/build_model_historical_data.csv', index = False)
weekly_dk_dl = pd.read_csv('./DKSalaries_%s_wk%s.csv' % (config['current_year'],config['current_week']))
raw_data = dk_utilities.convert_dk_csv(config, weekly_dk_dl)
raw_data.to_csv('./data/raw_data/build_model_raw_data.csv', index = False)

# analyze teames to generate stats
from dk_data_prep_hist import DkDataPrepHist
dk_data_prep_hist =  DkDataPrepHist(config,hist_hist)

from dk_data_prep_raw import DkDataPrepRaw
dk_data_prep_raw =  DkDataPrepRaw(config, hist_raw, dk_data_prep_hist.historical_data)

analyzed_raw = dk_data_prep_raw.raw_data
analyzed_raw.to_csv('./data/raw_data/analyzed_raw_data.csv', index = False)

# generate initial csv's
if not os.path.exists('./data/raw_data/random_teams.csv'):
    temp_df = pd.DataFrame(numpy.zeros(shape=(1,len(analyzed_raw.columns))),columns=analyzed_raw.columns)
    temp_df['team_id'] = 0
    temp_df.to_csv('./data/raw_data/random_teams.csv', index=False)

if not os.path.exists('./data/raw_data/random_teams_analyzed.csv'):
    col_list = ['team_id','Year','Week','total_home','team_salary','flex_pos']
    expand_list = analyzed_raw.columns[8:]
    for pos in ['team','Def','QB','RB','WR','TE']:
        for col in expand_list:
            col_list.append('%s_%s_sum' % (pos, col))
            col_list.append('%s_%s_ave' % (pos, col))
    
    temp_df = pd.DataFrame(numpy.zeros(shape=(1,len(col_list))),columns=col_list)
    temp_df.to_csv('./data/raw_data/random_teams_analyzed.csv', index=False)
