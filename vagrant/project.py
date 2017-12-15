from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Car, User

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
    newest = session.query(Car).order_by(Car.id.desc()).limit(3).all()
    return render_template('index.html', newest=newest)


@app.route('/cars/<string:category>/')
def readCategory(category):
    cars = session.query(Car).filter_by(category=category).all()
    return render_template('category.html', category=category, cars=cars)


@app.route('/cars/<string:category>/<int:car_id>')
def readCar(category, car_id):
    car = session.query(Car).filter_by(category=category, id=car_id).one()
    return render_template('car.html', car=car)


@app.route('/cars/create/', methods=['GET', 'POST'])
def createCar():
    if request.method == 'POST':
        newCar = Car(
            category=request.form['category'],
            year=request.form['year'],
            make=request.form['make'],
            model=request.form['model'],
            mileage=request.form['mileage'],
            price=request.form['price'],
            description=request.form['description'])
        session.add(newCar)
        session.commit()
        return redirect(url_for('showMainPage'))
    else:
        return render_template('create.html')


@app.route('/cars/<string:category>/<int:car_id>/update/', methods=['GET', 'POST'])
def updateCar(category, car_id):
    if request.method == 'POST':
        editCar = session.query(Car).filter_by(id=car_id).one()
        editCar.category = request.form['category']
        editCar.year = request.form['year']
        editCar.make = request.form['make']
        editCar.model = request.form['model']
        editCar.mileage = request.form['mileage']
        editCar.price = request.form['price']
        description = request.form['description']
        session.add(editCar)
        session.commit()
        return redirect(url_for('readCar', category=editCar.category, car_id=editCar.id))
    else:
        editCar = session.query(Car).filter_by(id=car_id).one()
        return render_template('update.html', category=category, car_id=car_id, editCar=editCar)


@app.route('/cars/<string:category>/<int:car_id>/delete/', methods=['GET', 'POST'])
def deleteCar(category, car_id):
    return 'You can delete a car here!'


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
