import pandas as pd
import dk_utilities2
import json
import random
from dk_generate_team_stats import DkGenerateTeamStats
pd.set_option('display.width', 140)
pd.options.display.max_columns=999

with open(r'config2.json') as f:
    config = json.load(f)

week = 4 #config['current_week']
year = config['current_year']
conf_threshold = 0.75
weekly_dk_dl = pd.read_csv('data/raw_data/DKSalaries_%s_wk%s.csv' % (year, week))
raw_data = dk_utilities2.convert_dk_csv(config, weekly_dk_dl)        


analyzed_raw_data = pd.read_csv('data/raw_data/analyzed_raw_data.csv')

wr = raw_data[raw_data['Pos']=='WR'].copy()
rb = raw_data[raw_data['Pos']=='RB'].copy()
qb = raw_data[raw_data['Pos']=='QB'].copy()
te = raw_data[raw_data['Pos']=='TE'].copy()
df = raw_data[raw_data['Pos']=='Def'].copy()

# -----------------------------------------------------------------    
#for <wk3 testing (use most recent full year since no stats yet)
wr_list = list(analyzed_raw_data[analyzed_raw_data['Pos'] == 'WR'].Name)
qb_list = list(analyzed_raw_data[analyzed_raw_data['Pos'] == 'QB'].Name)
te_list = list(analyzed_raw_data[analyzed_raw_data['Pos'] == 'TE'].Name)
rb_list = list(analyzed_raw_data[analyzed_raw_data['Pos'] == 'RB'].Name)
df_list = list(analyzed_raw_data[analyzed_raw_data['Pos'] == 'Def'].Name)

wr = wr[wr['Name'].isin(wr_list)]
rb = rb[rb['Name'].isin(rb_list)]
qb = qb[qb['Name'].isin(qb_list)]
te = te[te['Name'].isin(te_list)]
df = df[df['Name'].isin(df_list)]
# -----------------------------------------------------------------

for i in range(10000):    
    if (i % 67) == 0:
        print(i)
    generate_flex = random.choice(['WR','TE','RB'])
    generate_qb = qb.sample(1)
    generate_df = df.sample(1)
    
    if generate_flex == 'TE':
        generate_te = te.sample(2)
        generate_rb = rb.sample(2)
        generate_wr = wr.sample(3)      
        flex_cat = 1
    elif generate_flex == 'WR':
        generate_wr = wr.sample(4)
        generate_te = te.sample(1)
        generate_rb = rb.sample(2)
        flex_cat = 2
    elif generate_flex == 'RB':
        generate_rb = rb.sample(3)
        generate_te = te.sample(1)
        generate_wr = wr.sample(3)
        flex_cat = 3
            
            
    roster = generate_qb.append([generate_df,generate_te,generate_wr,generate_rb])
    raw_data['Year'] = year
    raw_data['week'] = week
    roster['Year'] = year
    roster['week'] = week


    if ((roster['DK salary'].sum() < 50000) & (roster['DK salary'].sum() > 45000)):
        team_id = 1
        
        dk_generate_team_stats = DkGenerateTeamStats(config, analyzed_raw_data, team_id, roster.Name, generate_flex)        
        
        factors_as_is = config['factors_as_is']
        X_test = dk_generate_team_stats.temp_team_analyzed.copy()        
        X_test['flex_pos'] = flex_cat
        cat_list = list(X_test.columns.values)
        
        track_sal = X_test['team_DK points_sum']

        
        remove = ['team_DK points_sum'
                  ,'team_DK points_ave'
                  ,'Def_DK points_sum'
                  ,'Def_DK points_ave'
                  ,'QB_DK points_sum'
                  ,'QB_DK points_ave'
                  ,'RB_DK points_sum'
                  ,'RB_DK points_ave'
                  ,'WR_DK points_sum'
                  ,'WR_DK points_ave'
                  ,'TE_DK points_sum'
                  ,'TE_DK points_ave'
                  ,'team_ppd_sum' 
                  ,'team_ppd_ave'
                  ,'team_id']
        for each in remove:
            cat_list.remove(each)
        crap = ['flex_pos']
        cat_list = cat_list + crap
        X_test = X_test[cat_list].copy()



        
        prediction = dk_utilities2.rf_predict(X_test, 160)
        if prediction[0][1] >= conf_threshold:
            print('\n', roster)
            print('actual points: ',track_sal)
            print(prediction[0][1])
            #temp_team_amalyzed.to_csv('data/results/winners_%s_wk%s_th%s.csv' % (year, week, round((conf_threshold*1000),0), mode='a', header=False, index=False) 

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    












