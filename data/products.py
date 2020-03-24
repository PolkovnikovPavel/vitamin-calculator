import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Products(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    vitamin = sqlalchemy.Column(sqlalchemy.Float)
    type = sqlalchemy.Column(sqlalchemy.Integer,
                               sqlalchemy.ForeignKey("types.id"))
    is_varfarin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
