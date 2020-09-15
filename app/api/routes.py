from flask import jsonify, request
from app import db
from app.models import User, MusicItem
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

@bp.route('/music/pinned', methods=['GET'])
@token_auth.login_required 
def get_pinned_music():
    user = User.query.get_or_404(token_auth.current_user().id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 5, type=int), 10)
    data = user.to_collection_dict(user.pinned_music, page, per_page, 'api.get_pinned_music')
    return jsonify(data)

@bp.route('/music/pinned/<int:id>', methods=['POST'])
@token_auth.login_required 
def pin_music(id):
    music_item = MusicItem.query.get_or_404(id)
    music_item.pin_count += 1
    if token_auth.current_user().is_pinned(music_item) == None:
        token_auth.current_user().pin_music_item(music_item)
    db.session.commit()
    return '', 200


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