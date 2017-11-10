from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Car, User

engine = create_engine('sqlite:///usedcars.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/<string:category>/JSON')
def categoryJSON(category):
    cars = session.query(Car).filter_by(category=category).all()
    return jsonify(Cars=[i.serialize for i in cars])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
