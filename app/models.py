from app import db


class User(db.Model):
    # id 
    # username
    # email
    # password_hash 

    #relationship: pinned music 
    #relationship: playlist
    pass

class UserToken(db.Model):
    # id
    # token 
    # token_exipiration 
    # user_id 

    pass

class MusicItem(db.Model):
    # id 
    # type (youtube/soundcloud)
    # resource_id
    # pin_count 
    # listen_count
    
    pass 

class TodoList(db.Model):
    pass 

class TodoItem(db.Model):
    pass

class Timer(db.Model):
    pass