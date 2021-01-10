from app import app, Session, session, render_template, url_for, request, redirect, flash, jsonify
from app import db
from app import wraps
from app import datetime, date
from app import Costs, ApiKeys
from app.forms import LoginForm, GetForm, OrderForm
from flask import request
import json
import requests
from app.apifunctions import get_activity, update_activity, check_token, servicelevel, get_route_data, get_nextday_activity, get_activity_paginated, get_fulfillment_customer
from app.dashfunctions import TimeFunctions as tf, InputFunctions as inpf, CostFunctions as cf
import time
import dateutil.parser as dparser
from app import mul
from app.labelmaker import gen_pdf

@app.route('/api/custshipping', methods=['GET', 'POST'])
def custshipping():

    content = request.json
    # print(content)
    print(type(content))
    content_dict = content

    fulfillment_cust_id = inpf.safeget(content_dict, 'picklist', 'idfulfilment_customer')
    print(fulfillment_cust_id)
    #get fulfillment customer data
    fulfillment_cust = get_fulfillment_customer(ApiKeys.PICQER_API_KEY, fulfillment_cust_id)
    status_code = fulfillment_cust[1]
    request_dict = fulfillment_cust[0]

    template_data = {'fulfillmentcustomer': '',
                    'reference': '',
                    'deliveryname': '',
                    'emailaddress': '',
                    'telephone': '',
                    'picklistid': ''}
    if status_code == 200:
        template_data['fulfillmentcustomer'] = inpf.safeget(request_dict, 'name', 'Niet beschikbaar')

    template_data['reference'] = inpf.safeget(content, 'picklist', 'reference')
    template_data['deliveryname'] = inpf.safeget(content, 'picklist', 'deliveryname')
    template_data['emailaddress'] = inpf.safeget(content, 'picklist', 'emailaddress')
    template_data['telephone'] = inpf.safeget(content, 'picklist', 'telephone')
    template_data['picklistid'] = inpf.safeget(content, 'picklist', 'picklistid')

    try:
        label = gen_pdf(render_template('label.html', template_data=template_data))
    except:
        return jsonify('Error in label generation'), 400

    try:
        MailClient.send_grid(template_data.get('deliveryname', 'NA'), template_data.get('emailaddress', 'NA'), template_data.get('deliveryname', 'NA'), template_data.get('picklistid', 'NA'))
        return jsonify({"identifier": "Ophalen",
                            "label_contents_pdf": label})
    except:
        return jsonify('Error in mailclient'), 400


@app.before_request
def before_request():
    if not request.is_secure and app.env != "development":
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)

def identificate(f):
    @wraps(f)
    def check_auth(*args, **kwargs):
        try:
            if session['token']:
                token_status_code = check_token(session['token'])
            if token_status_code == 200:
                return f(*args, **kwargs)
            else:
                return redirect(url_for('login', next=request.endpoint))
                flash('Je bent niet of niet meer ingelogd, graag even inloggen!', 'danger')

        except KeyError:
            return redirect(url_for('login', next=request.endpoint))
            flash('Je bent niet of niet meer ingelogd, graag even inloggen!', 'danger')
    return check_auth

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error.html', error=e), 404

@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 500 status explicitly
    return render_template('error.html', error=e), 500

# @app.route('/picqer/stockchanges', methods=['GET', 'POST'])
# def stockchanges():


@app.route('/docker', methods=['GET', 'POST'])
def docker():
    form = GetForm()
    #get the barcode
    raw_barcode = form.raw_barcode.data
    if request.method == 'POST' and raw_barcode != '':
        try:
            act = get_nextday_activity(raw_barcode, session['token'])
        except KeyError:
            flash('Je bent nog niet ingelogd, graag even inloggen!', 'danger')
            return redirect(url_for('login', next=request.endpoint))
        if act[1] == 200:
            if act[0]['items']:
                db.set(session['token'], json.dumps(act[0]))
                db.expire(session['token'], 600)
                return redirect(url_for('order', predes='docker'))
            else:
                flash('De ingevoerde order staat niet ingepland voor de aankomende routes', 'danger')
                return redirect(url_for('docker'))
        if act[1] == 403:
            flash('Je sessie is verlopen, graag opnieuw inloggen!', 'danger')
            return redirect(url_for('login', next=request.endpoint))

        else:
            flash('Je hebt nog geen barcode gescanned', 'danger')
    return render_template('docker.html', title='Docker', form=form)

