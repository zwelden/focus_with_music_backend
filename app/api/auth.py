from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models import User
from app.api.errors import error_response, bad_request

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password 
def verify_password(email, password):
    pass 

@basic_auth.error_handler 
def basic_auth_error(status):
    pass 

@token_auth.verify_token
def verify_token(token):
    pass 

@token_auth.error_handler 
def token_auth_error(status):
    pass