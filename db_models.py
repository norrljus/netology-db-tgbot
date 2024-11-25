import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
import db_connect

Base = declarative_base()


class UsersId(Base):
    __tablename__ = "Users"

    id = sq.Column(sq.Integer, primary_key=True)
    usertgid = sq.Column(sq.Integer, nullable=False)


class Dictionary(Base):
    __tablename__ = "Dictionary"

    id = sq.Column(sq.Integer, primary_key=True)
    rusword = sq.Column(sq.String(length=50), nullable=False)
    engword = sq.Column(sq.String(length=50), nullable=False)


class LearnWords(Base):
    __tablename__ = "LearnWords"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("Users.id"), nullable=False)
    dict_id = sq.Column(sq.Integer, sq.ForeignKey("Dictionary.id"), nullable=False)

    user = relationship(UsersId, backref="userid")
    dict = relationship(Dictionary, backref="wordid")


def firstwords():
    session = db_connect.make_session()
    fw = [("зеленый", "green"), ("синий", "blue"), ("красный", "red"), ("белый", "white"), ("розовый", "pink"),
          ("черный", "black"), ("я", "I"), ("ты", "you"), ("он", "he"), ("она", "she")]
    for i in fw:
        session.add(Dictionary(rusword=i[0], engword=i[1]))
    session.commit()
    session.close()


if __name__ == "__main__":
    engine = db_connect.give_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    firstwords()
