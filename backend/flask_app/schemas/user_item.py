from marshmallow import Schema, fields, validate
from flask_app.models.user_item import UserItem

class UserItemSchema(Schema):
    class Meta:
        model = UserItem
        fields = ('id', 'user_id', 'name', 'status', 'quantity', 'balance', 'deposit', 'description', 'created_at')
        
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    status = fields.Str()
    quantity = fields.Int()
    balance = fields.Decimal(places=2)
    deposit = fields.Decimal(places=2)
    description = fields.Str()

user_item_schema = UserItemSchema()
user_items_schema = UserItemSchema(many=True)