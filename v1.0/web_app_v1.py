from flask import Flask, render_template, request
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from trail_recommender_v1 import ContentBased, CollabFilter
import psycopg2
import numpy as np
import pandas as pd
import pandas.io.sql as sqlio
import pickle
import os

app = Flask(__name__)

with open('details_df', 'rb') as dets_mat:
    proper_df = pickle.load(dets_mat)

with open('transformed_details_df', 'rb') as trans_mat:
    norm_df = pickle.load(trans_mat)

with open('cosine_matrix', 'rb') as cos_mat:
    cosine_mat = pickle.load(cos_mat)

with open('collab_fit', 'rb') as collab_model:
    collab_based = pickle.load(collab_model)

with open('collab_df', 'rb') as col_df:
    collab_df = pickle.load(col_df)



#Build recommender
recommender = ContentBased(norm_df)



#Web app

@app.route('/')
def first():
    trails = norm_df['trail_name'].values.tolist()
    return render_template('home.html', trail_list = trails)

@app.route('/recommendation', methods=['POST'])
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

@app.route('/sign-in')
def sign_in():
    return render_template('sign-in.html')

@app.route('/user_recommendation')
def user_recommendation():
    user = str(np.random.choice(collab_df['user'], size = 1)[0])
    results_ids = pd.DataFrame(collab_based.recommend(user).sort_values(ascending=False)[:10]).reset_index()
    results_ids.columns = ['trail_id', 'expected_rating']
    results_df = proper_df.loc[proper_df['trail_id'].isin(results_ids['trail_id']),:].merge(results_ids, how = 'right', on = 'trail_id')[["trail_name", "dist", "elev", "difficulty", "expected_rating"]].sort_values(by = ['expected_rating'], ascending = False)
    return render_template('/user_recommendation.html', results = results_df.values.tolist())


if __name__ == '__main__':
    app.run(debug = True)
