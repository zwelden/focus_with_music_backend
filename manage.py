from flask_script import Manager 

from app import create_app, db 
from commands.seed_command import SeedCommand

app = create_app()

manager = Manager(app)
app.app_context().push()
manager.add_command('seed_db', SeedCommand)

if __name__ == "__main__":
    manager.run()
