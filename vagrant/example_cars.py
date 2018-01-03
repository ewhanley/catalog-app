import os
import shutil
import hashlib
import uuid
import random
import calendar
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Car, Base, User

engine = create_engine('sqlite:///usedcars.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# List of dummy users
names = ('Sharky McStevenson', 'Robert Smith', 'Jane Doe', 'John Public')
users = []
for name in names:
    email = name.replace(" ", ".") + '@example.com'
    users.append(tuple((name, email)))


categories = []
categories += ['Coupe'] * 5
categories += ['Hatchback'] * 3
categories += ['Pickup'] * 5
categories += ['Sedan'] * 3
categories += ['SUV'] * 3
categories += ['Van']
categories += ['Wagon'] * 2

makes = ['BMW', 'Chevrolet', 'Jaguar', 'Mercedes', 'Ford', 'Fiat', 'Subary',
         'VW', 'Chevrolet', 'Chevrolet', 'Dodge', 'Dodge', 'Nissan', 'BMW',
         'Renault', 'Saab', 'Jeep', 'Jeep', 'Toyota', 'VW', 'Audi', 'Volvo']

models = ['M3', 'Camaro', 'XK', 'C500', 'Mustang', '500', 'Outback', 'Golf',
          'Apache', 'C10', 'Ram 2500', 'Ram 1500', 'Navara', 'E6', 'Car', '920',
          'Grand Cherokee', 'Wrangler', 'FJ40', 'Westfalia', 'A5', '1300']


description = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
              do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
              enim ad minim veniam, quis nostrud exercitation ullamco laboris
              nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
              reprehenderit in voluptate velit esse cillum dolore eu fugiat
              nulla pariatur. Excepteur sint occaecat cupidatat non proident,
              sunt in culpa qui officia deserunt mollit anim id est laborum.'''


images = ('coupe_bmw.jpg', 'coupe_camaro.jpg', 'coupe_jaguar.jpg',
          'coupe_mercedes.jpg', 'coupe_mustang.jpg', 'hb_fiat.jpg',
          'hb_subaru.jpg', 'hb_vw.jpg', 'pu_chevrolet.jpg',
          'pu_chevrolet2.jpg', 'pu_dodge.jpg', 'pu_dodge2.jpg',
          'pu_nissan.jpg', 'sed_bmw.jpg', 'sed_renault.jpg', 'sed_saab.jpg',
          'suv_jeep.jpg', 'suv_jeep2.jpg', 'suv_toyota.jpg', 'van_vw.jpg',
          'wg_audi.jpg', 'wg_volvo.jpg')

src_dir = 'example_images'
dst_dir = 'static/uploads'

print "Populating database with example records."
print "Creating dummy users"
# Create dummy users
for user in users:
    new_user = User(name=user[0], email=user[1])
    session.add(new_user)
    session.commit()
    print ('Added dummy user: %s!' % new_user.name)

print "Creating dummy cars"
# Create dummy cars
for i in range(0, len(categories)):
    src_filename = images[i]
    src_file = os.path.join(src_dir, src_filename)
    dst_file = os.path.join(dst_dir, src_filename)
    shutil.copy(src_file, dst_dir)
    hashed_filename = hashlib.md5(str(uuid.uuid4()) + src_filename).hexdigest()
    dst_renamed = os.path.join(dst_dir, hashed_filename)
    os.rename(dst_file, dst_renamed)
    new_car = Car(
        category=categories[i],
        year=random.randint(1900, 2015),
        make=makes[i],
        model=models[i],
        mileage=random.randint(1, 500000),
        price=random.randint(500, 80000),
        description=description,
        image=hashed_filename,
        user_id=random.randint(1, 4),
        dt_created=calendar.timegm(time.gmtime()))
    session.add(new_car)
    session.commit()
    print ('Added %s %s %s!' % (new_car.year, new_car.make, new_car.model))
