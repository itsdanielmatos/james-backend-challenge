from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
from instance.config import app_config
from schemas.schemas import schemas
from jsonschema import validate, ValidationError

# Initialize SQL-ALCHEMY
db = SQLAlchemy()


def create_app(config_name):
    from app.models import Loan

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/loans/', methods=['POST'])
    def loans():

        request_data = request.get_json()

        try:
            validate(request_data, schemas["loan"])
        except ValidationError as validation_error:
            response = jsonify({"error": validation_error.message})
            response.status_code = 400
            return response

        amount = request_data["amount"]
        term = request_data["term"]
        rate = request_data["rate"]
        date = request_data["date"]

        loan = Loan(amount=amount, term=term, rate=rate, date=date)
        loan.save()

        response = jsonify({"loan_id": loan.id, "installment": Loan.calculate_loan_payment(rate, term, amount)})
        response.status_code = 201

        return response

    """
        Validate <loan_id> with the following regex expression:
        [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}
    """

    @app.route('/loans/<loan_id>/payments', methods=['POST'])
    def payments(loan_id):
        """
            Verify if the amount is a multiple of the monthly installment
        """
        return

    @app.route('/loans/<loan_id>/balance', methods=['POST'])
    def balance(loan_id):

        return

    return app