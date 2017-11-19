from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Car, User

engine = create_engine('sqlite:///usedcars.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


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
    return render_template('index.html')


@app.route('/cars/<string:category>/')
def readCategory(category):
    return render_template('category.html')


@app.route('/cars/<string:category>/<int:car_id>')
def readCar(category, car_id):
    car = session.query(Car).filter_by(category=category, id=car_id).one()
    return render_template('car.html')


@app.route('/cars/create/', methods=['GET', 'POST'])
def createCar():
    return 'You can create a new car here!'


@app.route('/cars/<string:category>/<int:car_id>/update/', methods=['GET', 'POST'])
def updateCar(category, car_id):
    return 'You can edit a car here!'


@app.route('/cars/<string:category>/<int:car_id>/delete/', methods=['GET', 'POST'])
def deleteCar(category, car_id):
    return 'You can delete a car here!'


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
