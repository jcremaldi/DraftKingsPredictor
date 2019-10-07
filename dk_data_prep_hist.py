import pandas as pd
import dk_utilities
pd.options.display.max_columns=999

class DkDataPrepHist():
    
    def __init__(self, config, historical_data):
        self.config = config
        self.historical_data = historical_data
        self.as_oppt_stats()
        self.home_away_stats()
        self.add_game_cnt()
        self.label_old_new()
        self.add_adjusted_stats()
        self.add_adj_historical()
    
    def as_oppt_stats(self):
        self.raw_data_oppt_stats = self.historical_data.copy()
        self.against_oppt_dict = self.raw_data_oppt_stats.groupby(['Oppt','Pos'])['DK points'].mean().to_dict()
        self.overall_average_dict = self.raw_data_oppt_stats.groupby(['Pos'])['DK points'].mean().to_dict()

    def home_away_stats(self):
        self.raw_data_home_away_stats = self.historical_data.copy()
        self.home_away_mean_dict = self.raw_data_home_away_stats.groupby(['Name','h/a'])['DK points'].mean().to_dict()

    def add_game_cnt(self):
        game_cnt_home_dict = self.historical_data[self.historical_data['h/a'] == 'h'].Name.value_counts().to_dict()
        game_cnt_away_dict = self.historical_data[self.historical_data['h/a'] == 'a'].Name.value_counts().to_dict()
        self.historical_data['games_home_tot'] = self.historical_data['Name'].map(game_cnt_home_dict)
        self.historical_data['games_away_tot'] = self.historical_data['Name'].map(game_cnt_away_dict)
        # to do: use this to weight the home_away_ in add_adjusted_stats
        
    def label_old_new(self):
        self.historical_data['weight_bucket'] = 'old'
        self.historical_data.loc[((self.config['current_rg_week'] - self.historical_data['Week']) < self.config['old_new_cutoff']), 'weight_bucket'] = 'new'
        self.historical_data = dk_utilities.drop_extra_cols(self.historical_data)

    def add_adjusted_stats(self):
        for index, row in self.historical_data.iterrows():
            try:
                oppt_adj = self.against_oppt_dict[(row['Oppt'], row['Pos'])] - self.overall_average_dict[row['Pos']]
                self.historical_data.loc[index, 'oppt_pts_adj'] = self.config['oppt_adj_weight']*oppt_adj
            except:
                self.historical_data.loc[index, 'oppt_pts_adj'] = 0
            
            # to do: use game total rather than try/except
            try:
                h_a_adj = self.home_away_mean_dict[(row['Name'],'h')] - self.home_away_mean_dict[(row['Name'],'a')]
                self.historical_data.loc[index, 'home_to_away_pts_adj'] = self.config['h_a_adj_weight']*h_a_adj
            except:
                self.historical_data.loc[index, 'home_to_away_pts_adj'] = 0

    def add_adj_historical(self):
        self.historical_data['oppt_adj_pts'] = self.historical_data['DK points'] + self.historical_data['oppt_pts_adj']
        self.historical_data['home_away_adj_ptsd'] = self.historical_data['DK points'] + self.historical_data['home_to_away_pts_adj']
        self.historical_data['composite_adj_pts'] = self.historical_data['DK points'] + self.historical_data['oppt_pts_adj'] + self.historical_data['home_to_away_pts_adj']
        self.historical_data['oppt_adj_ppd'] = self.historical_data['oppt_adj_pts']/self.historical_data['DK salary']
        self.historical_data['home_away_adj_ppd'] = self.historical_data['home_away_adj_ptsd']/self.historical_data['DK salary']
        self.historical_data['composite_adj_ppd'] = self.historical_data['composite_adj_pts']/self.historical_data['DK salary']






#import json

#with open(r'config2.json') as f:
#    config = json.load(f)          
#test_data_prep = DkDataPrepHist(config, pd.read_csv(r'data/raw_data/dk_historical_raw_data.csv'))
#



















































