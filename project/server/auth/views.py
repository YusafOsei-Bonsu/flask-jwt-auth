from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from project.server import bcrypt, db
from project.server.models import User

auth_blueprint = Blueprint('auth', __name__)

# A new user is registered and a new auth token for further requests is generated, which we send back to the client.
class RegisterAPI(MethodView):

    def post(self):
        # get the post data
        post_data = request.get_json()
        # check if user already exists
        user = User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                user = User(email=post_data.get('email'), password=post_data.get('password'))
                # insert the user
                db.session.add(user)
                db.session.commit()
                # generate the auth token
                auth_token = user.encode_auth_token(user.id)
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered.',
                    'auth_token': auth_token.decode()
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return make_response(jsonify(responseObject)), 202

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

# define the API resources
registration_view = RegisterAPI.as_view('register_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule('/auth/register', view_func = registration_view, methods = ['POST'])