import os
import redis
from flask import Flask

app = Flask(__name__)
db=redis.from_url(os.environ['REDISCLOUD_URL'])


@app.route('/')
def hello_world():
    name=db.get('name') or'World'
    return 'Hello %s!' % name

@app.route('/setname/<name>')
def setname(name):
    db.set('name',name)
    return 'Name updated.'

if __name__ == '__main__':
    app.run()
