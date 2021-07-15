from flask import Flask
from flask_socketio import SocketIO
import os

socketio = SocketIO()

def create_app(config):

    # setting the static_url_path to blank serves static files from the web root
    app = Flask(__name__, static_url_path='')
    app.config.from_object('irteamdash.config.{}'.format(config.title()))

    socketio.init_app(app)

    from irteamdash.views.api import resources
    app.register_blueprint(resources, url_prefix='/api')

    from irteamdash.views.ui import frontend
    app.register_blueprint(frontend)

    return app, socketio
