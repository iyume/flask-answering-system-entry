import os, json
import numpy as np
import pandas as pd

from flask import Flask, render_template, request, url_for, redirect, flash
from wtforms import Form, BooleanField, TextField, PasswordField, validators

with open('pkl/index.json', 'r+') as f:
    path_json = json.load(f)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user = request.form['user']
        pwd = request.form['pwd']
        if(user == 'admin' and pwd == 'workteam'):
            return redirect(url_for('secret_index'))
        print("incorrect")
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/32rBUiQhYmslIPweiXRu1P4jIqzYPZN36LnZHbgleMqpt79X60', methods=['GET', 'POST'])
def secret_index():
    if request.method == 'POST':
        path_a = request.form['a']
        path_b = request.form['b']
        path_c = request.form['c']
        file_name = request.form['file']
        file_path = os.path.join('pkl', path_a, path_b, path_c, file_name)
        if request.form['submit'] == 'add':
            os.system("touch " + file_path)
            path_json[path_a][path_b][path_c][file_name] = file_path
            with open('pkl/index.json', 'w') as f: # pkl initilization
                json.dump(path_json, f, ensure_ascii=False)
            pd.DataFrame(np.arange(7).reshape(1, 7), columns=['问题', 'A', 'B', 'C', 'D', '解析', 'Tags']).to_pickle(file_path)
        if request.form['submit'] == 'del':
            os.system("rm " + file_path)
            del path_json[path_a][path_b][path_c][file_name]
            with open('pkl/index.json', 'w') as f:
                json.dump(path_json, f, ensure_ascii=False)
        return redirect(url_for('secret_index'))
    else:
        return render_template('secret_index.html', paths=path_json)

@app.route('/32rBUiQhYmslIPweiXRu1P4jIqzYPZN36LnZHbgleMqpt79X60/edit/<path:filepath>', methods=['GET', 'POST'])
def secret_edit(filepath):
    current_filepath = os.path.join('pkl', filepath)
    df = pd.read_pickle(current_filepath)
    if request.method == 'POST':
        question = request.form['question']
        a = request.form['a']
        b = request.form['b']
        c = request.form['c']
        d = request.form['d']
        solution = request.form['solution']
        tags = request.form['tags']
        series = [question, a, b, c, d, solution, tags]
        if df.loc[0][0] == 0:
            df.loc[0] = series
        else:
            df.loc[df.index.size] = series
        df.to_pickle(current_filepath)
        return redirect(url_for('secret_edit', filepath=filepath))
    return render_template('secret_edit.html', columns_tags=list(df.columns), index_size=df.index.size, df=df)