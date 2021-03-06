from flask import jsonify, request, url_for, g
from functools import wraps
from app import db
from app.models import User, MusicItem
from app.api import bp 
from app.api.errors import bad_request
from app.api.auth import basic_auth, token_auth

def force_refresh_authentication(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        g.token_auth_type = 'refresh'
        return f(*args, **kwargs)
    return decorated

@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'email' not in data or 'password' not in data:
        return bad_request('An email and password is required to create and account')
    if User.query.filter_by(email = data['email']).first():
        return bad_request('Email address already in use.')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@bp.route('/music/default', methods=['GET'])
def get_default_music_list():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    data = MusicItem.to_collection_dict(
                MusicItem.query.order_by(MusicItem.listen_count.desc()), 
                page, per_page, 'api.get_default_music_list')
    return jsonify(data)
    
@bp.route('/music/home', methods=['GET'])
@token_auth.login_required
def get_user_home_music_list():
    user = token_auth.current_user()
    pinned_music_ids = db.session.query(MusicItem.id).filter(
                        User.pinned_music).filter(User.id == user.id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    data = MusicItem.to_collection_dict(
                MusicItem.query.filter(~MusicItem.id.in_(pinned_music_ids)),
                page, per_page, 'api.get_user_home_music_list')
    return jsonify(data)

@bp.route('/music/pinned', methods=['GET'])
@token_auth.login_required 
def get_pinned_music_list():
    user = token_auth.current_user()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 5, type=int), 10)
    data = user.to_collection_dict(
                user.pinned_music, 
                page, per_page, 'api.get_pinned_music_list')
    return jsonify(data)

@bp.route('/music/pinned/<int:id>', methods=['POST'])
@token_auth.login_required 
def pin_music(id):
    user = token_auth.current_user()
    music_item = MusicItem.query.get_or_404(id)
    if user.is_pinned(music_item):
        return bad_request('Music video is already in pinned list')
    if music_item.pin_count is None:
        music_item.pin_count = 1
    else: 
        setattr(music_item, 'pin_count', MusicItem.pin_count + 1)
    db.session.add(music_item)
    user.pin_music_item(music_item)
    db.session.commit()
    return '', 200

@bp.route('/music/pinned/<int:id>', methods=['DELETE'])
@token_auth.login_required 
def unpin_music(id):
    user = token_auth.current_user()
    music_item = MusicItem.query.get_or_404(id)
    if user.is_pinned(music_item) is None:
        return bad_request('Music video not found in pinned list')
    if music_item.pin_count is None:
        music_item.pin_count = 0
    else:
        setattr(music_item, 'pin_count', MusicItem.pin_count - 1)
    db.session.add(music_item)
    user.unpin_music_item(music_item)
    db.session.commit()
    return '', 204

@bp.route('/music/private', methods=['GET'])
@token_auth.login_required 
def get_private_music_list():
    user = token_auth.current_user()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 5, type=int), 10)
    data = user.to_collection_dict(
                user.private_music, 
                page, per_page, 'api.get_private_music_list')
    return jsonify(data)

@bp.route('/music/private', methods=['POST'])
@token_auth.login_required
def create_music_item():
    data = request.get_json() or {}
    user = token_auth.current_user()
    if 'resource_type' not in data or 'resource_id' not in data:
        return bad_request('must include resource type and resource id fields')
    music_item = MusicItem.query.filter_by(resource_type=data['resource_type'], 
            resource_id=data['resource_id']).first()
    if music_item:
        if music_item.private == False: 
            return bad_request('Music video already publicly avaliable')
        if user.is_in_private_list(music_item): 
            return bad_request('Music video is already in private list')
    if music_item is None:
        music_item = MusicItem()
        music_item.from_dict(data, private=True)
    user.create_private_music_item(music_item)
    db.session.commit()
    return '', 201

@bp.route('/music/private/<int:id>', methods=['DELETE'])
@token_auth.login_required 
def remove_from_private_music_list(id):
    user = token_auth.current_user()
    music_item = MusicItem.query.get_or_404(id)
    if user.is_in_private_list(music_item) is None:
         return bad_request('Music video not found in private list')
    user.remove_private_music_item(music_item)
    db.session.commit()
    return '', 200


@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_user_tokens():
    user_tokens = basic_auth.current_user().get_user_tokens()
    access_token = user_tokens['access_token']
    refresh_token = user_tokens['refresh_token']
    db.session.commit()
    return jsonify({
        'access_token': access_token.token, 
        'refresh_token': refresh_token.token
    })

@bp.route('/tokens/refresh', methods=['POST'])
@force_refresh_authentication
@token_auth.login_required
def refresh_tokens():
    user_tokens = basic_auth.current_user().get_user_tokens(full_refresh=True)
    access_token = user_tokens['access_token']
    refresh_token = user_tokens['refresh_token']
    db.session.commit()
    return jsonify({
        'access_token': access_token.token, 
        'refresh_token': refresh_token.token
    })

@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_user_token():
    user_tokens = token_auth.current_user().get_user_tokens()
    user_tokens['access_token'].revoke_token()
    user_tokens['refresh_token'].revoke_token()
    db.session.commit()
    return '', 204