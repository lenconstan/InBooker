from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class GetForm(FlaskForm):
    raw_barcode = StringField('Barcode', validators=[DataRequired()])
    submit = SubmitField('Zoek')

class OrderForm(FlaskForm):
    locatie = StringField("Loc.")
    submit = SubmitField("Update")
