from flask import render_template, request
from flaskexample import app
from a_Model import ModelIt
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2

user = 'rogershaw'
host = 'localhost'
dbname = 'lymeforecast'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Miguel' },
       )

@app.route('/db')
def birth_page():
    sql_query = """
                SELECT * FROM "counties.barnstable";
                """
    query_results = pd.read_sql_query(sql_query,con)
    feats = ""
    for i in range(0,2):
        feats += query_results.iloc[i]['variable']
        feats += "<br>"
    return feats

@app.route('/db_fancy')
def cesareans_page_fancy():
    sql_query = """
               SELECT * FROM "counties.barnstable";
                """
    query_results=pd.read_sql_query(sql_query,con)
    feats = []
    for i in range(0,query_results.shape[0]):
        feats.append(dict(index=query_results.iloc[i]['variable'], attendant=query_results.iloc[i][2000], birth_month=query_results.iloc[i][2001]))
    return render_template('cesareans.html',births=births)

@app.route('/input')
def cesareans_input():
    return render_template("input.html")

@app.route('/output')
def cesareans_output():
  #pull 'birth_month' from input field and store it
  # patient = request.args.get('birth_month')
    #just select the Cesareans  from the birth dtabase for the month that the user inputs
  query = '''SELECT "Year", "LymeCases", "Bio01" FROM "counties.barnstable"; '''
  #print query
  query_results=pd.read_sql_query(query,con)
  print query_results
  births = []
  for i in range(0,query_results.shape[0]):
      births.append(dict(index=query_results.iloc[i]['Year'], attendant=query_results.iloc[i]['LymeCases'], birth_month=query_results.iloc[i]['Bio01']))
      #the_result = ''
  the_result = ModelIt(births)
  return render_template("output.html", births = births, the_result = the_result)