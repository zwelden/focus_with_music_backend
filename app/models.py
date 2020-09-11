import enum
from app import db

user_pinned_music = db.Table('user_pinned_music', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('music_item_id', db.Integer, db.ForeignKey('music_item.id'), primary_key=True)   
)

class MusicTypeEnum(enum.Enum):
    youtube = 'youtube'
    soundcloud = 'soundcloud'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hand = db.Column(db.String(128))

    pinned_music = db.relationship(
        'MusicItem', 
        secondary=user_pinned_music, 
        lazy='dynamic',
        backref=db.backref('users', lazy='dynamic'))
    token = db.relationship('UserToken', backref='user', lazy='dynamic')
    #relationship: playlist

    def pin_music_item(self, music_item):
        self.pinned_music.append(music_item) 

    def unpin_music_item(self, music_item):
        if self.is_pinned(music_item):
            self.pinned_music.remove(music_item)

    def is_pinned(self, music_item):
        return self.pinned_music.filter(
                user_pinned_music.c.music_item_id == music_item.id).first()

    def __repr__(self):
        return '<User id={} email={}>'.format(self.id, self.email)

class UserToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, )
    token = db.Column(db.String(48), unique=True, index=True)
    expiration = db.Column(db.DateTime())

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

    def __repr__(self):
        return '<MusicItem id={} resource_type={} resource_id={}>'.format(
                self.id, self.type, self.resource_id
            )

# class TodoList(db.Model):
#     pass 

# class TodoItem(db.Model):
#     pass

# class Timer(db.Model):
#     pass