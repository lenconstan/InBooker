from flask import Flask
from config import Config
import redis

app = Flask(__name__)
app.config.from_object(Config)
db=redis.from_url(Config.REDISCLOUD_URL)

from app import routes
