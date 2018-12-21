import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Reader, Dataset, SVD, NMF, evaluate
from surprise.model_selection import GridSearchCV


class ContentBased():
    
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def create_cosine_mat(self):
        self.cosine_mat = cosine_similarity(self.dataframe.drop(['trail_name', 'trail_id'], axis = 1), self.dataframe.drop(['trail_name', 'trail_id'], axis = 1))
        return pd.DataFrame(self.cosine_mat)
    def recommend(self, trail, cosine_mat):
        indices = pd.Series(self.dataframe.index, index = self.dataframe['trail_name']).drop_duplicates()
        idx = indices[trail]
        sim_scores = list(enumerate(cosine_mat[idx]))
        sim_scores = sorted(sim_scores, key = lambda x: x[1], reverse = True)
        sim_scores = sim_scores[1:11]
        trail_indices = [i[0] for i in sim_scores]
        return self.dataframe['trail_id'].iloc[trail_indices]


class CollabFilter():
    
    def __init__(self, dataframe = None):
        self.dataframe = dataframe
        self.reader = Reader(rating_scale = (0, 5))
        self.data = Dataset.load_from_df(self.dataframe[['user', 'trail_id', 'rating']], self.reader)
        self.fit_model = None
        
    def best_params(self):
        param_grid = {'n_factors':[x for x in range(100, 200, 10)], 'n_epochs':[90, 100, 110], 'lr_all':[.003, .005, .008], 'reg_all': [0.08, 0.1, 0.15] }
        gs = GridSearchCV(SVD, param_grid, measures = ['rmse'], cv = 3)
        gs.fit(self.data)
        return gs.best_score['rmse'], gs.best_params['rmse']
    
    def fit(self):
        trainset = self.data.build_full_trainset()
        algo = SVD()
        self.fit_model = algo.fit(trainset)
        return self.fit_model
    
    def recommend(self, user):
        predictions = defaultdict(float)
        x = 1
        for trail in set(self.dataframe['trail_id'].unique())-set(self.dataframe[self.dataframe['user'] == user]['trail_id']):
            print(x)
            x += 1
            predictions[trail] = self.fit_model.predict(user, trail).est
        return pd.Series(predictions).sort_values(ascending = False)[:20]
            


if __name__ == "__main__":
    pass
    
