import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class Trail_Recommender():
    
    def __init__(self, dataframe):
        
        self.dataframe = dataframe    
        
    def recommend(self, trail):
        self.cosine_mat = cosine_similarity(self.dataframe.drop(['trail_name', 'trail_id'], axis = 1), self.dataframe.drop(['trail_name', 'trail_id'], axis = 1))
        indices = pd.Series(self.dataframe.index, index = self.dataframe['trail_name']).drop_duplicates()
        idx = indices[trail]
        sim_scores = list(enumerate(self.cosine_mat[idx]))
        sim_scores = sorted(sim_scores, key = lambda x: x[1], reverse = True)
        sim_scores = sim_scores[1:11]
        trail_indices = [i[0] for i in sim_scores]
        return self.dataframe['trail_name'].iloc[trail_indices]