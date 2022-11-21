from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.db.tables import mapper_registry
from configparser import ConfigParser

# Using SQLAlchemy 2.0

class DatabaseHandler:

    isRunning = True

    def __init__(self, cfg: ConfigParser=None, db_URL: str=None, echo=False):
        if cfg is not None and db_URL is None:
            self.cfg = cfg
            self.dbname = f"sqlite:///data/{self.cfg.get('database', 'name')}.sqlite"
        elif cfg is None and db_URL is not None:
            self.dbname = db_URL
        else:
            self.dbname = "sqlite:///data/appdb.sqlite"
        self.engine = create_engine(
            url=self.dbname, 
            connect_args={"check_same_thread": False},
            echo=echo, 
            future=True
        )
        mapper_registry.metadata.create_all(self.engine)
        session_factory = sessionmaker(autoflush=True, autocommit=False, bind=self.engine)
        scoped = scoped_session(session_factory)
        self.session = scoped()
        self.n_operations = 0 # Number of SQL operations to track before committing them
