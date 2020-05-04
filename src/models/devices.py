from marshmallow import fields, Schema
import datetime
from . import db


class DeviceModel(db.Model):

    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    device_clazz = db.Column(db.String(128), nullable=False)
    address = db.Column(db.Integer)
    bus = db.Column(db.Integer)
    mux_address = db.Column(db.Integer)
    mux_channel = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        self.name = data.get('name')
        self.device_clazz = data.get('device_clazz')
        self.address = data.get('address')
        self.bus = data.get('bus')
        self.mux_address = data.get('mux_address')
        self.mux_channel = data.get('mux_channel')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return DeviceModel.query.all()

    @staticmethod
    def get(id):
        return DeviceModel.query.get(id)

    def __repr(self):
        return '<id {}>'.format(self.id)


class DeviceSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    device_clazz = fields.Str(required=True)
    address = fields.Int(required=True)
    bus = fields.Int(required=True)
    mux_address = fields.Int(required=True)
    mux_channel = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
