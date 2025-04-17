from marshmallow import Schema, fields, validate
from flask_app.models.income import Income

class IncomeSchema(Schema):
    class Meta:
        model = Income
        fields = ('id', 'user_id', 'category', 'amount', 'description', 'date', 'created_at')
        
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    category = fields.Str(
        required=True,
        validate=validate.OneOf([choice[0] for choice in Income.CATEGORY_CHOICES])
    )
    amount = fields.Decimal(required=True, places=2)
    description = fields.Str()
    date = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)

income_schema = IncomeSchema()
incomes_schema = IncomeSchema(many=True)