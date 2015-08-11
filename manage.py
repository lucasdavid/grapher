from flask.ext.script import Manager, Server
from grapher import Grapher, GrapherApi

if __name__ == "__main__":
    app = Grapher(__name__)
    app.config.from_object('grapher.settings.DevelopmentSettings')

    api = GrapherApi(app).startup()

    manager = Manager(app)
    manager.add_command('runserver', Server(port=80))

    manager.run()
