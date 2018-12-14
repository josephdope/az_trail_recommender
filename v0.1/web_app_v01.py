from flask import Flask, render_template
from src.trail_recommender_v01 import Trail_Recommender
import psycopg2
import pandas.io.sql as sqlio


conn = psycopg2.connect("dbname='az_trail_recommender' user='josephdoperalski' host='localhost'")
cur = conn.cursor()

query2 = 'SELECT * FROM trail_info'
data2 = sqlio.read_sql_query(query2, conn)
data2.drop('index', axis = 1, inplace = True)

app = Flask(__name__)

@app.route('/')
def first():
    trails = list(data2['trail_name'])
    return render_template('home.html', trails = trails)

@app.route('/recommendation')
def recommendation():
    pass


@app.route('/trail-stats')
def stats():
    pass



if __name__ == '__main__':
    app.run(debug = True)
