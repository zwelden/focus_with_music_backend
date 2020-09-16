from app import db 
from app.models import MusicItem 
from flask_script import Command

class SeedCommand(Command):

    def run(self):
        music = [
            {'resource_type': 'youtube', 'resource_id': 'BnSjnz_mSxk'},
            {'resource_type': 'youtube', 'resource_id': 'JvKjJeXrFvc'},
            {'resource_type': 'youtube', 'resource_id': 'gtmzPUmq7XU'},
            {'resource_type': 'youtube', 'resource_id': 'M5QY2_8704o'},
            {'resource_type': 'youtube', 'resource_id': 'wtg7AetxuWo'},
            {'resource_type': 'youtube', 'resource_id': 'X1uaOtiJ9Vc'},
            {'resource_type': 'youtube', 'resource_id': 'O6CyK4HJ2xU'},
            {'resource_type': 'youtube', 'resource_id': 'iAYMJk9IsDA'},
            {'resource_type': 'youtube', 'resource_id': 'waqxrK-EFI0'}
        ]

        for item in music:
            mi = MusicItem()
            mi.from_dict(item)
            db.session.add(mi)

        db.session.commit()