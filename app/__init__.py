from flask import Flask
from config import Config
import redis
from flask_session import Session

sess=Session()



app = Flask(__name__)
app.config.from_object(Config)
db=redis.from_url(Config.REDISCLOUD_URL)

from app import routes
