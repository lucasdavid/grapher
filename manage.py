from flask.ext.script import Manager, Server
from grapher.core.grapher import Grapher

if __name__ == "__main__":
    grapher = Grapher(__name__)

    manager = Manager(grapher.app)
    manager.add_command('runserver', Server(port=80))

    manager.run()
