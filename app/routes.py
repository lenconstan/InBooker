from app import app
from app import db
from flask import session

@app.route('/')
def hello_world():
    name=db.get('name') or'World'
    session['test'] = 'stan'
    return 'Hello %s!' % name + session['test']

@app.route('/setname/<name>')
def setname(name):
    db.set('name',name)
    return 'Name updated.'