@app.route('/label', methods=['GET', 'POST'])
def label():

    return render_template('label.html')

@app.route('/docks', methods=['GET', 'POST'])
def docks():
    dock_list = ['Dock 11', 'Dock 10', 'Dock 9', 'Dock 8', 'Dock 7', 'Dock 6', 'Projectenvak', 'UG/RET']
    if request.method == 'POST':
        pass
    return render_template('docks.html', title='Docks', dock_list=dock_list)

@app.route('/routes', methods=['GET', 'POST'])
@identificate
def routes():
    #1 - Get the value from the datepicker
    date_from = request.form.get('date_from') or None
    date_to = request.form.get('date_to') or None

    #prepare the from and to dates for the api-call

    if request.method == 'POST':
        date_from_req = None
        date_to_req = None
        if date_from is None:
            flash('Je hebt geen datum of databereik ingevluld', 'danger')
            return redirect(url_for('routes'))
        else:
            date_from_req = date_from + 'T00:00:00.000Z'
            if date_to is not None:
                date_to_req = date_to + 'T23:59:59.999Z'
            if date_from is not None and date_to is None:
                date_to_req = date_from + 'T23:59:59.999Z'

        #Forward the datetime data to the query page
        return redirect(url_for('routes_query_two', date_from=date_from_req, date_to=date_to_req))



    return render_template('routes.html', title='RouteDash')

