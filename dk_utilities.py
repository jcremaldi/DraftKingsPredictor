def split_data(config, all_games):
    test_year = config['current_year']
    test_week = config['current_rg_week']
    raw_data = all_games[((all_games['Year'] == test_year) & (all_games['Week'] == test_week))].copy()
    historical_data = all_games[((all_games['Year'] == test_year) & (all_games['Week'] < test_week))].copy()

    return raw_data, historical_data

def rotogurus_scrape(config, ):
    import requests
    import pandas as pd
    import io
    from bs4 import BeautifulSoup
    
    BASE_URL='http://rotoguru1.com/cgi-bin/fyday.pl?game=dk&scsv=1&week=WEEK&year=YEAR'
    WEEKS=list(map(str,range(1,config['current_week'])))
    all_games=pd.DataFrame()

    current_year = config['current_year']
    BASE_URL='http://rotoguru1.com/cgi-bin/fyday.pl?week=WEEK&game=dk&scsv=1'
    
    for wk in WEEKS:
        print(current_year,wk)
        result = requests.get(BASE_URL.replace("WEEK",wk))
        c = result.content
        soup = BeautifulSoup(c)
        all_games=pd.concat([all_games,pd.read_csv(io.StringIO(soup.find("pre").text),sep=";")])
    
    all_games = all_games[all_games['DK salary'] != 0].reset_index(drop=True)   
    all_games['ppd'] = all_games['DK points']/all_games['DK salary']
    all_games = limit_players_by_pos(config, all_games)
    
    return all_games

def limit_players_by_pos(config, all_games):
    all_games['rank_week_pos_oppt'] = all_games.groupby(['Year','Week','Oppt','Pos'])['DK salary'].rank(ascending=False,method='first')
    all_games = all_games[all_games['rank_week_pos_oppt'] <= all_games['Pos'].map(config['team_position_allowed'])]
    all_games['rank_week_pos'] = all_games.groupby(['Year','Week','Pos'])['DK salary'].rank(ascending=False,method='first')

    return all_games

def rf_predict(X_test, threshold):
    import pickle
    filename = 'data/results/DK_rf_model_%s.sav' % (threshold)
    loaded_model = pickle.load(open(filename, 'rb'))
    test_result = loaded_model.predict_proba(X_test)
    
    return test_result

def convert_dk_csv(config, raw_data_convert):
    raw_data_convert = raw_data_convert.rename(columns={'Position' : 'Pos', 'Salary' : 'DK salary'})    
    raw_data_convert['h/a'] = 'a'    
    
    def_name_dict = config['def_name_dict']
    
    for each in raw_data_convert.index:
        stop_words = ['I','II','III','IV']
        query_words = raw_data_convert.loc[each,'Name'].split()        
        result_words  = [word for word in query_words if word not in stop_words]
        
        # fix name order
        if len(result_words)>1:
            result = ' '.join(result_words[1:]) + ', ' + result_words[0]
        else:
            result = def_name_dict[result_words[0]]
            
        raw_data_convert.loc[each, 'Name'] = result
        
        # add home games
        if raw_data_convert.loc[each,'Game Info'].split('@')[0] == raw_data_convert.loc[each,'TeamAbbrev']:
            raw_data_convert.loc[each, 'h/a'] = 'h'
        
        raw_data_convert.loc[each,'Oppt'] = raw_data_convert.loc[each,'Game Info'].split(' ')[0].split('@')[1]

    oppt_match_dict = config['oppt_match_dict']
    
    raw_data_convert['Oppt'] = raw_data_convert['Oppt'].map(oppt_match_dict)        
    raw_data_convert.loc[raw_data_convert['Pos'] == 'DST','Pos'] = 'Def'
    return raw_data_convert

def dict_to_df(dictionary):
    import pandas as pd
    #must all be similar dict entries
    df_list = [ v for k,v in dictionary.items()] 
    df = pd.concat(df_list ,axis=0).reset_index(drop=True)
    return df

def standardize_df(dataframe, cols):
    from sklearn import preprocessing
    dataframe[cols] = preprocessing.scale(dataframe[cols])
    return dataframe

def categorize_df(dataframe, cols):
    from sklearn import preprocessing
    le = preprocessing.LabelEncoder()
    for col in cols:
        dataframe[col] = le.fit_transform(dataframe[col])
    return dataframe

