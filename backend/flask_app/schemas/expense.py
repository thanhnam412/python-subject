from marshmallow import Schema, fields, validate
from flask_app.models.expense import Expense

class ExpenseSchema(Schema):
    class Meta:
        model = Expense
        fields = ('id', 'user_id', 'category', 'amount', 'description', 'date', 'created_at')
        
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    category = fields.Str(
        required=True,
        validate=validate.OneOf([choice[0] for choice in Expense.CATEGORY_CHOICES])
    )
    amount = fields.Decimal(required=True, places=2)
    description = fields.Str()
    date = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)

expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)