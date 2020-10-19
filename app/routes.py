from app import app, Session, session, render_template, url_for, request, redirect, flash
from app import db
from app import datetime, date
from app.forms import LoginForm, GetForm, OrderForm
from flask import request
import json
import requests
from app.apifunctions import get_activity, update_activity

@app.route('/test')
def test():
    disabled = 'disabled'
    order_dict = json.loads(db.get(session['token']))['items'][0]
    session['reference'] = order_dict['reference']
    return session['reference']

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html', title='Over Inbooker')

@app.route('/error', methods=['GET', 'POST'])
def error():
    return render_template('error.html', title='Oh ooh')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    email = form.email.data
    password = form.password.data
    authenticate_url = 'https://br8.freightlive.eu/api/v2/authenticate/sign-in'

    if request.method == 'POST':
        POST_authenticate = requests.post(authenticate_url, json={"email": email, "password": password})
        if POST_authenticate.status_code == 200:
            token = POST_authenticate.json()["token"]
            session['token'] = token
            return redirect(url_for('home'))
        flash('Inloggegevens niet bekend', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/get_order', methods=['GET', 'POST'])
def get_order():
    form = GetForm()
    #get the barcode
    raw_barcode = form.raw_barcode.data
    if request.method == 'POST' and raw_barcode is not None:
        act = get_activity(raw_barcode, session['token'])
        if act[1] == 200:
            if act[0]['items']:
                db.set(session['token'], json.dumps(act[0]))
                db.expire(session['token'], 200)
                return redirect(url_for('order'))
            else:
                flash('De ingevoerde order kon niet worden gevonden', 'danger')
                return redirect(url_for('get_order'))
        else:
            flash('Er is iets misgegaan, probeer het opnieuw')


    return render_template('get_order.html', title='Activiteit ophalen', form=form)

@app.route('/order', methods=['GET', 'POST'])
def order():
    form = OrderForm()
    disabled = 'disabled'
    order_dict = json.loads(db.get(session['token']))['items'][0]

    session['reference'] = order_dict['reference']
    session['assingment_party_name'] = order_dict['assignment']['party_name']
    session['name'] = order_dict['address']['full_name']
    session['activityid'] = order_dict['id']
    session['saywhen'] = order_dict['communication']['saywhen'] # if this variable is '1' Saywhen is activated, if '0' saywehen is not activated
    session['str_package_lines_descriptions'] = [m + 'x '+n for m,n in zip([i['nr_of_packages'].split('.')[0] for i in order_dict['package_lines']],[i['description'] for i in order_dict['package_lines']])]
    session['update_dict'] = {}

    #add current tags to dict that will be posted to retain current tags
    session['update_dict']['tags'] = order_dict['tags']
    session['update_dict']['package_lines'] = order_dict['package_lines']

    # update session['update_dict']['tags'] with session['update_dict']['tags'].append({'tag_type_id': TAGID})
    # tag_type_ids: 2mans: 49, laadklep:53, project: 50, 4mans: 62, bouwpakket: 63

    #check current tags
    session['bool_2mans'] = '49' in [i['tag_type_id'] for i in order_dict['tags']]
    session['bool_laadklep'] = '53' in [i['tag_type_id'] for i in order_dict['tags']]
    session['bool_project'] = '50' in [i['tag_type_id'] for i in order_dict['tags']]
    session['bool_4mans'] = '62' in [i['tag_type_id'] for i in order_dict['tags']]
    session['bool_bouwpakket'] = '63' in [i['tag_type_id'] for i in order_dict['tags']]

    # get form toggle state
    if form.validate_on_submit():
        #saywhen
        if session['saywhen'] == '0' and request.form.get('saywhen_switch') == 'on':
            session['update_dict']['communication'] = {'saywhen': '1', 'send_invite': '1'}
            session['update_dict']['reference'] =  '*' + order_dict['reference']
        else:
            pass

        #tags
        if session['bool_2mans'] == False and request.form.get('tweemans_switch') == 'on':
            session['update_dict']['tags'].append({'tag_type_id': '49'})
        if session['bool_laadklep'] == False and request.form.get('laadklep_switch') == 'on':
            session['update_dict']['tags'].append({'tag_type_id': '53'})
        if session['bool_project'] == False and request.form.get('project_switch') == 'on':
            session['update_dict']['tags'].append({'tag_type_id': '50'})
        if session['bool_4mans'] == False and request.form.get('viermans_switch') == 'on':
            session['update_dict']['tags'].append({'tag_type_id': '62'})
        if session['bool_bouwpakket'] == False and request.form.get('bouwpakket_switch') == 'on':
            session['update_dict']['tags'].append({'tag_type_id': '63'})

        #package_lines
        for i in session['str_package_lines_descriptions']:
            if request.form.get(i) != '':
                session['update_dict']['package_lines'][(session['str_package_lines_descriptions'].index(i))]['description'] = '[' + str(request.form.get(i)) + ' '  + str(date.today().strftime("%d%m")) + ']' + session['update_dict']['package_lines'][(session['str_package_lines_descriptions'].index(i))]['description']
            else:
                pass

        #notes
        if request.form.get("comment-box") != '':
            session['update_dict']['notes'] = order_dict['notes']
            session['update_dict']['notes'].append({
                    "note_category_id": "3",
                    "content": request.form.get("comment-box"),
                    "visible_for_driver": "true",
                    "note_active": "1",
                    "note_category_name": "reference"
                    })

        #update activity
        if bool(session['update_dict']) is True:
            udac = update_activity(session['activityid'], session['update_dict'], session['token'])
            if udac == 200:
                flash('Activiteit succesvol aangepast!', 'success')
                udac == 0
                return redirect(url_for('get_order'))
            else:
                redirect(url_for('error'))

    return render_template('order.html', title='Order', form=form)
