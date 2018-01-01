import os
import hashlib
import uuid
import random
import string
import httplib2
import json
import requests
import calendar
import time
from flask import (Flask, render_template, request, redirect, jsonify, url_for,
                   flash, make_response)
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from database_setup import Base, Car, User


app = Flask(__name__)

CLIENT_ID = json.loads(open('g_client_secrets.json', 'r').read())[
    'web']['client_id']
APPLICATION_NAME = "Udacity Backend Project"
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

engine = create_engine('sqlite:///usedcars.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def format_currency(value):
    '''Formats a number with thousands separator and currency ($)
    prefix.
    '''
    return "${:,}".format(value)


def format_number(value):
    '''Formats numbers with thousands separator.'''
    return "{:,}".format(value)


app.jinja_env.globals.update(format_currency=format_currency)
app.jinja_env.globals.update(format_number=format_number)


@app.route('/login')
def show_login():
    '''Generates a random uppercase alphanumeric string, 32 characters
    in length to prevent cross-site request forgery.
    '''
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


def create_user(login_session):
    '''Creates a new User object upon login and commits it to the User table.
    Returns the respective user id.
    '''
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    '''Returns the resulting user object from a query filtered on user
    id
    '''
    user = session.query(User).filter_by(id=user.id).one()
    return user


def get_user_id(email):
    '''Queries user id associated with a given email address. Returns
    None if user does not exist.
    '''
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('g_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the inteded user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    # Check if user already logged in.
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info.
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['email'] = data['email']

    if get_user_id(login_session['email']) is None:
        login_session['user_id'] = create_user(login_session)
    else:
        login_session['user_id'] = get_user_id(login_session['email'])

    output = '<h1>Welcome, ' + login_session['username'] + '!</h1>'
    flash("You are now logged in as %s" % login_session['username'], 'success')
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('show_main_page'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type='
           'fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    # Due to the formatting for the result from the server token
    # exchange we have to split the token first on commas and select the
    # first index which gives us the key : value for the server access
    # token. Then we split it on colons to pull out the actual token
    # value and replace the remaining quotes with nothing so that it can
    # be used directly in the graph api calls.
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = ('https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,'
           'email') % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session to properly logout
    login_session['access_token'] = token

    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'

    flash("Now logged in as %s" % login_session['username'], 'success')
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        del login_session['provider']

        flash("You have successfully logged out!", 'success')
        return redirect(url_for('show_main_page'))
    else:
        flash("You were not logged in", 'warning')
        return redirect(url_for('show_main_page'))


@app.route('/cars/<string:category>/JSON')
def category_json(category):
    cars = session.query(Car).filter_by(category=category).all()
    return jsonify(Cars=[i.serialize for i in cars])


@app.route('/cars/<string:category>/<int:car_id>/JSON')
def car_json(category, car_id):
    car = session.query(Car).filter_by(category=category, id=car_id).one()
    return jsonify(Car=car.serialize)


@app.route('/')
@app.route('/cars/')
def show_main_page():
    newest = session.query(Car).order_by(Car.id.desc()).limit(6).all()
    if 'username' not in login_session:
        return render_template('index.html', newest=newest)
    else:
        return render_template('index_loggedin.html', newest=newest)


@app.route('/cars/<string:category>/')
def read_category(category):
    print request.referrer
    cars = session.query(Car).filter_by(category=category).all()
    if 'username' not in login_session:
        return render_template('category.html', category=category, cars=cars)
    else:
        return render_template('category_loggedin.html', category=category,
                               cars=cars)


@app.route('/cars/<string:category>/<int:car_id>')
def read_car(category, car_id):
    car = session.query(Car).filter_by(category=category, id=car_id).one()
    if 'username' not in login_session:
        return render_template('car.html', car=car)
    else:
        user_id = get_user_id(login_session['email'])
        return render_template('car_loggedin.html', car=car, user_id=user_id)


@app.route('/my posts/')
@app.route('/cars/my posts/')
def my_posts():
    cars = session.query(Car).filter_by(user_id=login_session['user_id']).all()
    if 'username' not in login_session:
        return redirect(url_for('show_login'))
    else:
        return render_template('my_posts.html', cars=cars)


@app.route('/cars/create/', methods=['GET', 'POST'])
def create_car():
    if 'username' not in login_session:
        return redirect(url_for('show_login'))
    else:
        if request.method == 'POST':
            file = request.files['image']
            if len(file.filename) > 0:
                hashed_filename = hashlib.md5(
                    str(uuid.uuid4()) + file.filename).hexdigest()
                f = os.path.join(app.config['UPLOAD_FOLDER'], hashed_filename)
                file.save(f)
            else:
                hashed_filename = 'placeholder.png'
            newCar = Car(
                category=request.form['category'],
                year=request.form['year'],
                make=request.form['make'],
                model=request.form['model'],
                mileage=request.form['mileage'],
                price=request.form['price'],
                description=request.form['description'],
                image=hashed_filename,
                user_id=login_session['user_id'],
                dt_created=calendar.timegm(time.gmtime()))
            session.add(newCar)
            session.commit()

            car = session.query(Car).filter_by(
                user_id=login_session['user_id']).order_by(Car.dt_created.desc(
                )).first()
            flash_message = ("You successfully created a post for a %s %s %s!"
                             % (car.year, car.make, car.model))
            flash(flash_message, 'success')

            return redirect(url_for('read_car', category=car.category,
                                    car_id=car.id))
        else:
            return render_template('create.html')


@app.route('/cars/<string:category>/<int:car_id>/update/',
           methods=['GET', 'POST'])
def update_car(category, car_id):
    if 'username' not in login_session:
        return redirect(url_for('show_login'))
    else:

        edit_car = session.query(Car).filter_by(id=car_id).one()
        if login_session['user_id'] != edit_car.user_id:
            flash("You don't have authorization to update this post.",
                  'warning')
            return redirect(url_for('read_car', category=edit_car.category,
                                    car_id=edit_car.id))
        if request.method == 'POST':

            if request.files['image'].filename != '' > 0:
                file = request.files['image']
                hashed_filename = hashlib.md5(
                    str(uuid.uuid4()) + file.filename).hexdigest()
                f = os.path.join(app.config['UPLOAD_FOLDER'], hashed_filename)
                file.save(f)
            else:
                hashed_filename = edit_car.image
            edit_car.category = request.form['category']
            edit_car.year = request.form['year']
            edit_car.make = request.form['make']
            edit_car.model = request.form['model']
            edit_car.mileage = request.form['mileage']
            edit_car.price = request.form['price']
            edit_car.description = request.form['description']
            edit_car.image = hashed_filename
            edit_car.dt_modified = calendar.timegm(time.gmtime())
            session.add(edit_car)
            session.commit()
            flash_message = "You successfully updated your %s %s %s post." % (
                edit_car.year, edit_car.make, edit_car.model)
            flash(flash_message, 'success')

            return redirect(url_for('read_car', category=edit_car.category,
                                    car_id=edit_car.id))
        else:
            edit_car = session.query(Car).filter_by(id=car_id).one()
            return render_template('update.html', category=category,
                                   car_id=car_id, edit_car=edit_car)


@app.route('/cars/<string:category>/<int:car_id>/delete/',
           methods=['GET', 'POST'])
def delete_car(category, car_id):
    if 'username' not in login_session:
        return redirect(url_for('show_login'))
    else:
        delete_car = session.query(Car).filter_by(
            category=category, id=car_id).one()
        if login_session['user_id'] != delete_car.user_id:
            flash("You don't have authorization to delete this post.",
                  'warning')
            return redirect(url_for('read_car', category=delete_car.category,
                                    car_id=delete_car.id))
        if request.method == 'POST':

            session.delete(delete_car)
            session.commit()
            flash_message = "You successfully deleted your %s %s %s post." % (
                delete_car.year, delete_car.make, delete_car.model)
            flash(flash_message, 'success')
            return redirect(url_for('show_main_page'))
        else:
            delete_car = session.query(Car).filter_by(
                category=category, id=car_id).one()
            return render_template('delete.html', category=delete_car.category,
                                   car_id=delete_car.id, delete_car=delete_car)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
