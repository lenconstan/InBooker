from flask import Flask, session, render_template, url_for, request, redirect, flash, jsonify
from config import Config, Costs, ApiKeys
import redis
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from functools import wraps
from operator import mul, itemgetter
import xhtml2pdf
import sendgrid
import postmarker
from flask_session import Session

app = Flask(__name__)
app.config.from_object(Config)
db=redis.from_url(Config.REDISCLOUD_URL)
rel_db = SQLAlchemy(app)
migrate = Migrate(app, rel_db)


from app import routes, models
