import unittest
import json
from project.server import db
from project.server.models import User
from project.tests.base import BaseTestCase

# The test suite of the authentication process
class TestAuthBlueprint(BaseTestCase):

    # Tests user registration
    def test_registration(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps(dict(email='joe@gmail.com', password='123456')),
                content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    # Test registration in a scenario where the user already exists
    def test_registered_with_already_registered_user(self):
        user = User(email = 'joe@gmail.com', password = 'test')
        db.session.add(user)
        db.session.commit()

        with self.client:
            response = self.client.post(
                '/auth/register',
                data = json.dumps(dict(email = 'joe@gmail.com', password = '123456')),
                content_type = 'application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User already exists. Please Log in.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 202)

    # Tests the login of registered users
    def test_registered_user_login(self):
        with self.client:
            # user registration
            resp_register = self.client.post(
                '/auth/register',
                data = json.dumps(dict(email = 'joe@gmail.com', password = '123456')),
                content_type = 'application/json'
            )
            
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            
            # registered user login
            response = self.client.post(
                '/auth/login',
                data = json.dumps(dict(email = 'joe@gmail.com', password = '123456')),
                content_type='application/json'
            )
            
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

    # Tests the scenario where a non-registered user attempts to login into the app
    def test_non_registered_user_login(self):
        with self.client:
            response = self.client.post(
                '/auth/login',
                data = json.dumps(dict(email = 'joe@gmail.com', password = '123456')),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User does not exist.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()