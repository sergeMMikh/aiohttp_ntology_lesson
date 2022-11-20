import pytest
from models import Base
from config import PG_HOST, PG_USER, PG_DB, PG_PORT, PG_PASSWORD

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}")
Session = sessionmaker(bind=engine)
@pytest.fixture(scope='session', autouse=True)
def cleanup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

