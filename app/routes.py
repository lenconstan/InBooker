from app import app
from app import db


@app.route('/')
def hello_world():
    name=db.get('name') or'World'
    return 'Hello %s!' % name

@app.route('/setname/<name>')
def setname(name):
    db.set('name',name)
    return 'Name updated.'
