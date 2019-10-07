import numpy as np
import pandas as pd
import statistics
import dk_utilities

class DkGenerateTeamStats():
    
    def __init__(self, config, generate_raw_data, team_id, roster_names, generate_flex):
        self.config = config
        self.team_id = team_id
        self.roster_names = roster_names
        self.generate_flex = generate_flex
        self.col = list(pd.read_csv('data/raw_data/analyzed_raw_data.csv').columns.values)
        self.col_list = ['team_id','Year','Week','total_home','team_salary','flex_pos']
        self.team_roster_stats = generate_raw_data[generate_raw_data['Name'].isin(roster_names)].copy()
        self.team_roster_stats = dk_utilities.drop_extra_cols(self.team_roster_stats)
        self.temp_team_analyzed = pd.DataFrame(np.zeros(shape=(1,len(self.col_list))),columns=self.col_list)

        self.add_non_agg_stats()
        self.add_team_agg_stats()
        self.add_pos_agg_stats()

    def add_non_agg_stats(self):

        self.temp_team_analyzed.loc[0,'team_id'] = self.team_id
        self.temp_team_analyzed.loc[0,'Year'] = statistics.mode(self.team_roster_stats['Year'])
        self.temp_team_analyzed.loc[0,'Week'] = statistics.mode(self.team_roster_stats['Week'])
    
    def add_team_agg_stats(self):
        self.temp_team_analyzed.loc[0,'total_home'] = (self.team_roster_stats['h/a'] == 'h').sum()
        self.temp_team_analyzed.loc[0,'team_salary'] = self.team_roster_stats['DK salary'].sum()
        self.temp_team_analyzed.loc[0,'flex_pos'] = self.generate_flex[0]
                
    def add_pos_agg_stats(self):
        self.temp_list = self.col[8:]

        for pos in ['team','Def','QB','RB','WR','TE']:
            if pos == 'team':
                temp_df = self.team_roster_stats.copy()
            else:
                temp_df = self.team_roster_stats[self.team_roster_stats['Pos'] == pos].copy()
            for col in self.temp_list:
                self.temp_team_analyzed.loc[0,'%s_%s_sum' % (pos,col)] = temp_df[str(col)].sum()
                self.temp_team_analyzed.loc[0,'%s_%s_ave' % (pos,col)] = temp_df[str(col)].mean()