def normalize_df(dataframe, cols):
    from sklearn import preprocessing
    dataframe[cols] = preprocessing.normalize(dataframe[cols])
    return dataframe

def makeOverSamplesADASYN(X,y):
    from imblearn.over_sampling import ADASYN 
    sm = ADASYN()
    X, y = sm.fit_sample(X, y)
    return(X,y)

def makeOverSamplesSMOTE(X, y):
    from imblearn.over_sampling import SMOTE
    sm = SMOTE()
    X, y = sm.fit_sample(X, y)
    return X,y

def add_stats(config, raw_data, historical_data, prefix):
    mean_dict = historical_data.groupby(['Name','weight_bucket'])['%sppd' % (prefix)].mean().to_dict()
    stdev_dict = historical_data.groupby(['Name','weight_bucket'])['%sppd' % (prefix)].std().to_dict()
    weighted_mean_dict = {}
    weighted_stdev_dict = {}
    for name in raw_data.Name:
        weighted_mean_dict[name] = mean_dict[(name,'new')]*config['six_month_weight'] + mean_dict[(name,'old')]*(1 - config['six_month_weight'])
        weighted_stdev_dict[name] = stdev_dict[(name,'new')]*config['six_month_weight'] + stdev_dict[(name,'old')]*(1 - config['six_month_weight'])
    raw_data['%sppd_mean' % (prefix)] = raw_data['Name'].map(weighted_mean_dict)
    raw_data['%sppd_stdev' % (prefix)] = raw_data['Name'].map(weighted_stdev_dict)        
    raw_data['%sppd_comb' % (prefix)] = raw_data['%sppd_mean' % (prefix)]/raw_data['%sppd_stdev' % (prefix)]
    raw_data['%sppd_comb_rank' % (prefix)] = raw_data.groupby(['Year','Week','Pos'])['%sppd_comb' % (prefix)].rank(ascending=False, method='first')

    return raw_data

def adjust_points(config, historical_data, against_mean_dict, overall_average_dict, prefix):
    historical_data['%spts' % (prefix)] = 0
    historical_data['%sppd' % (prefix)] = 0
    for index, row in historical_data.iterrows(): 
        temp = (int(row['Year']),str(row['Oppt']),str(row['Pos']))
        temp2 = (int(row['Year']),str(row['Pos']))
        adj = against_mean_dict[temp] - overall_average_dict[temp2]
        historical_data.loc[index, '%spts' % (prefix)] = row['DK points'] + adj
    
    historical_data['%sppd' % (prefix)] = historical_data['%spts' % (prefix)]/historical_data['DK salary']
    
    return historical_data

def get_sharpe_stats(config, raw_data, prefix):
    import numpy as np
    coef = {}
    intercept = {}
    slope = {}
    for position in raw_data.Pos.unique():
        temp_plot = raw_data[raw_data['Pos'] == position].copy()
        temp_plot = temp_plot[temp_plot['%sppd_mean' % (prefix)] >0]
        temp_plot = temp_plot[temp_plot['%sppd_stdev' % (prefix)] >0]
        coef[position] = np.polyfit(temp_plot['%sppd_stdev' % (prefix)], temp_plot['%sppd_mean' % (prefix)], 1)
        intercept[position] = coef[position][1]
        slope[position] = coef[position][1]
        
    raw_data['%ssharpe_rf' % (prefix)] = raw_data['Pos'].map(intercept)
    raw_data['%ssharpe_rat' % (prefix)] = (raw_data['%sppd_mean' % (prefix)] - raw_data['%ssharpe_rf' % (prefix)])/raw_data['%sppd_stdev' % (prefix)]
    raw_data['%ssharpe_rank' % (prefix)] = raw_data.groupby(['Year','Week','Pos'])['%ssharpe_rat' % (prefix)].rank(ascending=False, method='first')
    raw_data = raw_data.sort_values(by=['Year','Week','Pos','sharpe_rank'], ascending=True)      

    return raw_data

def drop_extra_cols(raw_data):
    try:
        raw_data = raw_data.drop(columns=['Unnamed: 0'])      
    except:
        pass

    try:
        raw_data = raw_data.drop(columns=['Unnamed: 0.1'])      
    except:
        pass

    return raw_data



