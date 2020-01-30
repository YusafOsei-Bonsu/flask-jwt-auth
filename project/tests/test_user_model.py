# project/tests/test_user_model.py
import unittest

from project.server import db
from project.server.models import User
from project.tests.base import BaseTestCase

# Unit test for the user model
class TestUserModel(BaseTestCase):

    # Tests the encoding of the authentication token
    def test_encode_auth_token(self):
        user = User(email="test@test.com", password="test")
        db.session.add(user)
        db.session.commit()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))

    # Tests the decoding of the authentication token
    def test_decode_auth_token(self):
        user = User(email = 'test@test.com', password = 'test')
        db.session.add(user)
        db.session.commit()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        # Convert bytes into a string
        self.assertTrue(User.decode_auth_token(auth_token.decode("utf-8")) == 1)    

if __name__ == "__main__":
    unittest.main()