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

if __name__ == '__main__':
    unittest.main()