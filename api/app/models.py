from app import db
from math import floor
import uuid


class Loan(db.Model):
    __tablename__ = 'loan'

    id = db.Column(db.String(), primary_key=True, default=str(uuid.uuid1()))
    amount = db.Column(db.Integer(), nullable=False)
    term = db.Column(db.Integer(), nullable=False)
    rate = db.Column(db.Numeric(precision=3, scale=2), nullable=False)
    date = db.Column(db.DateTime(timezone=True), nullable=False)

    def __init__(self, amount, term, rate, date):
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
    def __floor_decimal(value):
        return floor(value * 100) / 100