@app.route('/routes_query_two', methods=['GET', 'POST'])
# @identificate
def routes_query_two():
    # obtain datepicker input dates
    start = request.args['date_from'] or None
    stop = request.args['date_to'] or None
    # format selected datetimes for view
    start2 = start.split('T')[0]
    stop2 = stop.split('T')[0]

    activity_data = get_activity_paginated(session['token'], start, stop)[0]
    route_data = get_route_data(start, stop, 0, session['token'])

    costs = {'1mans': float(Costs.COSTS_ONE) / 60, '2mans': float(Costs.COSTS_TWO)/60}
    stop_rev = float(Costs.STOP_REV)
    rev_min = float(Costs.MIN_REV)
    stop_revs = json.loads(Costs.STOP_REVS)
    types = json.loads(Costs.TYPES)

    #collect route data
    routes_list = []
    if route_data[1] == 200 and route_data[0]['items']:
        for i in route_data[0]['items']:
            one_or_two_man = cf.def_two_men(inpf.safeget(i, 'driver', 'full_name'), inpf.safeget(i, 'trailer', 'name'), 'NA')
            routes_list.append({'id': inpf.safeget(i, 'id'), 'nr': inpf.safeget(i,'nr'), 'name': inpf.safeget(i, 'name'), 'nr_of_stops': inpf.safeget(i,'nr_of_stops'),
            'driver_full_name': inpf.safeget(i, 'driver', 'full_name'), 'trailer' :inpf.safeget(i, 'trailer', 'name'), 'car': inpf.safeget(i, 'car', 'name'), 'planned_driving_distance': inpf.try_it(str(round(int(i['planned_driving_distance'])/1000, 1)), 0),
             'planned_activity_duration': inpf.safeget(i, 'planned_activity_duration'), 'billable_minutes': (float(inpf.safeget(i, 'planned_activity_duration')) - float(inpf.safeget(i, 'planned_start_duration')) - float(inpf.safeget(i, 'planned_end_duration'))),
             'planned_total_duration': inpf.safeget(i, 'planned_total_duration'), 'actual_duration': tf.timedelta(inpf.safeget(i, 'executed_date_time_from'), inpf.safeget(i, 'executed_date_time_to')), 'date': inpf.split_it(inpf.safeget(i, 'planned_date_time_from'), ' ', 0), 'zones': inpf.list_to_string(inpf.safeget(i, 'zone_names')), 'two_man': one_or_two_man,
             'planned_start_duration' : inpf.safeget(i, 'planned_start_duration'), 'planned_end_duration': inpf.safeget(i, 'planned_end_duration'), 'activity_ids': inpf.safeget(i, 'activity_ids'),
             'exp_costs': cf.exp_costs(one_or_two_man, inpf.safeget(i, 'planned_total_duration'), costs.get('1mans', 0), costs.get('2mans', 0))
              })

        tf.sort_by_date(routes_list)
        #collect stop data
        for i in routes_list:
            route_rev = 0
            for j in i['activity_ids']:
                for k in activity_data:
                    if k['id'] == str(j):
                        temp = servicelevel(inpf.safeget(k, 'tags'), "tag_type_name", ['2mans'])
                        routes_list[routes_list.index(i)]['activity_ids'][i['activity_ids'].index(j)] = {
                        'reference': inpf.safeget(k, 'reference'),
                        'party_name': inpf.safeget(k, 'assignment', 'party_name'),
                        'duration': inpf.safeget(k, 'duration'),
                        'servicelevel': servicelevel(inpf.safeget(k, 'tags'), "tag_type_name", ['Overalinhuis', 'Gebruiksklaar', 'Project', 'Ophalen+Verpakken (kwetsbaar)', 'Ophalen', 'Magazijnretour', 'Beganegrond', 'Magazijn Ophalen']),
                        'manpower': (lambda x : '2mans' if x == '2mans' else '1mans')(temp),
                        'stop_rev': cf.ind_stop_rev(types, servicelevel(inpf.safeget(k, 'tags'), "tag_type_name", ['Overalinhuis', 'Gebruiksklaar', 'Project', 'Ophalen+Verpakken (kwetsbaar)', 'Ophalen', 'Magazijnretour', 'Beganegrond', 'Magazijn Ophalen']), (lambda x : '2mans' if x == '2mans' else '1mans')(temp), inpf.safeget(k, 'assignment', 'party_name'), 1, int(inpf.safeget(k, 'duration')))}
                        route_rev+=cf.ind_stop_rev(types, servicelevel(inpf.safeget(k, 'tags'), "tag_type_name", ['Overalinhuis', 'Gebruiksklaar', 'Project', 'Ophalen+Verpakken (kwetsbaar)', 'Ophalen', 'Magazijnretour', 'Beganegrond', 'Magazijn Ophalen']), (lambda x : '2mans' if x == '2mans' else '1mans')(temp), inpf.safeget(k, 'assignment', 'party_name'), 1, int(inpf.safeget(k, 'duration')))
            t_rl_i = routes_list[routes_list.index(i)]
            t_rl_i['exp_rev'] = route_rev
            t_rl_i['exp_margin'] = cf.margin(t_rl_i['exp_costs'], t_rl_i['exp_rev'])

        #compute totals
        exp_totals = {'sum_exp_costs': cf.totals(routes_list, 'exp_costs'), 'sum_exp_rev': cf.totals(routes_list, 'exp_rev')}
        exp_tot_mar = {'sum_exp_margin': round(((exp_totals['sum_exp_rev']-exp_totals['sum_exp_costs'])/exp_totals['sum_exp_rev'])*100, 3)}
        sum_stops = int(cf.totals(routes_list, 'nr_of_stops'))

        return render_template('routes_query_two.html', title='Query results', date_from=start2, date_to=stop2, query=routes_list, totals=exp_totals, margin=exp_tot_mar, sum_stops=sum_stops)



