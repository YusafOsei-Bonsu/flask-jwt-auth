import datetime
import jwt
from project.server import app, db, bcrypt

# User model for storing user-based details
class User(db.Model):
    __tablename__ = "users"

    # Fields of the "users" table schema
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(password, app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        self.registered_on = datetime.datetime.now()
        self.admin = admin
    
    # Generates the authentication token
    def encode_auth_token(self, user_id):

        try:
            payload = {
                # Token's expiry date
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                # The time when the token was generated
                'iat': datetime.datetime.utcnow(),
                # The owner (user) of the token
                'sub': user_id
            }

            return jwt.encode(payload, app.config.get('SECRET_KEY'), algorithm='HS256')

        except Exception as e:
            return e
    
    # Decodes the authentication token
    @staticmethod
    def decode_auth_token(auth_token):
        try:
            # the token is decoded with every API request and its signature is 
            # verified to validate the user's authenticity
            payload = jwt.decode(auth_token, app.config.get("SECRET_KEY"))
            # If the auth token is valid, the user id is returned
            return payload["sub"] 
        except jwt.ExpiredSignatureError:
             # Token is used after it has expired
            return "Signature expired. Please log in again."
        except jwt.InvalidTokenError:
            # The token is incorrect/malformed
            return "Invalid token. Please log in again."

# Token model for storing JWT tokens
class BlacklistToken(db.Model):
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)