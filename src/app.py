from flask import Flask
from sqlalchemy import event, DDL

from src.config import app_config
from src.models import db, bcrypt, UserModel
from src.views.users import user_api as user_blueprint
from src.views.devices import device_api as device_blueprint
from flask_apispec import FlaskApiSpec
from src.views import users
from src.views import devices

def create_app(env_name):

    app = Flask(__name__)
    app.config.from_object(app_config[env_name])

    bcrypt.init_app(app)
    db.init_app(app)

    app.register_blueprint(user_blueprint, url_prefix='/garden/v1/users')
    app.register_blueprint(device_blueprint, url_prefix='/garden/v1/devices')

    docs = FlaskApiSpec(app)
    docs.register(devices.create, blueprint=device_blueprint)

    @app.route('/', methods=['GET'])
    def index():
        return 'blah blah blah'

    return app
