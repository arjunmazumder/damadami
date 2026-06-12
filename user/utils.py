import jwt
import datetime
import secrets
from django.conf import settings

def generate_access_token(user):
    payload = {
        'user_id': str(user.id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def decode_access_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Access token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid access token")

def generate_refresh_token():
    return secrets.token_urlsafe(128)
