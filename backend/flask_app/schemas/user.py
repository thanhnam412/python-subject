from marshmallow import Schema, fields, validate
from flask_app.models.user import User
from werkzeug.security import generate_password_hash
class UserSchema(Schema):
    class Meta:
        model = User
        # fields = ('id', 'username', 'email', 'created_at')
        
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password_hash = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

   
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))

    def load(self, *args, **kwargs):
        data = super().load(*args, **kwargs)
        if 'password' in data:
           
            data['password_hash'] = generate_password_hash(data['password'])
        return data
class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_login_schema = UserLoginSchema()