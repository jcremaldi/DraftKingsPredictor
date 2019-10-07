import pandas as pd
import dk_utilities
from dk_generate_team_stats import DkGenerateTeamStats
import json
pd.set_option('display.width', 140)
pd.options.display.max_columns=999

with open(r'config.json') as f:
    config = json.load(f)

week = 4
year = 2019
weekly_dk_dl = pd.read_csv('data/raw_data/DKSalaries_%s_wk%s.csv' % (year, week))
analyzed_raw_data = pd.read_csv('data/raw_data/analyzed_raw_data.csv')
#

roster_explicit = {
        'QB'    : 'Jameis Winston'
        ,'Def'  : 'Giants ' #must include space after name
        ,'TE'   : 'Eric Ebron'
        ,'WR1'  : 'JuJu Smith-Schuster'        
        ,'WR2'  : 'Robert Woods'
        ,'WR3'  : 'Mecole Hardman'   
        ,'RB1'  : 'Leonard Fournette'        
        ,'RB2'  : 'Joe Mixon'
        ,'Flex' : 'Kerryon Johnson'
        }
generate_flex = ['RB']

#roster_explicit = {
#        'QB'    : 'Philip Rivers'
#        ,'Def'  : 'Patriots ' #must include space after name
#        ,'TE'   : 'Will Dissly'
#        ,'WR1'  : 'Parris Campbell'        
#        ,'WR2'  : 'Cooper Kupp'
#        ,'WR3'  : 'Allen Robinson II'   
#        ,'RB1'  : 'Nick Chubb'        
#        ,'RB2'  : 'Chris Carson'
#        ,'Flex' : 'Aaron Jones'
#        }
#generate_flex = ['RB']

roster_explicit_list = list(roster_explicit.values())
roster = weekly_dk_dl[weekly_dk_dl['Name'].isin(roster_explicit_list)]
print(roster.Name)
print(roster['Salary'].sum())
roster = dk_utilities.convert_dk_csv(config, roster) 


if generate_flex == 'TE':     
    flex_cat = 1
elif generate_flex == 'WR':
    flex_cat = 2
elif generate_flex == 'RB':
    flex_cat = 3
cntr = 1
roster['Year'] = year
roster['week'] = week

dk_generate_team_stats = DkGenerateTeamStats(config, analyzed_raw_data, cntr, roster.Name, generate_flex)        

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
print('actual points: ',track_sal)

for threshold in range(100,170,10):

    prediction = dk_utilities.rf_predict(X_test, threshold)
    print('Threshold %s percent-chance: ' % (threshold), prediction[0][1])



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    












