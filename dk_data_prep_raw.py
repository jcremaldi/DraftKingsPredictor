import pandas as pd
import dk_utilities2
pd.options.display.max_columns=999


class DkDataPrepRaw():
    
    def __init__(self, config, raw_data, historical_prepped_data):
        self.config = config
        self.raw_data = raw_data
        self.historical_data = historical_prepped_data
        self.new_weight = config['new_weight']
        self.limit_players()
        self.add_base_stats()
        self.add_weighted_stats()

        self.get_sharpe_rank()
        self.get_oppt_adj_sharpe_rank()

    def limit_players(self):
        game_cnt_dict = self.historical_data.Name.value_counts().to_dict()
        self.raw_data['hist_games_tot'] = self.raw_data['Name'].map(game_cnt_dict)
        self.raw_data.to_csv('temp_raw_prepped_results.csv')
        self.raw_data = self.raw_data[self.raw_data['hist_games_tot']>=3]
        # to do: add in checks for injured or recently injured



    def add_base_stats(self):                    
        base_mean_dict = self.historical_data.groupby(['Name'])['DK points'].mean().to_dict()
        base_std_dict = self.historical_data.groupby(['Name'])['DK points'].std().to_dict()
        self.raw_data['ave_dk_pts'] = self.raw_data['Name'].map(base_mean_dict)
        self.raw_data['std_dk_pts'] = self.raw_data['Name'].map(base_std_dict)
        
        base_mean_dict = self.historical_data.groupby(['Name'])['DK salary'].mean().to_dict()
        base_std_dict = self.historical_data.groupby(['Name'])['DK salary'].std().to_dict()
        self.raw_data['ave_dk_salary'] = self.raw_data['Name'].map(base_mean_dict)
        self.raw_data['std_dk_salary'] = self.raw_data['Name'].map(base_std_dict)
                
        self.raw_data['ppd'] = self.raw_data['ave_dk_pts']/self.raw_data['ave_dk_salary']
        
    def add_weighted_stats(self):
        weighted_ave_pts_dict = self.historical_data.groupby(['Name','weight_bucket'])['DK points'].mean().to_dict()        
        weighted_ave_salary_dict = self.historical_data.groupby(['Name','weight_bucket'])['DK salary'].mean().to_dict()        
        
        weighted_pts_mean_dict = {}
        weighted_salary_mean_dict = {}
        for name in self.raw_data.Name:
            weighted_pts_mean_dict[name] = weighted_ave_pts_dict[(name,'new')]*self.config['new_weight'] + weighted_ave_pts_dict[(name,'old')]*(1 - self.config['new_weight'])
            weighted_salary_mean_dict[name] = weighted_ave_salary_dict[(name,'new')]*self.config['new_weight'] + weighted_ave_salary_dict[(name,'old')]*(1 - self.config['new_weight'])
            
        self.raw_data['weighted_pts'] = self.raw_data['Name'].map(weighted_pts_mean_dict)
        self.raw_data['weighted_salary'] = self.raw_data['Name'].map(weighted_salary_mean_dict)
        self.raw_data['weighted_ppd'] = self.raw_data['weighted_pts']/self.raw_data['weighted_salary']
        

    def get_sharpe_rank(self):
        self.ppd_mean_dict = self.historical_data.groupby(['Name'])['ppd'].mean().to_dict()
        self.ppd_std_dict = self.historical_data.groupby(['Name'])['ppd'].std().to_dict()
        self.raw_data['ppd_mean'] = self.raw_data['Name'].map(self.ppd_mean_dict)
        self.raw_data['ppd_stdev'] = self.raw_data['Name'].map(self.ppd_std_dict)
        
        self.raw_data = dk_utilities2.get_sharpe_stats(self.config, self.raw_data, '')

    def get_oppt_adj_sharpe_rank(self):
        self.oppt_adj_ppd_mean_dict = self.historical_data.groupby(['Name'])['oppt_adj_ppd'].mean().to_dict()
        self.oppt_adj_ppd_std_dict = self.historical_data.groupby(['Name'])['oppt_adj_ppd'].std().to_dict()        
        self.raw_data['oppt_adj_ppd_mean'] = self.raw_data['Name'].map(self.oppt_adj_ppd_mean_dict)
        self.raw_data['oppt_adj_ppd_stdev'] = self.raw_data['Name'].map(self.oppt_adj_ppd_std_dict)   
        
        self.home_away_adj_ppd_mean_dict = self.historical_data.groupby(['Name'])['home_away_adj_ppd'].mean().to_dict()
        self.home_away_adj_ppd_std_dict = self.historical_data.groupby(['Name'])['home_away_adj_ppd'].std().to_dict()        
        self.raw_data['home_away_adj_ppd_mean'] = self.raw_data['Name'].map(self.home_away_adj_ppd_mean_dict)
        self.raw_data['home_away_adj_ppd_stdev'] = self.raw_data['Name'].map(self.home_away_adj_ppd_std_dict)   
        
        self.composite_adj_ppd_mean_dict = self.historical_data.groupby(['Name'])['composite_adj_ppd'].mean().to_dict()
        self.composite_adj_ppd_std_dict = self.historical_data.groupby(['Name'])['composite_adj_ppd'].std().to_dict()        
        self.raw_data['composite_adj_ppd_mean'] = self.raw_data['Name'].map(self.composite_adj_ppd_mean_dict)
        self.raw_data['composite_adj_ppd_stdev'] = self.raw_data['Name'].map(self.composite_adj_ppd_std_dict)
        self.raw_data.to_csv('temp_results_raw.csv')
        self.raw_data = dk_utilities2.get_sharpe_stats(self.config, self.raw_data, 'oppt_adj_')
        self.raw_data = dk_utilities2.get_sharpe_stats(self.config, self.raw_data, 'home_away_adj_')
        self.raw_data = dk_utilities2.get_sharpe_stats(self.config, self.raw_data, 'composite_adj_')
  
#import json
#
#with open(r'config2.json') as f:
#    config = json.load(f)          
#test_data_prep = DkDataPrepRaw(config)
#
#
#

















































