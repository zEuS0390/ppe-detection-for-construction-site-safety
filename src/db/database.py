from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.tables import mapper_registry
from configparser import ConfigParser

# Using SQLAlchemy 2.0

class DatabaseHandler:

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
            echo=echo, 
            future=True
        )
        mapper_registry.metadata.create_all(self.engine)
        self.session = Session(self.engine)


