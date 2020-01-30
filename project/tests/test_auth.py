# project/tests/test_auth.py
import unittest
import json
import time
from project.server import db
from project.server.models import User, BlacklistToken
from project.tests.base import BaseTestCase

# Simulates a registered user
def register_user(self, email, password):
    return self.client.post(
        "/auth/register",
        data = json.dumps(dict(email = email, password = password)),
        content_type = "application/json"
    )

# The test suite of the authentication process
class TestAuthBlueprint(BaseTestCase):

    # Tests user registration
    def test_registration(self):
        with self.client:
            response = register_user(self, "joe@gmail.com", "123456")
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
            response = register_user(self, "joe@gmail.com", "123456")
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User already exists. Please Log in.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 202)

    # Tests the login of registered users
    def test_registered_user_login(self):
        with self.client:
            # user registration
            resp_register = register_user(self, "joe@gmail.com", "123456")

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
    
    #  Testing if the the auth token is sent with the request within the header.
    def test_user_status(self):
        with self.client:
            resp_register = register_user(self, "joe@gmail.com", "123456")

            response = self.client.get(
                '/auth/status',
                headers = dict(Authorization='Bearer ' + json.loads(resp_register.data.decode())['auth_token'])
            )

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['data'] is not None)
            self.assertTrue(data['data']['email'] == 'joe@gmail.com')
            self.assertTrue(data['data']['admin'] is 'true' or 'false')
            self.assertEqual(response.status_code, 200)

    # Tests logging out before token expiration
    def test_valid_logout(self):
        with self.client:
            # user registration
            resp_register = register_user(self, "joe@gmail.com", "123456")

            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            
            # user login
            resp_login = self.client.post(
                '/auth/login',
                data = json.dumps(dict(email = 'joe@gmail.com', password = '123456')),
                content_type='application/json'
            )

            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
    
            # valid token logout
            response = self.client.post(
                '/auth/logout',
                headers = dict(Authorization='Bearer ' + json.loads(resp_login.data.decode())['auth_token'])
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged out.')
            self.assertEqual(response.status_code, 200)


    # Tests post-token expiration after attempting to logout 
    def test_invalid_logout(self):
        with self.client:
            # user registration
            resp_register = register_user(self, "joe@gmail.com", "123456")
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # user login

            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(email='joe@gmail.com', password='123456')),
                content_type='application/json'
            )
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
            # invalid token logout
            time.sleep(6)
            response = self.client.post(
                '/auth/logout',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'Signature expired. Please log in again.')
            self.assertEqual(response.status_code, 401)


    # Tests logging out after a valid token has been blacklisted
    def test_valid_blacklisted_token_logout(self):
        with self.client:
            # user registration
            resp_register = register_user(self, "joe@gmail.com", "123456")
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)

            # user login
            resp_login = self.client.post(
                '/auth/login',
                data = json.dumps(dict(email = 'joe@gmail.com', password = '123456')),
                content_type='application/json'
            )
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
            # blacklist a valid token
            blacklist_token = BlacklistToken(
                token=json.loads(resp_login.data.decode())['auth_token'])
            db.session.add(blacklist_token)
            db.session.commit()
            
            # blacklisted valid token logout
            response = self.client.post(
                '/auth/logout',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    # Test for user status with a blacklisted valid token
    def test_valid_blacklisted_token_user(self):
        with self.client:
            resp_register = register_user(self, "joe@gmail.com", "123456")
            
            # blacklist a valid token
            blacklist_token = BlacklistToken(token = json.loads(resp_register.data.decode())['auth_token'])
            db.session.add(blacklist_token)
            db.session.commit()
            response = self.client.get(
                '/auth/status',
                headers = dict(Authorization='Bearer ' + json.loads(resp_register.data.decode())['auth_token'])
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    # Test for user status with malformed bearer token
    def test_user_status_malformed_bearer_token(self):

        with self.client:
            resp_register = register_user(self, 'joe@gmail.com', '123456')
            response = self.client.get(
                '/auth/status',
                headers = dict(Authorization='Bearer' + json.loads(resp_register.data.decode())['auth_token'])
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Bearer token malformed.')
            self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
