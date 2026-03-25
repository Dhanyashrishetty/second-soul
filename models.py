from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)

class NGO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    registration_number = db.Column(db.String(50), nullable=True)
    owner_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    qr_code_filename = db.Column(db.String(200), nullable=True)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    skills = db.Column(db.String(200), nullable=True)
    availability = db.Column(db.String(100), nullable=True)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False) # 'money' or 'item'
    amount = db.Column(db.Float, nullable=True)
    item_name = db.Column(db.String(100), nullable=True)
    item_image_filename = db.Column(db.String(200), nullable=True)
    ngo_id = db.Column(db.Integer, db.ForeignKey('ngo.id'), nullable=True)
    ngo = db.relationship('NGO', backref=db.backref('donations', lazy=True))
    donor_name = db.Column(db.String(100), nullable=True)
    donor_email = db.Column(db.String(120), nullable=True)
    donor_phone = db.Column(db.String(20), nullable=True)
    date_donated = db.Column(db.DateTime, default=datetime.utcnow)
