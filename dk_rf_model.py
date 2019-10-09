import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import warnings
import pickle
import dk_utilities
warnings.filterwarnings("ignore")
pd.options.display.max_columns=999

class DkRfModel():
    
    def __init__(self, config, raw_data, threshold):
        self.raw_data = raw_data
        self.config = config
        self.threshold = threshold
        self.rf_data_prep()
        self.create_store_rf_model()

    def rf_data_prep(self):        

        self.raw_data['target'] = 0
        
        # set target data
        for each in self.raw_data.index:
            if (self.raw_data.loc[each,'team_DK points_sum'] >= self.threshold):
                self.raw_data.loc[each,'target'] = 1    
        
        factors_as_is = list(self.raw_data.columns.values)
        
        # to do: put into dict
        self.raw_data.loc[self.raw_data['flex_pos'] == 'TE', 'flex_pos'] = 1
        self.raw_data.loc[self.raw_data['flex_pos'] == 'WR', 'flex_pos'] = 2
        self.raw_data.loc[self.raw_data['flex_pos'] == 'RB', 'flex_pos'] = 3
        
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
                  ,'team_id'
                  ,'target']
        for each in remove:
            factors_as_is.remove(each)
                
        #can add in other factors if needed (i.e. factors_categorize)
        self.factors_test = factors_as_is
        
        self.X = self.raw_data[self.factors_test].copy()
        self.cat_list = list(self.X.columns.values)
        
        self.y = self.raw_data['target'].copy()
        #balancing
        print(self.raw_data['target'].value_counts())
        print(len(self.y))
        if self.config['model_balance_data']:
            (self.X, self.y) = dk_utilities.makeOverSamplesSMOTE(self.X, self.y)
        print(len(self.y))

    def create_store_rf_model(self):            
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, train_size = .8)
        classifier_rf = RandomForestClassifier(n_estimators = 300, max_features = 'sqrt')
        classifier_rf.fit(X_train, y_train)
        #weight_dict = dict(zip(self.cat_list, classifier_rf.feature_importances_))
        #print(weight_dict)
        y_pred = classifier_rf.predict(X_test)
        print('\n', 'RF accuracy_score: ', accuracy_score(y_test, y_pred),'\n')
        # Save the model to disk
        filename = 'data/results/DK_rf_model_%s.sav' % (self.threshold)
        pickle.dump(classifier_rf, open(filename, 'wb'))    
        
        #--------------------------------------------------------------------------
        # turn off balancing to use the following analysis
        if not self.config['model_balance_data']:
            x_col = self.X.columns
        
            for feat, importance in zip(x_col, classifier_rf.feature_importances_):
                print('%-25s : %20f' % (feat, importance))
            
            proba_results = classifier_rf.predict_proba(self.X)
            results_cols = self.factors_test + ['actual_pts','expected_pts']
            results = self.raw_data[results_cols].copy()
            results['results0'] = proba_results[:,0]
            results['results1'] = proba_results[:,1]
            
            results.to_csv('data/results/prediction_results.csv')
        #--------------------------------------------------------------------------

import json
with open(r'config.json') as f:
    config = json.load(f)
raw_data = pd.read_csv('data/raw_data/random_teams_analyzed.csv')
len1 = len(raw_data)
raw_data = raw_data.replace([np.inf, -np.inf], np.nan).dropna()
print(len1 - len(raw_data), ' of %s rows lost' % (len1))
for threshold in range(110,180,10):
    print(threshold)
    create_model = DkRfModel(config, raw_data, threshold)



