from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

from src.models.users import UserModel, UserSchema
from src.models.devices import DeviceModel, DeviceSchema
