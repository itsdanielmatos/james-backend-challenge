import unittest
import json
from app import create_app, db


class LoanTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

        with self.app.app_context():
            db.create_all()

    def test_loan_creation(self):
        correct_loan = {"amount": 1000, "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        res = self.client().post('/loans/', data=json.dumps(correct_loan), content_type='application/json')
        self.assertEqual(res.status_code, 201)

    def test_loan_error_creation(self):
        incorrect_loan = {"amount": "1000", "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        res = self.client().post('/loans/', data=json.dumps(incorrect_loan), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

if __name__ == "__main__":
    unittest.main()
