import os
import redis

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    REDISCLOUD_URL = os.environ.get('REDISCLOUD_URL')
    FLASK_ENV = os.environ.get('FLASK_ENV')


class Costs(object):
    COSTS_ONE = os.environ.get('COSTS_ONE') or 0
    COSTS_TWO = os.environ.get('COSTS_TWO') or 0
    STOP_REV = os.environ.get('STOP_REV') or 0
    MIN_REV = os.environ.get('MIN_REV') or 0
