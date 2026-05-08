from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Синглтон
class DatabaseManager:
    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls, database_url="sqlite:///cinema.db"):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._engine = create_engine(database_url)
            cls._session_factory = sessionmaker(bind=cls._engine)
        return cls._instance

    def get_session(self):
        return self._session_factory()

Base = declarative_base()
db_manager = DatabaseManager()