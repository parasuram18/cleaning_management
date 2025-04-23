import jwt, datetime
from members.models import RoleMapping, CustomUser
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_jwt.settings import api_settings

def get_secret_key():
    return settings.SECRET_KEY

def custom_payload_handler(user):
    if isinstance(user, dict):
        user_id = user.get('user_id')
        user = CustomUser.objects.get(id=user_id)
    else:
        user_id = user.id

    role = RoleMapping.objects.get(user=user).role.role
    payload = {
        "user_id":user_id,
        'email': user.email,
        "role":role,
        "exp":datetime.datetime.utcnow()+datetime.timedelta(days=1),
        "iat":datetime.datetime.utcnow()
    }
    return payload

def get_user_id_from_payload_handler(payload):
    id = payload.get('user_id')
    usernamefield = CustomUser.objects.get(id=id).phonenumber
    return usernamefield

def custom_jwt_encode_handler(payload):
    secret = get_secret_key()
    token = jwt.encode(payload, key=secret,algorithm='HS256')
    abs_token = token.decode('utf-8') if isinstance(token, bytes) else token
    return abs_token

def custom_decode_handler(token):
    secret = get_secret_key()
    abs_token = token.decode('utf-8') if isinstance(token, bytes) else token
    try:
        payload = jwt.decode(abs_token, secret, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid Token')
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token Expired')
    return payload
