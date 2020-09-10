from flask import jsonify, request
from app.main import bp 

@bp.route('/music/default')
def get_default_music_list():
    return {'test': 'content'}

