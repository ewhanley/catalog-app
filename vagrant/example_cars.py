from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Car, Base, User

engine = create_engine('sqlite:///usedcars.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
User1 = User(name="John Doe", email="john.doe@example.com")
session.add(User1)
session.commit()

car1 = Car(user_id=1, category="SUV", year=2013, make="Jeep",
           model="Wrangler", mileage=98356, price=25000,
           description="Classic off-road machine")

session.add(car1)
session.commit()

car1 = Car(user_id=1, category="SUV", year=2016, make="Toyota",
           model="Landcruiser", mileage=16887, price=78000,
           description="Luxury sport utility vehicle")

session.add(car1)
session.commit()

car1 = Car(user_id=1, category="Pickup", year=1996, make="Ford",
           model="F-150", mileage=198765, price=2500,
           description="Beat up work truck")

session.add(car1)
session.commit()

car1 = Car(user_id=1, category="Wagon", year=2005, make="Volvo",
           model="XC70", mileage=176555, price=13500,
           description="Great winter vehicle")

session.add(car1)
session.commit()
print "added cars!"
