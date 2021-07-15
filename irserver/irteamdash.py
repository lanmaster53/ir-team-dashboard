from irteamdash import create_app
import os

# docker-compose run -p 5000:5000 app python3 ./irteamdash.py

app, socketio = create_app(os.environ.get('CONFIG', 'Development'))
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
