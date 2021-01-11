from flask import Flask, session, render_template, url_for, request, redirect, flash, jsonify
from config import Config, Costs, ApiKeys
import redis
from datetime import datetime, date
from functools import wraps
from operator import mul
import xhtml2pdf
import sendgrid
import postmarker



from flask import session
from flask_session import Session

app = Flask(__name__)
app.config.from_object(Config)
db=redis.from_url(Config.REDISCLOUD_URL)





from app import routes
