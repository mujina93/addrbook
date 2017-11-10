from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text

from addrbook.model import DeclarativeBase, metadata, DBSession

class Addressbook(DeclarativeBase):
    __tablename__ = 'addressbook'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    number = Column(Text, nullable=False)
