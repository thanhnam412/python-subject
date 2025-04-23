from marshmallow import Schema, fields, validate


class IncomeSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    source = fields.Str(required=True)
    description = fields.Str(required=False)
    date = fields.DateTime(required=False)


class ExpenseSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    title = fields.Str(required=True)
    description = fields.Str(required=False)
    date = fields.DateTime(required=False)


class DebtSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    title = fields.Str(required=True)
    description = fields.Str(required=False)
    interest_rate = fields.Float(required=True, validate=validate.Range(min=0))
    due_date = fields.DateTime(required=True)
