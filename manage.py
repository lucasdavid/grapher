from flask.ext.script import Manager, Server
from demosthenes import app

app.config.from_object('demosthenes.settings.DevelopmentSettings')

manager = Manager(app)
manager.add_command('runserver', Server(port=80))

if __name__ == "__main__":
    manager.run()
