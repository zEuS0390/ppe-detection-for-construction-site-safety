from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.tables import mapper_registry

# Using SQLAlchemy 2.0

class DatabaseHandler:

    def __init__(self, db_URL, echo=False):
        self.engine = create_engine(url=db_URL, echo=echo, future=True)
        mapper_registry.metadata.create_all(self.engine)
        self.session = Session(self.engine)


