from app import db
from math import floor

from sqlalchemy import ForeignKey


class Loan(db.Model):
    __tablename__ = 'loan'

    id = db.Column(db.String(), primary_key=True)
    amount = db.Column(db.Integer(), nullable=False)
    term = db.Column(db.Integer(), nullable=False)
    rate = db.Column(db.Numeric(precision=3, scale=2), nullable=False)
    date = db.Column(db.DateTime(timezone=True), nullable=False)

    def __init__(self, id, amount, term, rate, date):
        self.id = id
        self.amount = amount
        self.term = term
        self.rate = rate
        self.date = date

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Loan.query.all()

    @staticmethod
    def calculate_loan_payment(rate, term, amount):
        monthly_rate = rate / 12
        return Loan.__floor_decimal((monthly_rate + (monthly_rate / (((1 + monthly_rate) ** term) - 1))) * amount)

    @staticmethod
    def get_loan(loan_id):
        return Loan.query.get(loan_id)

    @staticmethod
    def __floor_decimal(value):
        return floor(value * 100) / 100


class Payment(db.Model):
    __tablename__ = 'payment'

    id = db.Column(db.String(), primary_key=True)
    loan_id = db.Column(db.String(), ForeignKey("loan.id"), nullable=False)
    payment = db.Column(db.String(length=15), nullable=False)
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    amount = db.Column(db.Numeric(scale=2), nullable=False)

    def __init__(self, id, loan_id, payment, date, amount):
        self.id = id
        self.loan_id = loan_id
        self.payment = payment
        self.date = date
        self.amount = amount

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Payment.query.all()

    @staticmethod
    def get_loan_payments(loan_id):
        return Payment.query.filter_by(loan_id=loan_id).order_by(Payment.date).all()
