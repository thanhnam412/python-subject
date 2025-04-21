from marshmallow import Schema, fields, validate


class IncomeSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    source = fields.Str(required=True)
    description = fields.Str(required=False)
    date = fields.Date(required=False)


class ExpenseSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    description = fields.Str(required=True)
    category = fields.Str(required=True)
    date = fields.Date(required=False)


class DebtSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    description = fields.Str(required=False)
    interest_rate = fields.Float(required=True, validate=validate.Range(min=0))
    due_date = fields.Date(required=True)
    is_paid = fields.Bool(required=False)
    monthly_payment = fields.Float(required=False, validate=validate.Range(min=0))
    category = fields.Str(required=False)


class DebtUpdateSchema(Schema):
    amount = fields.Float(required=False, validate=validate.Range(min=0))
    description = fields.Str(required=False)
    interest_rate = fields.Float(required=False, validate=validate.Range(min=0))
    due_date = fields.Date(required=False)
    is_paid = fields.Bool(required=False)
    monthly_payment = fields.Float(required=False, validate=validate.Range(min=0))
    category = fields.Str(required=False)


class FinancialSummarySchema(Schema):
    total_income = fields.Float(dump_only=True)
    total_expense = fields.Float(dump_only=True)
    total_debt = fields.Float(dump_only=True)
    balance = fields.Float(dump_only=True)
    date = fields.Date(dump_only=True)


class IncomeSourceSchema(Schema):
    source = fields.Str(required=True)
    total = fields.Float(required=True)


class IncomeDateSchema(Schema):
    date = fields.Str(required=True)
    total = fields.Float(required=True)


class IncomeStatisticsSchema(Schema):
    total_income = fields.Float(required=True)
    by_source = fields.List(fields.Nested(IncomeSourceSchema), required=True)
    monthly_income = fields.List(fields.Nested(IncomeDateSchema), required=True)


class DebtDateSchema(Schema):
    date = fields.Str(required=True)
    total = fields.Float(required=True)


class DebtStatisticsSchema(Schema):
    total_debt = fields.Float(required=True)
    upcoming_debts = fields.List(fields.Nested(DebtDateSchema), required=True) 