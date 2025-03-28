from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    """
    Schema for serializing/deserializing User objects.

    Fields:
        id (int): User ID (read-only).
        username (str): Username (required).
        email (str): Email address (required, must be a valid email).
        password (str): Password (required, write-only).
    """
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)


class CategorySchema(Schema):
    """
    Schema for serializing/deserializing Category objects.

    Fields:
        id (int): Category ID (read-only).
        name (str): Category name (required).
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class TransactionSchema(Schema):
    """
    Schema for serializing/deserializing Transaction objects.

    Fields:
        id (int): Transaction ID (read-only).
        user_id (int): User ID (required).
        category_id (int): Category ID (required).
        amount (float): Transaction amount (required).
        type (str): Transaction type (required, must be 'expense' or 'income').
        date (date): Transaction date (required).
        description (str): Transaction description (optional).
    """
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    category_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    type = fields.Str(required=True, validate=validate.OneOf(['expense', 'income']))
    date = fields.Date(required=True)
    description = fields.Str()


class BudgetSchema(Schema):
    """
    Schema for serializing/deserializing Budget objects.

    Fields:
        id (int): Budget ID (read-only).
        user_id (int): User ID (required).
        category_id (int): Category ID (required).
        limit (float): Budget limit (required).
    """
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    category_id = fields.Int(required=True)
    limit = fields.Float(required=True)


class BillSchema(Schema):
    """
    Schema for serializing/deserializing Bill objects.

    Fields:
        id (int): Bill ID (read-only).
        user_id (int): User ID (required).
        bill_name (str): Bill name (required).
        due_date (date): Due date of the bill (required).
        amount (float): Bill amount (required).
    """
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    bill_name = fields.Str(required=True)
    due_date = fields.Date(required=True)
    amount = fields.Float(required=True)


class SharedExpenseSchema(Schema):
    """
    Schema for serializing/deserializing SharedExpense objects.

    Fields:
        id (int): Shared expense ID (read-only).
        payer_id (int): Payer ID (required).
        amount (float): Shared expense amount (required).
        description (str): Shared expense description (optional).
        participants (str): Comma-separated list of participants (required).
    """
    id = fields.Int(dump_only=True)
    payer_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    description = fields.Str()
    participants = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, error="Participants list cannot be empty"),
            validate.Regexp(
                r'^[a-zA-Z0-9_]+(,[a-zA-Z0-9_]+)*$',
                error="Participants must be a comma-separated list of usernames (letters, numbers, underscores)"
            )
        ]
    )


class NotificationSchema(Schema):
    """
    Schema for serializing/deserializing Notification objects.

    Fields:
        id (int): Notification ID (read-only).
        user_id (int): User ID (required).
        message (str): Notification message (required).
        created_at (datetime): Creation timestamp (read-only).
        is_read (bool): Whether the notification has been read (optional).
    """
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    message = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    is_read = fields.Boolean()