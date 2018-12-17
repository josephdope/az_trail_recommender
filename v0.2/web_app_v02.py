from flask import Flask, render_template, request
from src.hiking_data_v02 import DataShaper
from src.trail_recommender_v02 import Trail_Recommender
import psycopg2
import pandas as pd
import pandas.io.sql as sqlio

app = Flask(__name__)

#DB Connection
conn = psycopg2.connect("dbname='az_trail_recommender' user='josephdoperalski' host='localhost'")
cur = conn.cursor()

#DB Query
query2 = 'SELECT * FROM trail_info'
raw = sqlio.read_sql_query(query2, conn)
raw.drop('index', axis = 1, inplace = True)

#Data Manipulation
shaper = DataShaper(raw)
shaper.adjust_columns()
shaper.fix_column_data()
proper_df = shaper.proper_df
shaper.tfidf()
shaper.transform()
norm_df = shaper.transformed_df



#Build recommender
recommender = Trail_Recommender(norm_df)
cosine_mat = pd.DataFrame(recommender.cosine_mat, index = proper_df.index, columns = proper_df.index)



#Web app

@app.route('/')
def first():
    trails = list(norm_df['trail_name'])
    return render_template('home.html', trails = trails)

@app.route('/recommendation', methods=['GET','POST'])
def recommendation():
    try:
        user_entered = str(request.form['trail_entered'])
        trail_details = list(proper_df.loc[proper_df['trail_name'] == user_entered, ["trail_name", "dist", "elev", "difficulty"]].values.tolist())
        results_ids = list(recommender.recommend(user_entered))
        results_join = proper_df.loc[proper_df["trail_id"].isin(results_ids), ["trail_name", "dist", "elev", "difficulty"]].join(cosine_mat[proper_df.loc[proper_df['trail_name'] == user_entered].index], how = 'left')
        results_join.rename(columns = {results_join.columns[-1]: 'sim'}, inplace = True)
        results_join.sort_values(by = ['sim'], ascending = False, inplace = True)

        return render_template('recommend.html', results = results_join.values.tolist(), trail_details = trail_details)
    except:
        return render_template('no-results.html')

@app.route('/trail-stats')
def stats():
    pass



if __name__ == '__main__':
    app.run(debug = True)
