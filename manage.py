from flask.ext.script import Manager, Server
from grapher import app

app.config.from_object('grapher.settings.DevelopmentSettings')

manager = Manager(app)
manager.add_command('runserver', Server(port=80))

if __name__ == "__main__":
    manager.run()
