def get_loan_schema():
    return {
        "type": "object",
        "properties": {
            "amount": {"type": "integer", "minimum": 0, "exclusiveMinimum": True},
            "term": {"type": "integer", "minimum": 0, "exclusiveMinimum": True},
            "rate": {"type": "number", "multipleOf": 0.01, "minimum": 0.00, "maximum": 1.00},
            "date": {"type": "string", "minLength": 1}
        },
        "additionalProperties": False,
        "required": ["amount", "term", "rate", "date"]
    }


def get_payment_schema():
    return {
        "type": "object",
        "properties": {
            "payment": {"type": "string", "enum": ["made", "missed"]},
            "amount": {"type": "number"},
            "date": {"type": "string", "minLength": 1}
        },
        "additionalProperties": False,
        "required": ["payment", "amount", "date"]
    }


schemas = {
    "loan": get_loan_schema(),
    "payment": get_payment_schema()
}
