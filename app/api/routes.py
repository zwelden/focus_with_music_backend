from flask import jsonify, request
from app import db
from app.models import User
from app.api import bp 
from app.api.auth import basic_auth, token_auth

@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())

@bp.route('/users', methods=['POST'])
def create_user():
    pass


@bp.route('/music/default')
def get_default_music_list():
    return {'test': 'content'}


@bp.route('/music', methods=['POST'])
def create_music_item():
    pass


@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_user_token():
    user_token = basic_auth.current_user().get_user_token()
    db.session.commit()
    return jsonify({'user_token': user_token.token})

@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_user_token():
    token = token_auth.current_user().get_user_token()
    token.revoke_token()
    db.session.commit()
    return '', 204