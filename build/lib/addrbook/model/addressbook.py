from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text

from addrbook.model import DeclarativeBase, metadata, DBSession

from addrbook.model.auth import User

# Association table for the many-to-many relationship between
# users and contacts.
users_contacts_table = Table('users_contacts', metadata,
                               Column('user_id', Text,
                                      ForeignKey('tg_user.user_id',
                                                 onupdate="CASCADE",
                                                 ondelete="CASCADE"),
                                      primary_key=False),
                               Column('contact_id', Text,
                                      ForeignKey('addressbook.id',
                                                 onupdate="CASCADE",
                                                 ondelete="CASCADE"),
                                      primary_key=False))

class Addressbook(DeclarativeBase):
    __tablename__ = 'addressbook'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    number = Column(Text, nullable=False)
    # many to many relationship with users
    users = relation('User', secondary=users_contacts_table, backref='contacts')
