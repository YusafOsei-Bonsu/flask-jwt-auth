import unittest

from project.server import db
from project.server.models import User
from project.tests.base import BaseTestCase

# Unit test for the user model
class TestUserModel(BaseTestCase):

    def test_encode_auth_token(self):
        user = User(email="test@test.com", password="test")
        db.session.add(user)
        db.session.commit()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))

if __name__ == "__main__":
    unittest.main()