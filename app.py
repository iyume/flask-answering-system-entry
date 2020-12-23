import os, json
import numpy as np
import pandas as pd

from flask import Flask, render_template, request, url_for, redirect, flash
from wtforms import Form, BooleanField, TextField, validators
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

Flask.jinja_options['line_comment_prefix'] = '##'


with open('pkl/index.json', 'r+') as f:
    PATH_JSON = json.load(f)

AUTHS = pd.DataFrame([['0', 'admin', generate_password_hash('workteam')],
                    ['1', 'guest', generate_password_hash('FuckCat233')]], columns=['id', 'name', 'password_hash'])


class LoginForm(Form):
    user = TextField("Username", [validators.required(), validators.length(min=2, max=6)])
    pwd = TextField("Password", [validators.required(), validators.length(min=2, max=10)])

class AuthModel():
    pass

class User(AuthModel, UserMixin):
    def __init__(self, user_series):
        self.id = user_series['id']
        self.username = user_series['name']
        self.password_hash = user_series['password_hash']

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


app = Flask(__name__)
app.secret_key = 'dev'

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    try:
        user = AUTHS[AUTHS['id'] == user_id]
        return User(user)
    except:
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:

        if request.method == 'POST':
            # 拼接路径
            path_a = request.form['a']
            path_b = request.form['b']
            path_c = request.form['c']
            file_name = request.form['filename']
            file_path = os.path.join('pkl', path_a, path_b, path_c, file_name)

            if request.form['submit'] == 'add':
                if os.path.exists(file_path):
                    flash('文件已存在')
                    return redirect(url_for('index'))
                else:
                    os.system("touch " + file_path)
                    PATH_JSON[path_a][path_b][path_c][file_name] = file_path
                    with open('pkl/index.json', 'w') as f:
                        json.dump(PATH_JSON, f, ensure_ascii=False)
                    # pkl initialization
                    pd.DataFrame(np.arange(7).reshape(1, 7), columns=['问题', 'A', 'B', 'C', 'D', '答案', 'Tags']).to_pickle(file_path)
                    return redirect(url_for('index'))

            # if request.form['submit'] == 'del':
            #     if os.path.exists(file_path):
            #         os.system("rm " + file_path)
            #         del PATH_JSON[path_a][path_b][path_c][file_name]
            #         return redirect(url_for('index'))
            #     else:
            #         flash('你所输入的文件名不存在')
            #         return redirect(url_for('index'))

            #     with open('pkl/index.json', 'w') as f:
            #         json.dump(PATH_JSON, f, ensure_ascii=False)

            return redirect(url_for('index'))

        return render_template('index.html', paths=PATH_JSON)

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        # 验证用户是否存在
        if form.user.data in AUTHS['name'].squeeze().values:
            series = AUTHS[AUTHS['name'] == form.user.data].squeeze()
            user = User(series)
        else:
            flash('用户名或密码错误')
            return redirect(url_for('login'))
        # 验证用户名和密码是否一致
        if form.user.data == user.username and user.validate_password(form.pwd.data):
            login_user(user)
            return redirect(url_for('index'))

        flash('用户名或密码错误')
        return redirect(url_for('login'))

    return render_template('login.html', form=form)


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
            PATH_JSON[path_a][path_b][path_c][file_name] = file_path
            with open('pkl/index.json', 'w') as f: # pkl initilization
                json.dump(PATH_JSON, f, ensure_ascii=False)
            pd.DataFrame(np.arange(7).reshape(1, 7), columns=['问题', 'A', 'B', 'C', 'D', '解析', 'Tags']).to_pickle(file_path)
        if request.form['submit'] == 'del':
            os.system("rm " + file_path)
            del PATH_JSON[path_a][path_b][path_c][file_name]
            with open('pkl/index.json', 'w') as f:
                json.dump(PATH_JSON, f, ensure_ascii=False)
        return redirect(url_for('secret_index'))
    else:
        return render_template('secret_index.html', paths=PATH_JSON)


@app.route('/32rBUiQhYmslIPweiXRu1P4jIqzYPZN36LnZHbgleMqpt79X60/edit', methods=['GET', 'POST'])
def secret_edit():
    filepath = request.args.get('path')
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
        return redirect(url_for('secret_edit', path=filepath))
    return render_template('secret_edit.html', columns_tags=list(df.columns), index_size=df.index.size, df=df)


@app.route('/admin')
def admin():
    return 'hello!'