import enum
import base64
import os
from datetime import datetime, timedelta
from app import db
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash

user_pinned_music = db.Table('user_pinned_music', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('music_item_id', db.Integer, db.ForeignKey('music_item.id'), primary_key=True)   
)

user_private_music = db.Table('user_private_music',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('music_item_id', db.Integer, db.ForeignKey('music_item.id'), primary_key=True)
)

class MusicTypeEnum(enum.Enum):
    youtube = 'youtube'
    soundcloud = 'soundcloud'

class PaginatedAPIMixin(object):
    @staticmethod 
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page, 
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page, **kwargs),
                'prev': url_for(endpoint, page=page - 1, per_page=per_page, **kwargs)
            }
        }
        return data

class User(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    pinned_music = db.relationship(
        'MusicItem', 
        secondary=user_pinned_music, 
        lazy='dynamic',
        backref=db.backref('users', lazy='dynamic'))
    private_music = db.relationship(
        'MusicItem',
        secondary=user_private_music,
        lazy='dynamic', 
        backref=db.backref('pinned_users', lazy='dynamic'))
    tokens = db.relationship('UserToken', backref='user', lazy='dynamic')
    #relationship: playlist

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)

    def get_user_token(self, expires_in=3000):
        now = datetime.utcnow()
        tokens = self.tokens.filter(
                UserToken.expiration > now).order_by(
                    UserToken.expiration.desc())
        current_token = tokens[0] if tokens.count() > 0 else None
        if (current_token and
                current_token.expiration > now + timedelta(seconds=60)):
            return current_token
        if current_token:
            current_token.revoke_token()
        new_token = UserToken()
        new_token.user_id = self.id 
        new_token.token = base64.b64encode(os.urandom(24)).decode('utf8')
        new_token.expiration = now + timedelta(seconds=expires_in)
        db.session.add(new_token)
        return new_token

    def get_pinned_music(self):
        pass
        
    def pin_music_item(self, music_item):
        self.pinned_music.append(music_item) 

    def unpin_music_item(self, music_item):
        if self.is_pinned(music_item):
            self.pinned_music.remove(music_item)

    def is_pinned(self, music_item):
        return self.pinned_music.filter(
                user_pinned_music.c.music_item_id == music_item.id).first()

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email
        }

    def from_dict(self, data, new_user=False):
        for field in ['email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def __repr__(self):
        return '<User id={} email={}>'.format(self.id, self.email)

class UserToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, )
    token = db.Column(db.String(48), unique=True, index=True)
    expiration = db.Column(db.DateTime())

    @staticmethod 
    def check_token(token):
        user_token = UserToken.query.filter_by(token=token).first()
        if (user_token and user_token.expiration > datetime.utcnow() and 
                user_token.user):
            return user_token.user
        return None

    def revoke_token(self):
        self.expiration = datetime.utcnow() - timedelta(seconds=1)
        db.session.add(self)

    def __repr__(self):
        return '<UserToken id={} user_id={}, token={}, expiration={}>'.format(
                self.id, self.user_id, self.token, self.expiration
            )

class MusicItem(db.Model):
    __table_args__ = (db.UniqueConstraint('resource_type', 'resource_id'),)
    id = db.Column(db.Integer, primary_key=True)
    resource_type = db.Column(db.Enum(MusicTypeEnum))
    resource_id = db.Column(db.String(48))
    pin_count = db.Column(db.Integer, index=True)
    listen_count = db.Column(db.Integer, index=True)
    private = db.Column(db.Boolean)

    def from_dict(self, data, private=False):
        for field in ['resource_type', 'resource_id']:
            setattr(self, field, data[field])
        if private:
            self.private = True

    def to_dict(self):
        return {
            'id': self.id,
            'resource_type': self.resource_type.name,
            'resource_id': self.resource_id,
            'pin_count': self.pin_count,
            'listen_count': self.listen_count,
            'private': self.private
        }

    def __repr__(self):
        return '<MusicItem id={} resource_type={} resource_id={}>'.format(
                self.id, self.resource_type, self.resource_id
            )

# class TodoList(db.Model):
#     pass 

# class TodoItem(db.Model):
#     pass

# class Timer(db.Model):
#     pass