import os
basedir = os.path.abspath(os.path.dirname(__file__))
import redis

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_ENV = os.environ.get('FLASK_ENV') #Development or Production
    REDISCLOUD_URL = os.environ.get('REDISCLOUD_URL') #Redis cache
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db') #SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Costs(object):
    COSTS_ONE = os.environ.get('COSTS_ONE') or 0
    COSTS_TWO = os.environ.get('COSTS_TWO') or 0
    STOP_REV = os.environ.get('STOP_REV') or 0
    MIN_REV = os.environ.get('MIN_REV') or 0
    STOP_REVS = os.environ.get('STOP_REVS') or {}
    TYPES = os.environ.get('TYPES') or {}

class ApiKeys(object):
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    PICQER_API_KEY = os.environ.get('PICQER_API_KEY')
    PICQER_ENV = os.environ.get('PICQER_ENV')
    POSTMARK_SERVER_TOKEN = os.environ.get('POSTMARK_SERVER_TOKEN')
    POSTMARK_MAIL_ADRESS= os.environ.get('POSTMARK_MAIL_ADRESS')
