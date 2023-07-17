from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.db.tables import mapper_registry
from src.singleton import Singleton
from configparser import ConfigParser

# Using SQLAlchemy 2.0

class DatabaseHandler:

    isRunning = True

    def __init__(self, cfg: ConfigParser=None, db_URL: str=None, echo=False):
        if cfg is not None and db_URL is None:
            self.cfg = cfg
            self.dbname = f"sqlite:///data/{self.cfg.get('database', 'name')}.sqlite"
            print("picking the custom named database from the configuration")
        elif (cfg is None and db_URL is not None) or (cfg is not None and db_URL is not None):
            self.dbname = db_URL
            print("picking the custom named database from the argument") 
        else:
            self.dbname = "sqlite:///data/appdb.sqlite"
            print("picking the default named database")
        self.engine = create_engine(
            url=self.dbname
        )
        mapper_registry.metadata.create_all(self.engine)
        session_factory = sessionmaker(autoflush=True, autocommit=False, bind=self.engine)
        self.scoped = scoped_session(session_factory)
        self.session = self.scoped()
        self.n_operations = 0 # Number of SQL operations to track before committing them
