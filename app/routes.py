from app import app, Session, session, render_template, url_for, request
from app import db
from app.forms import LoginForm
from flask import request

import requests
from app import apifunctions

@app.route('/')
def hello_world():
    name=db.get('name') or'World'
    session['test'] = 'test134'
    return 'Hello %s!' % name

@app.route('/setname/<name>')
def setname(name):
    db.set('name',name)
    return 'Name updated.' + session.get('test')


@app.route('/login')
def login():
    form = LoginForm()

    email = form.email.data
    password = form.password.data


    authenticate_url = 'https://br8.freightlive.eu/api/v2/authenticate/sign-in'

    if request.method == 'POST':
        POST_authenticate = requests.post(authenticate_url, json={"email": email, "password": password})

        if POST_authenticate.status_code == 200:
            token = POST_authenticate.json()["token"]
            session['token'] = token
            session['id'] = 'tempid'

            return redirect(url_for('testpage'))
    return render_template('login.html', title='Login', form=form)
