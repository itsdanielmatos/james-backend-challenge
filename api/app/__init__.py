from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort
from instance.config import app_config
from schemas.schemas import schemas
from jsonschema import validate, ValidationError
from dateutil import relativedelta
import uuid
import datetime
import pytz
import ciso8601
import re

# Initialize SQL-ALCHEMY
db = SQLAlchemy()


def create_app(config_name):
    from app.models import Loan, Payment

    loan_id_re = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.before_request
    def require_json():
        if not request.is_json and request.method != "GET":
            abort(415)

    @app.errorhandler(415)
    def handle_unsupported_media_type():
        return generate_error_message("Unsupported Media Type", 415)

    @app.route('/loans', methods=['POST'])
    def loans():

        request_data = request.get_json()

        try:
            validate(request_data, schemas["loan"])
        except ValidationError as validation_error:
            return generate_error_message(validation_error.message, 400)

        date = ciso8601.parse_datetime(request_data["date"])

        if date is None:
            return generate_error_message("Specified date doesn't follow the ISO8601 norm", 400)

        amount = request_data["amount"]
        term = request_data["term"]
        rate = request_data["rate"]

        loan = Loan(id=str(uuid.uuid4()), amount=amount, term=term, rate=rate, date=date)
        loan.save()

        response = jsonify({"loan_id": loan.id, "installment": Loan.calculate_loan_payment(rate, term, amount)})
        response.status_code = 201

        return response

    @app.route('/loans/<loan_id>/payments', methods=['POST'])
    def payments(loan_id):
        request_data = request.get_json()

        if re.match(loan_id_re, loan_id) is None:
            response = jsonify({"error": "Specified loan id is not valid"})
            response.status_code = 400
            return response

        try:
            validate(request_data, schemas["payment"])
        except ValidationError as validation_error:
            return generate_error_message(validation_error.message, 400)

        date = ciso8601.parse_datetime(request_data["date"])

        if date is None:
            return generate_error_message("Specified date doesn't follow the ISO8601 norm", 400)

        if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
            date = date.replace(tzinfo=pytz.UTC)

        db_loan = Loan.get_loan(loan_id)

        if db_loan is None:
            return generate_error_message("Specified loan id doesn't exist", 400)

        db_loan_installment = Loan.calculate_loan_payment(db_loan.rate, db_loan.term, db_loan.amount)

        if request_data["amount"] != db_loan_installment:
            return generate_error_message(
                "Specified amount is not equal to monthly installment of {}".format(db_loan_installment), 400)

        db_loan_payments = Payment.get_loan_payments(loan_id)

        if len(db_loan_payments) != 0:
            made_payments = []

            for payment in db_loan_payments:
                if payment.payment == "made":
                    made_payments.append(payment)

            if len(made_payments) == db_loan.term:
                return generate_error_message("This loan has already been paid", 409)

            db_loan_last_payment = db_loan_payments[-1]
            months = relativedelta.relativedelta(date, db_loan_last_payment.date).months
            if abs(months) < 1:
                return generate_error_message(
                    "Payments work in a monthly base. Since last payment {} one month hasn't passed".format(
                        db_loan_last_payment.date), 409)

        request_data = request.get_json()

        payment = request_data["payment"]
        amount = request_data["amount"]
        payment = Payment(id=str(uuid.uuid4()), loan_id=loan_id, payment=payment, date=date, amount=amount)
        payment.save()

        response = jsonify({"message": "Payment successful"})
        response.status_code = 201
        return response

    @app.route('/loans/<loan_id>/balance', methods=['GET'])
    def balance(loan_id):
        if re.match(loan_id_re, loan_id) is None:
            response = jsonify({"error": "Specified loan id is not valid"})
            response.status_code = 400
            return response

        if len(request.args) != 1:
            return generate_error_message("Invalid number of arguments", 400)

        date = request.args.get('date')

        if date is None:
            return generate_error_message("Invalid query parameter", 400)

        transformed_date = ciso8601.parse_datetime(date)

        if transformed_date is None:
            return generate_error_message("Specified date doesn't follow the ISO8601 norm", 400)

        if transformed_date.tzinfo is None or transformed_date.tzinfo.utcoffset(transformed_date) is None:
            transformed_date = transformed_date.replace(tzinfo=pytz.UTC)

        db_loan = Loan.get_loan(loan_id)

        if db_loan is None:
            return generate_error_message("Specified loan id doesn't exist", 400)

        total_to_pay = db_loan.amount

        db_loan_payments = Payment.get_loan_payments(loan_id)

        for payment in db_loan_payments:
            if payment.payment == "made" and payment.date <= transformed_date:
                total_to_pay -= payment.amount

        response = jsonify({"balance": float(round(total_to_pay, 2))})
        response.status_code = 200
        return response

    def generate_error_message(error_message, status_code):
        response = jsonify({"error": error_message})
        response.status_code = status_code
        return response

    return app
