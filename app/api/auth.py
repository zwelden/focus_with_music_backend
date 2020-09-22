from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models import User, UserToken
from app.api.errors import error_response, bad_request

import logging
log = logging.getLogger('app.api.auth')
log.setLevel(logging.INFO)

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password 
def verify_password(username, password):
    user = User.query.filter_by(email=username).first()
    if user and user.check_password_hash(password):
        return user

@basic_auth.error_handler 
def basic_auth_error(status):
    return error_response(status)

@token_auth.verify_token
def verify_token(token):
    # log.info(token)
    if hasattr(g, 'token_auth_type') and g.token_auth_type == 'refresh':
        return UserToken.check_token(token, token_type='refresh') if token else None

    return UserToken.check_token(token) if token else None

@token_auth.error_handler 
def token_auth_error(status):
    return error_response(status)