@app.route('/routes_query', methods=['GET', 'POST'])
# @identificate
def routes_query():

    costs = {'1mans': float(Costs.COSTS_ONE), '2mans': float(Costs.COSTS_TWO)}
    stop_rev = float(Costs.STOP_REV)
    rev_min = float(Costs.MIN_REV)

    def delta(t1, t2):
        """Provides the timedelta between two datetime values in minutes"""
        try:
            d1 = dparser.parse(t1, fuzzy=True)
            d2 = dparser.parse(t2, fuzzy=True)
            factors = (60, 1, 1/60)
            duration = str((d2 - d1))
            duration_minutes = sum(i*j for i, j in zip(map(int, duration.split(':')), factors))
            return str(round(duration_minutes))
        except:
            return 'NA'

    def try_it(input_key):
        try:
            if input_key:
                return input_key
            else:
                return 'NA'
        except:
            return 'NA'

    def safeget(dct, *keys):
        for key in keys:
            try:
                dct = dct[key]
            except (KeyError, TypeError) as e:
                return 'NA'
        return dct

    def def_two_men(val_a, val_b, na_val):
        if val_a == na_val and val_b == na_val:
            return True
        elif val_a != na_val and val_b != na_val:
            return True
        elif val_b != na_val:
            return True
        else:
            return False

    def list_to_string(s):
        try:
            str1 = " "
            return (str1.join(s))
        except (KeyError, TypeError) as e:
            return 'NA'

    def split_it(it, split_char, split_index):
        try:
            if type(it) is str:
                return it.split(split_char)[split_index]
        except (KeyError, TypeError) as e:
            return 'NA'

    def sort_by_date(list_obj):
        try:
            list_obj.sort(key = lambda x:x['date'])
        except (KeyError, TypeError) as e:
            pass

    def get_tag(list_obj, tag):
        if list_obj:
            return tag in list_obj
        else:
            return False



    def rev_exp(driver, trailer, trailer_val, bool, costs_oneman, costs_twomen, stops, stop_rev, duration, rev_min, act_dur, loading_time, unloading_time):
        exp_costs = 0
        #Expenses

        #Determine 2mans or 1mans and calculate costs with according cost figures
        if driver == trailer_val and trailer == trailer_val:
            exp_costs = round(costs_twomen * float(duration), 2)
        elif trailer != trailer_val:
            exp_costs = round(costs_twomen * float(duration), 2)
        else:
            exp_costs = round(costs_oneman * float(duration), 2)

        # if bool is True:
        #     exp_costs = round(costs_twomen * (float(duration) - float(loading_time) - float(unloading_time)), 2)
        # else:
        #     exp_costs = round(costs_oneman * (float(duration) - float(loading_time) - float(unloading_time)), 2)
        #Revenue
        rev = round(float(stops) * stop_rev + (float(act_dur) - float(loading_time) - float(unloading_time)) * rev_min, 2)
        # rev = round(float(stops) * stop_rev + float(act_dur) * rev_min, 2)
        #Margin
        try:
            margin = round(((rev - exp_costs) / rev), 2)
        except ZeroDivisionError:
            margin = 0

        return exp_costs, rev, margin

    def totals(list, object_to_sum):
        try:
            total = 0
            for i in list:
                total += float(i[object_to_sum])

            return round(total, 2)
        except TypeError:
            return 'NA'


    # obtain datepicker input dates
    start = request.args['date_from'] or None
    stop = request.args['date_to'] or None
    # format selected datetimes for view
    start2 = start.split('T')[0]
    stop2 = stop.split('T')[0]
    route_data = get_route_data(start, stop, 0, session['token'])

    # print(route_data)
    routes_list = []
    if route_data[1] == 200 and route_data[0]['items']:
        for i in route_data[0]['items']:
            routes_list.append({'id': safeget(i, 'id'), 'nr': safeget(i,'nr'), 'name': safeget(i, 'name'), 'nr_of_stops': safeget(i,'nr_of_stops'),
            'driver_full_name': safeget(i, 'driver', 'full_name'), 'trailer' :safeget(i, 'trailer', 'name'), 'car': safeget(i, 'car', 'name'), 'planned_driving_distance': inpf.try_it(str(round(int(i['planned_driving_distance'])/1000, 1)), 0),
             'planned_activity_duration': safeget(i, 'planned_activity_duration'), 'billable_minutes': (float(safeget(i, 'planned_activity_duration')) - float(safeget(i, 'planned_start_duration')) - float(safeget(i, 'planned_end_duration'))),
             'planned_total_duration': safeget(i, 'planned_total_duration'), 'actual_duration': delta(safeget(i, 'executed_date_time_from'), safeget(i, 'executed_date_time_to')), 'date': split_it(safeget(i, 'planned_date_time_from'), ' ', 0), 'zones': list_to_string(safeget(i, 'zone_names')), 'two_man': def_two_men(safeget(i, 'driver', 'full_name'), safeget(i, 'trailer', 'name'), 'NA'),
             'planned_start_duration' : safeget(i, 'planned_start_duration'), 'planned_end_duration': safeget(i, 'planned_end_duration'),
             'exp_costs': rev_exp(safeget(i, 'driver', 'full_name'), safeget(i, 'trailer', 'name'), 'NA', get_tag(safeget(i, 'tag_names'), '2mans'), costs['1mans'], costs['2mans'], safeget(i,'nr_of_stops'), stop_rev, safeget(i, 'planned_total_duration'),rev_min, safeget(i, 'planned_activity_duration'), safeget(i, 'planned_start_duration'), safeget(i, 'planned_end_duration'))[0],
             'exp_rev': rev_exp(safeget(i, 'driver', 'full_name'), safeget(i, 'trailer', 'name'), 'NA', get_tag(safeget(i, 'tag_names'), '2mans'), costs['1mans'], costs['2mans'], safeget(i,'nr_of_stops'), stop_rev, safeget(i, 'planned_total_duration'),rev_min, safeget(i, 'planned_activity_duration'), safeget(i, 'planned_start_duration'), safeget(i, 'planned_end_duration'))[1],
             'exp_margin': rev_exp(safeget(i, 'driver', 'full_name'), safeget(i, 'trailer', 'name'), 'NA', get_tag(safeget(i, 'tag_names'), '2mans'), costs['1mans'], costs['2mans'], safeget(i,'nr_of_stops'), stop_rev, safeget(i, 'planned_total_duration'),rev_min, safeget(i, 'planned_activity_duration'), safeget(i, 'planned_start_duration'), safeget(i, 'planned_end_duration'))[2] *100

              })



        sort_by_date(routes_list)


        exp_totals = {'sum_exp_costs': totals(routes_list, 'exp_costs'), 'sum_exp_rev': totals(routes_list, 'exp_rev')}
        exp_tot_mar = {'sum_exp_margin': round(((exp_totals['sum_exp_rev']-exp_totals['sum_exp_costs'])/exp_totals['sum_exp_rev'])*100, 3)}
        sum_stops = int(totals(routes_list, 'nr_of_stops'))

    return render_template('routes_query.html', title='Query results', date_from=start2, date_to=stop2, query=routes_list, totals=exp_totals, margin=exp_tot_mar, sum_stops=sum_stops)


