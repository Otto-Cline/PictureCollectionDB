"""
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

image_tag = Table(
    'image_tag', Base.metadata,
    Column("image_id", ForeignKey("images.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True)
)

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    creator = Column(String)
    date = Column(String)
    source_url = Column(String)
    collection_id = Column(Integer, ForeignKey("collections.id"))

    tags = relationship("Tag", secondary=image_tag, back_populates="images")
    collection = relationship("Collection", back_populates="images")

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    images = relationship("Image", secondary=image_tag, back_populates="tags")

class Collection(Base):
    __tablename__ = 'collections'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    images = relationship("Image", back_populates="collection")
"""
