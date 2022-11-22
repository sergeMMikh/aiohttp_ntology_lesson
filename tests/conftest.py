import pytest
import time
from models import Base, User
from config import PG_HOST, PG_USER, PG_DB, PG_PORT, PG_PASSWORD
from auth import hash_password

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}")
Session = sessionmaker(bind=engine)


@pytest.fixture(scope='session', autouse=True)
def cleanup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield


@pytest.fixture(scope='session')
def root_user():
    with Session() as session:
        new_user = User(name='root', password=hash_password('toor'))
        session.add(new_user)
        session.commit()
        return {
            'id': new_user.id,
            'name': new_user.name,
            'password': 'toor'
        }


@pytest.fixture()
def new_user():
    with Session() as session:
        new_user = User(name=f'new_user_{time.time()}', password=hash_password('1234'))
        session.add(new_user)
        session.commit()
        return {
            'id': new_user.id,
            'name': new_user.name,
            'password': '1234'
        }
