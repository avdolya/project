from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import BaseModel

BASE_DIR=Path(__file__).parent.parent

# настройки jwt
class AuthJWT(BaseModel):
    # Path - тип путь
    # название переменной: тип = значение
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    # сколько минут живет токен
    access_token_expire_minutes: int = 15

class Setting(BaseSettings):
    # адрес базы данных
    db_url: str = "postgresql+asyncpg://user:password@localhost:5432/db"
    # вывод sql запросов в консоль, запросы отображаются в консоль
    db_echo: bool = True
    # создает экземпляр класса AuthJWT
    auth_jwt: AuthJWT = AuthJWT()


# создание экземпляра конфигурации
settings = Setting()




