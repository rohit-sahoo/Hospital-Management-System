from HospitalSystem import db, login_manager
from sqlalchemy import Column, Integer, DateTime, Boolean, String, ForeignKey, Float, Date
from flask_login import UserMixin

ROOM_TYPE = {
    "GE": "GENERAL",
    "SE": "SEMI",
    "SI": "SINGLE"
}

PATIENT_STATUS = {
    "A": "ADMIT",
    "D": "DISCHARGE",
}

USER_TYPE = {
    "p": "pharmacist",
    "r": "receptionist",
    "d": "diagnostic"
}

# @login_manager.user_loader
@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))

# model which stores information require for login


class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    is_pharmacist = db.Column(db.Boolean(), default=False)
    is_diagnostic = db.Column(db.Boolean(), default=False)

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'is_pharmacist': self.is_pharmacist,
            'is_diagnostic': self.is_diagnostic
        }

# model for patient


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ssn = db.Column(db.Integer, unique=True, nullable=False)
    pat_id = db.Column(db.Integer, unique=True, nullable=False)
    pat_name = db.Column(db.String(80), nullable=False)
    adrs = db.Column(db.String(256), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    doj = db.Column(db.Date, nullable=False)
    rtype = db.Column(db.String(256), default=ROOM_TYPE['GE'])
    status = db.Column(db.String(256), default=PATIENT_STATUS['A'])
    amt = db.Column(db.Integer, default=0)

    def serialize(self):
        return {
            'SSN': self.ssn,
            'Patient ID': self.pat_id,
            'Name': self.pat_name,
            'address': self.adrs,
            'age': self.age,
            'doj': str(self.doj),
            'room type': self.rtype,
            'status': self.status
        }

# model which stores price of medicine


class Med(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    med_name = db.Column(db.String(80), nullable=False)
    med_qty = db.Column(db.Integer, nullable=False)
    med_price = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'med_name': self.med_name,
            'med_qty': self.med_qty,
            'med_price': self.med_price,
        }

# model for associating medicine to patient


class Medicines(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pat_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    med_id = db.Column(db.Integer, db.ForeignKey('med.id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'pat_id': self.pat_id,
            'med_id': self.med_id,
            'qty': self.qty
        }


class Diag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diagn = db.Column(db.String(256), nullable=False)
    diagn_price = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'diagn': self.diagn,
            'diagn_price': self.diagn_price,
        }


class Diagnostics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pat_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    diagn_id = db.Column(db.Integer, db.ForeignKey('diag.id'), nullable=False)

    def serialize(self):
        return{
            'pat_id': self.pat_id,
            'diagn_id': self.diagn_id
        }
