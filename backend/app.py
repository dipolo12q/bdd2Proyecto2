from types import MethodDescriptorType
from recovery.DataRecovery import DataRecovery
from numpy import round_
from flask import (
Flask, 
render_template, 
request, 
redirect, 
url_for, 
jsonify,
send_from_directory
)
import os
import recovery.Postgres as pg
import time
app = Flask(__name__, template_folder= '../frontend/', static_folder = '../frontend/')

score_time = 0
retrieve_time = 0

@app.route("/")
def state():
    dataRecovery.ini()
    return  render_template('index.html')


@app.route("/load", methods = ['GET'])
def load():
    print('load')
    dataRecovery.load()
    return url_for('index')


@app.route("/score/<text>/<k>", methods = ['POST'])
def score(text, k):
    print(text)
    n = 1
    start = time.time()
    nresults = dataRecovery.score(text)
    end = time.time()
    global score_time 
    score_time = (end - start)*1000
    palabra = text
    cantidad = k
    print(nresults)
    #jsonify({'succes': dataRecovery.score(text)}),
    return  redirect(url_for('retrieve', number = n, query = palabra, k = cantidad))


@app.route("/retrieve/page<number>/query=<query>/k=<k>", methods = ['GET'])
def retrieve(number, query, k):
    print(number)
    ik = int(k)
    start = time.time()
    data = dataRecovery.retrieve_k_tweets(ik)
    end = time.time()
    global retrieve_time
    retrieve_time = (end - start)*1000
    tiempo_py = round_(score_time + retrieve_time, 3)
    palabra = query
    page = number
    #print(data)
    #postgres
    data2, tiempo_pg = pg.postgres_retrieve_k(query, ik)
    #print(data2)
    
    if(not data):
        return redirect(url_for('retrieve', number = 1, query = palabra, k = k))
    return render_template('retrieve.html', obj2 = data2, obj = data, word = palabra, Npage = page, 
                           cant = str(ik), postgres_time = tiempo_pg, python_time=str(tiempo_py))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    dataRecovery = DataRecovery()
    app.run(debug = True, port = 5050)
    app.add_url_rule('/favicon.ico',
                 redirect_to=url_for('static', filename='src/logoico.png'))