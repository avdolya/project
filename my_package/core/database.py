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




'''SQL_DB_URL = 'sqlite:///./test.db'

engine = create_async_engine(SQL_DB_URL, connect_args={"check_same_thread": False})

session_local = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()'''