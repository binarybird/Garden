from flask import request, json, Response, Blueprint, g
from src.models.users import UserModel, UserSchema
from src.shared.auth import Auth

user_api = Blueprint('user_api', __name__)
user_schema = UserSchema()


@user_api.route('/', methods=['POST'])
def create():
    req_data = request.get_json()

    valid = ['email', 'name', 'password']
    clean = {}
    for key in req_data:
        if key in valid:
            clean[key] = req_data[key]

    clean['role'] = 1
    data = user_schema.load(clean)

    user_in_db = UserModel.get_by_email(data.get('email'))
    if user_in_db:
        message = {'error': 'User already exist, please supply another email address'}
        return custom_response(message, 400)

    user = UserModel(data)
    user.save()
    ser_data = user_schema.dump(user)
    token = Auth.generate_token(ser_data.get('id'))
    return custom_response({'jwt_token': token}, 201)


@user_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
    if g.user.get("role") != 0:
        return custom_response({'error': 'invalid operation'}, 400)
    users = UserModel.get_all()
    ser_users = user_schema.dump(users, many=True)
    return custom_response(ser_users, 200)


@user_api.route('/<int:user_id>', methods=['GET'])
@Auth.auth_required
def get_user(user_id):
    if g.user.get('id') != user_id:
        if g.user.get("role") != 0:
            return custom_response({'error': 'invalid operation'}, 400)

    user = UserModel.get(user_id)
    if not user:
        return custom_response({'error': 'user not found'}, 404)

    ser_user = user_schema.dump(user)
    return custom_response(ser_user, 200)


@user_api.route('/<int:user_id>', methods=['PUT'])
@Auth.auth_required
def update(user_id):
    if g.user.get('id') != user_id:
        if g.user.get("role") != 0:
            return custom_response({'error': 'invalid operation'}, 400)

    req_data = request.get_json()
    valid = ['email', 'name', 'password']
    clean = {}
    for key in req_data:
        if key in valid:
            clean[key] = req_data[key]

    data = user_schema.load(clean, partial=True)

    user = UserModel.get(user_id)
    user.update(data)
    ser_user = user_schema.dump(user)
    return custom_response(ser_user, 200)


@user_api.route('/<int:user_id>', methods=['DELETE'])
@Auth.auth_required
def delete(user_id):
    if g.user.get('id') != user_id:
        if g.user.get("role") != 0:
            return custom_response({'error': 'invalid operation'}, 400)

    user = UserModel.get(user_id)
    user.delete()
    return custom_response({'message': 'deleted'}, 204)


@user_api.route('/me', methods=['GET'])
@Auth.auth_required
def get_me():
    user = UserModel.get(g.user.get('id'))
    ser_user = user_schema.dump(user)
    return custom_response(ser_user, 200)


@user_api.route('/login', methods=['POST'])
def login():
    req_data = request.get_json()

    data = user_schema.load(req_data, partial=True)
    # if error:
    #   return custom_response(error, 400)
    if not data.get('email') or not data.get('password'):
        return custom_response({'error': 'you need email and password to sign in'}, 400)
    user = UserModel.get_user_by_email(data.get('email'))
    if not user:
        return custom_response({'error': 'invalid credentials'}, 400)
    if not user.check_hash(data.get('password')):
        return custom_response({'error': 'invalid credentials'}, 400)
    ser_data = user_schema.dump(user)
    token = Auth.generate_token(ser_data.get('id'))
    return custom_response({'jwt_token': token}, 200)


def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )