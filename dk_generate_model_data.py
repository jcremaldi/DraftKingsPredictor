import pandas as pd
import random
import dk_utilities2
from dk_generate_team_stats import DkGenerateTeamStats 
pd.options.display.max_columns = 999
import json

with open(r'config2.json') as f:
    config = json.load(f)
    
def dk_generate_model_data(i, analyzed_raw_data):
    wr = analyzed_raw_data[analyzed_raw_data['Pos']=='WR'].copy()
    rb = analyzed_raw_data[analyzed_raw_data['Pos']=='RB'].copy()
    qb = analyzed_raw_data[analyzed_raw_data['Pos']=='QB'].copy()
    te = analyzed_raw_data[analyzed_raw_data['Pos']=='TE'].copy()
    df = analyzed_raw_data[analyzed_raw_data['Pos']=='Def'].copy()
    
    cntr = pd.read_csv(r'data/raw_data/random_teams.csv')['team_id'].max() + 1
    
    for j in range(i):
        generate_flex = random.sample(['WR','TE','RB'], 1)
        generate_qb = qb.sample(1)
        generate_df = df.sample(1)
        
        if generate_flex[0] == 'TE':
            generate_te = te.sample(2)
            generate_rb = rb.sample(2)
            generate_wr = wr.sample(3)
        elif generate_flex[0] == 'WR':
            generate_wr = wr.sample(4)
            generate_te = te.sample(1)
            generate_rb = rb.sample(2)
        elif generate_flex[0] == 'RB':
            generate_rb = rb.sample(3)
            generate_te = te.sample(1)
            generate_wr = wr.sample(3)
            
        roster = generate_qb.append([generate_df,generate_te,generate_wr,generate_rb])
        roster = dk_utilities2.drop_extra_cols(roster)

        roster['team_id'] = cntr
        if (roster['DK salary'].sum() < 50000):# & (roster['DK salary'].sum() > 45000)):
            
            roster.to_csv('data/raw_data/random_teams.csv', mode='a', header=False, index=False)            
            
            dk_generate_team_stats = DkGenerateTeamStats(config, analyzed_raw_data, cntr, roster.Name, generate_flex)
            temp_team_amalyzed = dk_generate_team_stats.temp_team_analyzed

            temp_team_amalyzed.to_csv('data/raw_data/random_teams_analyzed.csv', mode='a', header=False, index=False) 
            print(j, cntr)
            cntr += 1
                

# use to create rawdate for the model independently               
dk_generate_model_data(10000, pd.read_csv('./data/raw_data/analyzed_raw_data.csv'))  