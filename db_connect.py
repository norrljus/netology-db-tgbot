import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker

username = 'postgres'
password = '1111'
port = '5432'
dbname = 'learneng'

engine = sq.create_engine(f'postgresql://{username}:{password}@localhost:{port}/{dbname}')


def make_session():
    Session = sessionmaker(bind=engine)
    return Session()


def give_engine():
    return engine
