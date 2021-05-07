from flask import request, jsonify, current_app
from src.models import User
import jwt
from functools import wraps


# Decorator function to validate token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'msg': 'Token is missing!'}), 401
        try:
            print(current_app.config['SECRET_KEY'])
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            current_user = User.query.filter_by(user_id=data['user_id']).first()
        except Exception as e:
            print(e)
            return jsonify({'msg': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)

    return decorated
