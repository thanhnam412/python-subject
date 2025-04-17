from marshmallow import Schema, fields, validate
from flask_app.models.notification import Notification

class NotificationSchema(Schema):
    class Meta:
        model = Notification
        fields = ('id', 'user_id', 'title', 'description', 'is_read', 'created_at')
        
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    description = fields.Str(required=True)
    is_read = fields.Bool()
    created_at = fields.DateTime(dump_only=True)

notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)