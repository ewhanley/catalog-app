from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)


class Car(Base):
    __tablename__ = 'car'

    category = Column(String(80), nullable=False)
    year = Column(Integer, nullable=False)
    make = Column(String(80), nullable=False)
    model = Column(String(80), nullable=False)
    mileage = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    image = Column(String(32))
    user_id = Column(Integer, ForeignKey('user.id'))
    dt_created = Column(Integer, nullable=False)
    dt_modified = Column(Integer)
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'category': self.category,
            'year': self.year,
            'make': self.make,
            'model': self.model,
            'mileage': self.mileage,
            'price': self.price,
            'description': self.description,
            'id': self.id,
            'user_id': self.user_id,
            'image': self.image,
            'date_created': self.dt_created,
            'date_modified': self.dt_modified
        }


engine = create_engine('sqlite:///usedcars.db')


Base.metadata.create_all(engine)
