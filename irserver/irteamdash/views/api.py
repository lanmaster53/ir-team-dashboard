from flask import Blueprint, request, Response
from flask_restful import Resource, Api
from flask_socketio import emit
from irteamdash import socketio
import traceback

resources = Blueprint('resources', __name__)
api = Api()
api.init_app(resources)

# API RESOURCE CLASSES

class TelemetryList(Resource):

    def post(self):
        '''Collects telemetry from client agents.'''
        socketio.emit('newTelemetry', request.json)
        return Response(None, 204)

api.add_resource(TelemetryList, '/telemetry')

@socketio.on('connect')
def connect_handler():
    emit('log', 'Socket connected.')

@socketio.on_error_default
def default_error_handler(e):
    emit('log', request.event)
    print(traceback.format_exc())
