# Software Engineer Challenge

The objective of this challenge is to test your ability to implement a solution upon given an abstract problem.

We want you to develop an application through which a big bank can easily issue new loans and find out what the value and volume of outstanding debt are.

<b>Problem:</b>
- A big bank needs to keep track of the amount of money loaned out and the missed/made payments.
- A big bank needs a place to retrieve the volume of outstanding debt at some point in time.

<b>Limitations:</b>
- Loans are paid back in monthly installments.

<b>Considerations:</b>
- A loan can only be paid monthly, meaning that the payment date has to be superior by one month when compared with the last made payment date.
- The number of made payments can't be greater than the loan term.
- The payment amount has to be equal to the loan installment.

## Setup

In order to setup the docker container please follow the following steps:

- Clone the repo
```
$ git clone git@github.com:itsdanielmatos/james-backend-challenge.git
```

- Change to the repository folder
```
$ cd james-backend-challenge/
```
- Run execute.sh
```
$ ./execute.sh
```

After the execution of the execute.sh script the api is available on the specified endpoints.

## Testing

In order to test the api follow the following steps (Note: setup step has to be fulfilled):

- Get the docker container id
```
$ sudo docker ps -a
```
```
CONTAINER ID        IMAGE               COMMAND                  CREATED              STATUS                            PORTS                    NAMES
df611a242f0b        james_finance       "/bin/sh -c ./initia…"   About a minute ago   Up About a minute                 0.0.0.0:5000->5000/tcp   keen_varahamihira
```

- Run the tests
```
$ sudo docker exec -it df611a242f0b python test_james_finance.py
```

## Endpoints

### POST /loans

#### Summary

Creates a loan application. Loans are automatically accepted.

#### Payload
- amount: loan amount in dollars.
- term: number of months that will take until its gets paid-off.
- rate: interest rate as decimal.
- date: when a loan was asked (origination date as an ISO 8601 string).

###### Example
```
{
	"amount": 1000,
	"term": 12,
	"rate": 0.05,
	"date": "2017-08-05 02:18Z",
}
```

#### Reply

- loan_id: unique id of the loan.
- installment: monthly loan payment.

###### Example

```
{
	"loan_id": "000-0000-0000-0000",
	"installment": 85.60
}
```

#### Notes

##### Loan payment formula

```
r = rate / 12.
Installment (monthly) = [ r + r / ( (1+r) ^ term - 1) ] x amount
```

###### Example

<b>For repaying a loan of $1000 at 5% interest for 12 months, the equation would be:</b>
```
Installment (monthly) = [ (0.05 / 12) + (0.05 / 12) / ( (1+ (0.05 / 12)) ^ 12 -1) ] x 1000
Installment (monthly) = $85.60
```

### POST /loans/<:id>/payments

#### Summary

Creates a record of a payment `made` or `missed`.

#### Payload

- payment: type of payment: `made` or `missed`.
- date: payment date.
- amount: amount of the payment `made` or `missed` in dollars.

###### Example (Payment made)
```
{
  "payment": "made",
  "date": "2017-09-05 02:18Z",
  "amount": 85.60,
}
```
###### Example (Payment missed)
```
{
  "payment": "missed",
  "date": "2017-09-05 02:18Z",
  "amount": 85.60,
}
```

### GET /loans/<:id>/balance

#### Summary

Get the volume of outstanding debt (i.e., debt yet to be paid) at some point in time.


###### Example   
```
  /loans/<:id>/balance?date=2017-09-05 02:18Z
```

#### Reply

- balance: outstanding debt of loan.

###### Example
```
{
	"balance": 40
}
```
