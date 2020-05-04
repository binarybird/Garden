from flask import request, json, Response, Blueprint, g

import src
from src.models.users import UserModel, UserSchema
from src.models.devices import DeviceModel, DeviceSchema
from src.shared.auth import Auth
from src.i2c.device import *
import src.i2c
import src.i2c.device

device_api = Blueprint('device_api', __name__)
device_schema = DeviceSchema()


@device_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
    req_data = request.get_json()
    data = device_schema.load(req_data)

    dev = DeviceModel(data)
    dev.save()

    ser_dev = device_schema.dump(dev)
    return custom_response(ser_dev, 200)


@device_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
    devices = DeviceModel.get_all()
    ser_devices = device_schema.dump(devices, many=True)
    return custom_response(ser_devices, 200)


@device_api.route('/<int:device_id>', methods=['GET'])
@Auth.auth_required
def get_device(device_id):
    dev = DeviceModel.get(device_id)
    if not dev:
        return custom_response({'error': 'device not found'}, 404)

    ser_dev = device_schema.dump(dev)
    return custom_response(ser_dev, 200)


@device_api.route('/<int:device_id>', methods=['PUT'])
@Auth.auth_required
def update(device_id):
    req_data = request.get_json()
    data = device_schema.load(req_data, partial=True)

    dev = DeviceModel.get(device_id)
    if not dev:
        return custom_response({'error': 'device not found'}, 404)
    dev.update(data)
    ser_dev = device_schema.dump(dev)
    return custom_response(ser_dev, 200)


@device_api.route('/<int:device_id>', methods=['DELETE'])
@Auth.auth_required
def delete(device_id):
    dev = DeviceModel.get(device_id)
    if not dev:
        return custom_response({'error': 'device not found'}, 404)
    dev.delete()
    return custom_response({'message': 'deleted'}, 204)


@device_api.route('/<int:device_id>/poll', methods=['GET'])
@Auth.auth_required
def poll(device_id):
    dev = DeviceModel.get(device_id)
    if not dev:
        return custom_response({'error': 'device not found'}, 404)

    ser_dev = device_schema.dump(dev)
    muxer = src.i2c.device.get_muxer()

    devclass = getattr(src.i2c.device, ser_dev['device_clazz'])
    instance = devclass(ser_dev['mux_channel'], ser_dev['mux_address'],
                        ser_dev['name'], ser_dev['bus'], ser_dev['address'])

    change_mux_channel(muxer, instance)
    resp = instance.poll()

    return custom_response(resp, 200)


def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )
