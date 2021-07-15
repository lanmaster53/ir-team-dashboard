import os

class BaseConfig(object):

    # framework
    API_BASE_URL = os.environ.get('API_BASE_URL', 'http://127.0.0.1')

class Development(BaseConfig):

    # framework
    DEBUG = True
    SECRET_KEY = 'developmentkey'

class Production(BaseConfig):

    # framework
    DEBUG = False
    # randomize the key if not provided, will lose token persistence if server resets
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())
