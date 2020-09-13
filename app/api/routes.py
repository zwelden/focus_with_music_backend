from flask import jsonify, request
from app.api import bp 

@bp.route('/users/<int:id>')
def get_user(id):
    pass 

@bp.route('/users', methods=['POST'])
def create_user():
    pass


@bp.route('/music/default')
def get_default_music_list():
    return {'test': 'content'}


@bp.route('/music', methods=['POST'])
def create_music_item():
    pass