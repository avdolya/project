from datetime import datetime, timedelta
import bcrypt
import jwt
from my_package.core.config import settings
# функции для создания токенов

# создает токен, получает настройки из settings
def encode_jwt(
        payload: dict,
        # читаем наш ключ с помощью read_text()
        private_key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None,
):
    # чтобы токены были невечные
    # создаем отдельный словарь
    to_encode = payload.copy()
    # указываем когда токен сгорит
    # берем реальное время
    now = datetime.utcnow()
    # если expire_timedelta передано
    if expire_timedelta:
        # к реальному времени добавляем
        expire = now + expire_timedelta
    else:
        # если пришло expire_minutes
        expire = now + timedelta(minutes=expire_minutes)
    # обновляем
    to_encode.update(
        # служебны поля
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded

def decode_jwt(
        # может быть и строчкой, и байтами
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
):
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
    )
    return decoded

def hash_password(
       password: str,
) -> bytes:
    # генерируем соль
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    # передаем пароль и соль, при помощи
    # соли пароль хэшируется
    return bcrypt.hashpw(pwd_bytes, salt)

# когда приходит пароль, нужно проверить,
# совпадает ли он с хэшированным паролем
def validate_password(
    password: str,
    hashed_password: bytes,
)->bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )




