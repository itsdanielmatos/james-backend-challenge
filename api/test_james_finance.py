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
        res = self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        first_loan = self.getJSON(res)
        self.assertEqual(res.status_code, 201)
        res = self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        second_loan = self.getJSON(res)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(first_loan["loan_id"] != second_loan["loan_id"], True)

    def test_loan_schema(self):
        incorrect_loan = {"amount": "1000", "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        res = self.client().post('/loans', data=json.dumps(incorrect_loan), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_loan_date(self):
        incorrect_loan = {"amount": "1000", "term": 12, "rate": 0.05, "date": "2018"}
        res = self.client().post('/loans', data=json.dumps(incorrect_loan), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_payment_creation(self):
        correct_loan = {"amount": 1000, "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        res = self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        loan = self.getJSON(res)
        correct_payment = {"payment": "made", "amount": 85.60, "date": "2017-08-05 01:18Z"}
        res = self.client().post('/loans/{}/payments'.format(loan["loan_id"]), data=json.dumps(correct_payment),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 201)

    def test_payment_schema(self):
        correct_loan = {"amount": 1000, "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        res = self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        loan = self.getJSON(res)
        incorrect_payment = {"payment": "reject", "amount": 85.60, "date": "2017-08-05 01:18Z"}
        res = self.client().post('/loans/{}/payments'.format(loan["loan_id"]), data=json.dumps(incorrect_payment),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_payment_invalid_loan_id_format(self):
        correct_payment = {"payment": "missed", "amount": 85.60, "date": "2017-08-05 01:18Z"}
        res = self.client().post('/loans/{}/payments'.format("0000"), data=json.dumps(correct_payment),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_payment_unavailable_loan(self):
        correct_payment = {"payment": "missed", "amount": 85.60, "date": "2017-08-05 01:18Z"}
        res = self.client().post('/loans/{}/payments'.format("00000000-0000-0000-0000-000000000000"),
                                 data=json.dumps(correct_payment),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_payment_wrong_amount(self):
        correct_loan = {"amount": 1000, "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        res = self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        loan = self.getJSON(res)
        incorrect_payment = {"payment": "made", "amount": 10.00, "date": "2017-08-05 01:18Z"}
        res = self.client().post('/loans/{}/payments'.format(loan["loan_id"]), data=json.dumps(incorrect_payment),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_payment_fulfillment(self):
        correct_loan = {"amount": 1000, "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        res = self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        loan = self.getJSON(res)
        correct_payment = {"payment": "made", "amount": 85.60, "date": "2018-09-01 01:18Z"}
        for n in range(1, 13):
            correct_payment = {"payment": "made", "amount": 85.60, "date": "2017-0{}-05 01:18Z".format(n)}
            self.client().post('/loans/{}/payments'.format(loan["loan_id"]), data=json.dumps(correct_payment),
                               content_type='application/json')
        res = self.client().post('/loans/{}/payments'.format(loan["loan_id"]), data=json.dumps(correct_payment),
                                 content_type='application/json')
        print(res.data)
        self.assertEqual(res.status_code, 409)

    def test_payment_twice(self):
        correct_loan = {"amount": 1000, "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        res = self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        loan = self.getJSON(res)
        correct_payment = {"payment": "made", "amount": 85.60, "date": "2017-08-05 10:18Z"}
        self.client().post('/loans/{}/payments'.format(loan["loan_id"]), data=json.dumps(correct_payment),
                           content_type='application/json')
        correct_payment = {"payment": "made", "amount": 85.60, "date": "2017-08-05 10:18Z"}
        res = self.client().post('/loans/{}/payments'.format(loan["loan_id"]), data=json.dumps(correct_payment),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 409)

    def test_payment_wrong_date(self):
        correct_loan = {"amount": 1000, "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        res = self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        loan = self.getJSON(res)
        incorrect_payment = {"payment": "made", "amount": 85.60, "date": "2009"}
        res = self.client().post('/loans/{}/payments'.format(loan["loan_id"]), data=json.dumps(incorrect_payment),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_balance_get(self):
        correct_loan = {"amount": 1000, "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        res = self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        json_result = self.getJSON(res)
        correct_payment = {"payment": "made", "amount": 85.60, "date": "2017-08-05 01:18Z"}
        self.client().post('/loans/{}/payments'.format(json_result["loan_id"]),
                           data=json.dumps(correct_payment),
                           content_type='application/json')
        res = self.client().get('/loans/{}/balance?date=2017-09-05'.format(json_result["loan_id"]))
        json_result = self.getJSON(res)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_result["balance"], 1000 - 85.60)

    def test_balance_invalid_loan_id_format(self):
        correct_loan = {"amount": 1000, "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        res = self.client().get('/loans/{}/balance?date=2017-09-05'.format("00000"))
        self.assertEqual(res.status_code, 400)

    def test_balance_unavailable_loan(self):
        correct_loan = {"amount": 1000, "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        res = self.client().get('/loans/{}/balance?date=2017-09-05'.format("00000000-0000-0000-0000-000000000000"))
        self.assertEqual(res.status_code, 400)

    def test_balance_invalid_number_of_arguments(self):
        correct_loan = {"amount": 1000, "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        res = self.client().get(
            '/loans/{}/balance?date=2017-09-05&limit=3'.format("00000000-0000-0000-0000-000000000000"))
        self.assertEqual(res.status_code, 400)

    def test_balance_invalid_query_parameter(self):
        correct_loan = {"amount": 1000, "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        res = self.client().get(
            '/loans/{}/balance?limit=2017-09-05'.format("00000000-0000-0000-0000-000000000000"))
        self.assertEqual(res.status_code, 400)

    def test_balance_invalid_data(self):
        correct_loan = {"amount": 1000, "term": 12, "rate": 0.05, "date": "2017-08-05 02:18Z"}
        self.client().post('/loans', data=json.dumps(correct_loan), content_type='application/json')
        res = self.client().get(
            '/loans/{}/balance?date=2017'.format("00000000-0000-0000-0000-000000000000"))
        self.assertEqual(res.status_code, 400)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @staticmethod
    def getJSON(response):
        return json.loads(response.data.decode('utf-8').replace("'", '"'))


if __name__ == "__main__":
    unittest.main()
