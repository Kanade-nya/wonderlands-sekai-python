from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime,ForeignKey,BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext

from pydantic import BaseModel
from typing import List

Base = declarative_base()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    avatar = Column(String(255))
    description = Column(String(255))
    blog = Column(String)
    create_date = Column(DateTime, default=datetime.utcnow)


    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    author_name = Column(String(255))
    author_id = Column(Integer, ForeignKey('users.id'))
    author_avatar = Column(String(255))
    content = Column(String(255))
    title = Column(String(255))
    create_date = Column(DateTime, default=datetime.utcnow)

    author = relationship("User", backref="articles")

class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True)
    code = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Collection(Base):
    __tablename__ = "collections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(255))
    ids_list = Column(String(255), default="[]")  # 存储包含的图像的 id 的数组，以 JSON 字符串形式存储
    create_date = Column(DateTime, default=datetime.utcnow)

# 定义创建合集的请求体模型，这里由于 SQLAlchemy 本身不处理请求体，所以我们可以简单使用 Python 类来模拟 Pydantic 模型的功能
# 定义创建合集的请求体模型


# 定义 website_image_store 模型



class WebsiteImageStore(Base):
    __tablename__ = "website_image_store"
    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(255))
    image_url = Column(String)
    artiest = Column(String(255))
    description = Column(String)
    type_id = Column(Integer)
    character_id = Column(Integer)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    tags = relationship("Tag", secondary="image_tag_association", back_populates="images")
    __table_args__ = {'mysql_engine': 'InnoDB'}
class Tag(Base):
    __tablename__ = "tags"
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    images = relationship("WebsiteImageStore", secondary="image_tag_association", back_populates="tags")
    __table_args__ = {'mysql_engine': 'InnoDB'}

class ImageTagAssociation(Base):
    __tablename__ = "image_tag_association"
    image_id = Column(BigInteger, ForeignKey("website_image_store.id"), primary_key=True)
    tag_id = Column(BigInteger, ForeignKey("tags.id"), primary_key=True)
    # __table_args__ = {'mysql_engine': 'InnoDB'}