from flask import Flask, render_template, request
from src.hiking_data_v01 import DataShaper
from src.trail_recommender_v01 import Trail_Recommender
import psycopg2
import pandas.io.sql as sqlio

#DB Connection
conn = psycopg2.connect("dbname='az_trail_recommender' user='josephdoperalski' host='localhost'")
cur = conn.cursor()

#DB Query
query1 = 'SELECT * FROM trail_info'
raw = sqlio.read_sql_query(query1, conn)
raw.drop('index', axis = 1, inplace = True)

#Data Manipulation
shaper = DataShaper(raw)
shaper.adjust_columns()
shaper.fix_column_data()
shaper.tfidf()
shaper.transform()
df = shaper.transformed_df

#Build recommender
recommender = Trail_Recommender(df)

app = Flask(__name__)

@app.route('/')
def first():
    trails = list(df['trail_name'])
    return render_template('home.html', trails = trails)

@app.route('/recommendation', methods=['GET','POST'])
def recommendation():
    try:
        results = list(recommender.recommend(str(request.form['trail_entered'])))
        return render_template('recommend.html', results = results)
    except:
        return render_template('no-results.html')

@app.route('/trail-stats')
def stats():
    pass



if __name__ == '__main__':
    app.run(debug = True)
