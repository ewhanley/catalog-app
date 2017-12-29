from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
import os
import hashlib
import uuid
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Car, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import calendar
import time

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
APPLICATION_NAME = "Udacity Backend Project"


UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

engine = create_engine('sqlite:///usedcars.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def format_currency(value):
    return "${:,}".format(value)


def format_number(value):
    return "{:,}".format(value)


app.jinja_env.globals.update(format_currency=format_currency)
app.jinja_env.globals.update(format_number=format_number)

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


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
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    print access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the inteded user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    if getUserID(login_session['email']) is None:
        login_session['user_id'] = createUser(login_session)
    else:
        login_session['user_id'] = getUserID(login_session['email'])

    print login_session['user_id']

    output = '<h1>Welcome, ' + login_session['username'] + '!</h1>'
    flash("You are now logged in as %s" % login_session['username'], 'success')
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("You have successfully logged out!", 'success')
        return redirect(url_for('showMainPage'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user.id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/cars/<string:category>/JSON')
def categoryJSON(category):
    cars = session.query(Car).filter_by(category=category).all()
    return jsonify(Cars=[i.serialize for i in cars])


@app.route('/cars/<string:category>/<int:car_id>/JSON')
def carJSON(category, car_id):
    car = session.query(Car).filter_by(category=category, id=car_id).one()
    return jsonify(Car=car.serialize)


@app.route('/')
@app.route('/cars/')
def showMainPage():
    newest = session.query(Car).order_by(Car.id.desc()).limit(6).all()
    if 'username' not in login_session:
        return render_template('index.html', newest=newest)
    else:
        return render_template('index_loggedin.html', newest=newest)


@app.route('/cars/<string:category>/')
def readCategory(category):
    print request.referrer
    cars = session.query(Car).filter_by(category=category).all()
    if 'username' not in login_session:
        return render_template('category.html', category=category, cars=cars)
    else:
        return render_template('category_loggedin.html', category=category, cars=cars)


@app.route('/cars/<string:category>/<int:car_id>')
def readCar(category, car_id):
    car = session.query(Car).filter_by(category=category, id=car_id).one()
    if 'username' not in login_session:
        return render_template('car.html', car=car)
    else:
        user_id = getUserID(login_session['email'])
        return render_template('car_loggedin.html', car=car, user_id=user_id)


@app.route('/cars/create/', methods=['GET', 'POST'])
def createCar():
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    else:
        if request.method == 'POST':
            file = request.files['image']
            if len(file.filename) > 0:
                hashedFilename = hashlib.md5(
                    str(uuid.uuid4()) + file.filename).hexdigest()
                f = os.path.join(app.config['UPLOAD_FOLDER'], hashedFilename)
                file.save(f)
            else:
                hashedFilename = 'placeholder.png'
            newCar = Car(
                category=request.form['category'],
                year=request.form['year'],
                make=request.form['make'],
                model=request.form['model'],
                mileage=request.form['mileage'],
                price=request.form['price'],
                description=request.form['description'],
                image=hashedFilename,
                user_id=login_session['user_id'],
                dt_created=calendar.timegm(time.gmtime()))
            session.add(newCar)
            session.commit()

            car = session.query(Car).filter_by(
                user_id=login_session['user_id']).order_by(Car.dt_created.desc()).first()
            flash_message = "You successfully a post for a %s %s %s!" % (
                car.year, car.make, car.model)
            flash(flash_message, 'success')

            return redirect(url_for('readCar', category=car.category, car_id=car.id))
        else:
            return render_template('create.html')


@app.route('/cars/<string:category>/<int:car_id>/update/', methods=['GET', 'POST'])
def updateCar(category, car_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    else:

        editCar = session.query(Car).filter_by(id=car_id).one()
        if login_session['user_id'] != editCar.user_id:
            flash("You don't have authorization to update this post.", 'warning')
            return redirect(url_for('readCar', category=editCar.category,
                                    car_id=editCar.id))
        if request.method == 'POST':

            if request.files['image'].filename != '' > 0:
                file = request.files['image']
                hashedFilename = hashlib.md5(
                    str(uuid.uuid4()) + file.filename).hexdigest()
                f = os.path.join(app.config['UPLOAD_FOLDER'], hashedFilename)
                file.save(f)
            else:
                hashedFilename = editCar.image
            editCar.category = request.form['category']
            editCar.year = request.form['year']
            editCar.make = request.form['make']
            editCar.model = request.form['model']
            editCar.mileage = request.form['mileage']
            editCar.price = request.form['price']
            editCar.description = request.form['description']
            editCar.image = hashedFilename
            editCar.dt_modified = calendar.timegm(time.gmtime())
            session.add(editCar)
            session.commit()
            flash_message = "You successfully updated your %s %s %s post." % (
                editCar.year, editCar.make, editCar.model)
            flash(flash_message, 'success')

            return redirect(url_for('readCar', category=editCar.category, car_id=editCar.id))
        else:
            editCar = session.query(Car).filter_by(id=car_id).one()
            return render_template('update.html', category=category, car_id=car_id, editCar=editCar)


@app.route('/cars/<string:category>/<int:car_id>/delete/', methods=['GET', 'POST'])
def deleteCar(category, car_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    else:
        if request.method == 'POST':
            deleteCar = session.query(Car).filter_by(
                category=category, id=car_id).one()
            session.delete(deleteCar)
            session.commit()
            flash_message = "You successfully deleted your %s %s %s post." % (
                deleteCar.year, deleteCar.make, deleteCar.model)
            flash(flash_message, 'success')
            return redirect(url_for('showMainPage'))
        else:
            deleteCar = session.query(Car).filter_by(
                category=category, id=car_id).one()
            return render_template('delete.html', category=deleteCar.category, car_id=deleteCar.id, deleteCar=deleteCar)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