@app.route('/test')
def test():
    disabled = 'disabled'
    order_dict = json.loads(db.get(session['token']))['items'][0]
    session['reference'] = order_dict['reference']
    return session['reference']


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html', title='InBooker')


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
            session['initials'] = POST_authenticate.json()['user']['name_prefix']
            return redirect(request.args.get('next') or url_for('home'))
            # return redirect(url_for('home'))
        flash('Inloggegevens niet bekend', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/get_order', methods=['GET', 'POST'])
def get_order():
    form = GetForm()
    #get the barcode
    raw_barcode = form.raw_barcode.data
    if request.method == 'POST' and raw_barcode != '':
        try:
            act = get_activity(raw_barcode, session['token'])
        except KeyError:
            flash('Je bent nog niet ingelogd, graag even inloggen!', 'danger')
            return redirect(url_for('login', next=request.endpoint))
        if act[1] == 200:
            if act[0]['items']:
                db.set(session['token'], json.dumps(act[0]))
                db.expire(session['token'], 600)
                return redirect(url_for('order', predes='get_order'))
            else:
                flash('De ingevoerde order kon niet worden gevonden', 'danger')
                return redirect(url_for('get_order'))
        if act[1] == 403:
            flash('Je sessie is verlopen, graag opnieuw inloggen!', 'danger')
            return redirect(url_for('login', next=request.endpoint))

        else:
            flash('Je hebt nog geen barcode gescanned', 'danger')

    return render_template('get_order.html', title='Activiteit ophalen', form=form)

@app.route('/scan_order', methods=['GET', 'POST'])
def scan_order():
    form = GetForm()
    if request.method == 'POST':
        if request.form.get('scan-input') != '':
            try:
                act = get_activity(request.form.get("scan-input"), session['token'])
            except KeyError:
                flash('Je bent nog niet ingelogd, graag even inloggen!', 'danger')
                return redirect(url_for('login', next=request.endpoint))
            if act[1] == 200:
                if act[0]['items']:
                    db.set(session['token'], json.dumps(act[0]))
                    db.expire(session['token'], 600)
                    return redirect(url_for('order', predes='scan_order'))
                else:
                    flash('De ingevoerde order kon niet worden gevonden', 'danger')
                    return redirect(url_for('scan_order'))
            if act[1] == 403:
                flash('Je sessie is verlopen, graag opnieuw inloggen!', 'danger')
                return redirect(url_for('login', next=request.endpoint))

        else:
            flash('Je hebt nog geen barcode gescanned', 'danger')

    return render_template('scanorder.html', title='Activiteit ophalen', form=form)

@app.route('/zxing', methods=['GET', 'POST'])
def zxing():
    form = GetForm()
    if request.method == 'POST':
        if request.form.get('zxing-input') != '':
            try:
                act = get_activity(request.form.get("zxing-input"), session['token'])
            except KeyError:
                flash('Je bent nog niet ingelogd, graag even inloggen!', 'danger')
                return redirect(url_for('login', next=request.endpoint))
            if act[1] == 200:
                if act[0]['items']:
                    db.set(session['token'], json.dumps(act[0]))
                    db.expire(session['token'], 600)
                    return redirect(url_for('order', predes='zxing'))
                else:
                    flash('De ingevoerde order kon niet worden gevonden', 'danger')
                    return redirect(url_for('zxing'))
            if act[1] == 403:
                flash('Je sessie is verlopen, graag opnieuw inloggen!', 'danger')
                return redirect(url_for('login', next=request.endpoint))

        else:
            flash('Je hebt nog geen barcode gescanned', 'danger')

    return render_template('zxing.html', title='Activiteit ophalen', form=form)

@app.route('/zxingenv', methods=['GET', 'POST'])
def zxingenv():
    form = GetForm()
    if request.method == 'POST':
        if request.form.get('zxing-input') != '':
            try:
                act = get_activity(request.form.get("zxing-input"), session['token'])
            except KeyError:
                flash('Je bent nog niet ingelogd, graag even inloggen!', 'danger')
                return redirect(url_for('login', next=request.endpoint))
            if act[1] == 200:
                if act[0]['items']:
                    db.set(session['token'], json.dumps(act[0]))
                    db.expire(session['token'], 600)
                    return redirect(url_for('order', predes='zxingenv'))
                else:
                    flash('De ingevoerde order kon niet worden gevonden', 'danger')
                    return redirect(url_for('zxingenv'))
            if act[1] == 403:
                flash('Je sessie is verlopen, graag opnieuw inloggen!', 'danger')
                return redirect(url_for('login', next=request.endpoint))

        else:
            flash('Je hebt nog geen barcode gescanned', 'danger')

    return render_template('zxingenv.html', title='Activiteit ophalen', form=form)

@app.route('/order/<predes>', methods=['GET', 'POST'])
def order(predes):
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
    session['servicelevel'] = servicelevel(order_dict['tags'], "tag_type_name", ['Overalinhuis', 'Gebruiksklaar', 'Project'])

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
                session['update_dict']['package_lines'][(session['str_package_lines_descriptions'].index(i))]['description'] = '[' + str(request.form.get(i)) + ' ' + session['initials'] + ' '  + str(date.today().strftime("%d%m")) + ']' + session['update_dict']['package_lines'][(session['str_package_lines_descriptions'].index(i))]['description']
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
                return redirect(url_for(predes))
            else:
                redirect(url_for('error'))

    return render_template('order.html', title='Order', form=form)
