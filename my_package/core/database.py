# перенесла в core
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from .config import settings
class DatabaseHelper:
    def __init__(self, url: str, echo: bool=False):
        self.engine = create_async_engine(
            url=url,
            echo=echo
        )
        self.session_factory = async_sessionmaker(
            autoflush=False,
            autocommit=False,
            bind=self.engine,
            expire_on_commit=False,

            class_=AsyncSession,
        )


db_helper = DatabaseHelper(
    url=settings.db_url,
    echo=settings.db_echo,
)



