from flask import Flask
from flask.ext.script import Manager, Server
from grapher import Grapher

if __name__ == "__main__":
    app = Flask(__name__)
    app.config.from_object('grapher.settings.DevelopmentSettings')

    api = Grapher(app).startup()

    manager = Manager(app)
    manager.add_command('runserver', Server(port=80))

    manager.run()
