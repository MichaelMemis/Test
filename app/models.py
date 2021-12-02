from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    reviews = db.relationship('Review', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    rating = db.Column(db.Integer)
    description = db.Column(db.String(128), index=True)
    location = db.Column(db.String(128), index=True, unique=True)
    r2ds = db.relationship('RestaurantToDish', backref='restaurant', lazy='dynamic')
    reviews = db.relationship('Review', backref='restaurant', lazy='dynamic')

    def __repr__(self):
        return '<Restaurant {}>'.format(self.name)


class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    rating = db.Column(db.Integer)
    price = db.Column(db.Float)
    description = db.Column(db.String(128), index=True)
    r2ds = db.relationship('RestaurantToDish', backref='dish', lazy='dynamic')
    reviews = db.relationship('Review', backref='dish', lazy='dynamic')

    def __repr__(self):
        return '<Dish {}>'.format(self.name)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    rating = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    restaurantID = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    dishID = db.Column(db.Integer, db.ForeignKey('dish.id'))

    def __repr__(self):
        return '<Review {}>'.format(self.body)


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reviewID = db.Column(db.Integer, db.ForeignKey('review.id'))

    def __repr__(self):
        return '<Vote {}>'.format(self.body)


class RestaurantToDish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurantID = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    dishID = db.Column(db.Integer, db.ForeignKey('dish.id'))

    def __repr__(self):
        return '<Restaurant To Dish {}{}>'.format(self.restaurantID, self.dishID)

