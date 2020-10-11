import os
import redis
from flask import Flask

app = Flask(__name__)

REDISCLOUD_URL = 'redis://h:p07b612af7c32ffa406810e89813a138b453c8f1d3b73da45229f4b821d57003b@ec2-3-224-112-206.compute-1.amazonaws.com:25119'#os.environ['REDISCLOUD_URL']
db=redis.from_url(REDISCLOUD_URL)


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
