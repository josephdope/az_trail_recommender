from flask import Flask, render_template, request
from trail_recommender_v04 import ContentBased, CollabFilter
import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
import pickle

app = Flask(__name__)

with open('details_df', 'rb') as dets_mat:
    proper_df = pickle.load(dets_mat)

with open('transformed_details_df', 'rb') as trans_mat:
    norm_df = pickle.load(trans_mat)

with open('cosine_matrix', 'rb') as cos_mat:
    cosine_mat = pickle.load(cos_mat)

with open('collab_fit', 'rb') as collab_model:
    collab_based = pickle.load(collab_model)



#Build recommender
recommender = ContentBased(norm_df)



#Web app

@app.route('/')
def first():
    trails = list(norm_df['trail_name'])
    return render_template('home.html', trails = trails)

@app.route('/recommendation', methods=['GET','POST'])
def recommendation():
    try:
        user_entered = str(request.form['trail_entered'])
        trail_details = proper_df.loc[proper_df['trail_name'] == user_entered, ["trail_name", "dist", "elev", "difficulty"]].values.tolist()
        results_ids = list(recommender.recommend(user_entered, cosine_mat))
        results_join = proper_df.loc[proper_df["trail_id"].isin(results_ids), ["trail_name", "dist", "elev", "difficulty"]].join(cosine_mat[proper_df.loc[proper_df['trail_name'] == user_entered].index], how = 'left')
        results_join.rename(columns = {results_join.columns[-1]: 'sim'}, inplace = True)
        results_join.sort_values(by = ['sim'], ascending = False, inplace = True)

        return render_template('recommend.html', results = results_join.values.tolist(), trail_details = trail_details)
    except:
        return render_template('no-results.html')

@app.route('/trail-stats')
def stats():
    return render_template('trail-stats.html')



if __name__ == '__main__':
    app.run(debug = True)
