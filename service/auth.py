import base64
import hashlib
import datetime
import calendar
import jwt

from flask import current_app


def get_hash(password):
    """запись пользователя"""
    return hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode('utf-8'),  # Convert the password to bytes
        salt=current_app.config['PWD_HASH_SALT'],
        iterations=current_app.config['PWD_HASH_ITERATIONS']
    )


def generate_password_hash(password):
    """генерация хеша"""
    return base64.b64encode(get_hash(password)).decode('utf-8')


def compare_password(password_user, password_hash):
    """сравнение паролей"""
    return generate_password_hash(password_user) == password_hash


def generate_token(username, password_hash, password, is_refresh=True):
    if username is None:
        return None
    if not is_refresh:
        if not compare_password(password_user=password, password_hash=password_hash):
            return f'ошибка в сравнении,password_hash={password_hash}, password={password}, generate_password_hash(password)={generate_password_hash(password)}'

    data = {
        "username": username,
        "password": password
    }

    """15минутный токен"""
    min15 = datetime.datetime.utcnow() + datetime.timedelta(minutes=current_app.config['TOKEN_EXPIRE_MINUTES'])
    data["exp"] = calendar.timegm(min15.timetuple())
    access_token = jwt.encode(data, key=current_app.config['SECRET_KEY'],
                              algorithm=current_app.config['ALGORITHM'])

    """3600дневный токен"""
    min_day = datetime.datetime.utcnow() + datetime.timedelta(days=current_app.config['TOKEN_EXPIRE_DAY'])
    data["exp"] = calendar.timegm(min_day.timetuple())
    refresh_token = jwt.encode(data, key=current_app.config['SECRET_KEY'],
                               algorithm=current_app.config['ALGORITHM'])

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def approve_token(token):
    data = jwt.decode(token, key=current_app.config['SECRET_KEY'],
                      algorithm=current_app.config['ALGORITHM'])

    username = data.get("username")
    password = data.get("password")

    return generate_token(username=username, password=password, password_hash=None, is_refresh=True)
