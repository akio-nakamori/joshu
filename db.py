#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()
_session = []


def get_session():
    return _session


def init_db(url):
    engine = create_engine(url, pool_recycle=300)
    if not database_exists(url=engine.url):
        create_database(url=engine.url, encoding='utf8mb4', template=None)

    Base.metadata.create_all(engine)
    global _session
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    _session = Session()
    return _session


class UnknownTable(Base):
    __tablename__ = 'file_unknown'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    path = Column(Text, nullable=True)
    ed2khash = Column(Text, nullable=True)

    def update(self, **kwargs):
        for key, attr in kwargs.items():
            setattr(self, key, attr)

    def __repr__(self):
        return '<UnknownTable(id={id}, path={path}, ed2khash={ed2khash})>'.format(
            id=self.id,
            path=self.path.encode('utf-8'),
            ed2khash=self.ed2khash)


class EpisodeTable(Base):
    __tablename__ = 'episode'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    aid = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=False, index=True)
    eid = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=False, unique=True, index=True)
    length = Column(Integer, nullable=False)
    rating = Column(Float, nullable=True)
    votes = Column(Integer, nullable=False)
    epno = Column(String(8), nullable=False)
    title_eng = Column(String(256), nullable=True)
    title_romaji = Column(String(256), nullable=True)
    title_kanji = Column(Unicode(256), nullable=True)
    aired = Column(Date(), nullable=True)
    type = Column(
        Enum(
            'regular',
            'special',
            'credit',
            'trailer',
            'parody',
            'other'),
        nullable=False)
    updated = Column(DateTime(timezone=True), nullable=False)


class AnimeTable(Base):
    __tablename__ = 'anime'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    aid = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=False, unique=True)
    # TODO dateflags?
    year = Column(String(16), nullable=False)
    type = Column(String(16), nullable=False)

    nr_of_episodes = Column(Integer, nullable=False)
    highest_episode_number = Column(Integer, nullable=False)
    special_ep_count = Column(Integer, nullable=False)
    air_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    url = Column(Text, nullable=True)
    picname = Column(Text, nullable=True)

    rating = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=False)
    temp_rating = Column(Float, nullable=True)
    temp_vote_count = Column(Integer, nullable=False)
    average_review_rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=False)
    is_18_restricted = Column(Boolean, nullable=False)

    ann_id = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=True)
    allcinema_id = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=True)
    animenfo_id = Column(String(64), nullable=True)
    tag_name = Column(Text, nullable=True)
    tag_id = Column(Text, nullable=True)
    tag_weight = Column(Text, nullable=True)
    anidb_updated = Column(DateTime(timezone=False), nullable=False)
    character_id = Column(Text, nullable=True)
    special_count = Column(Integer, nullable=False)
    credit_count = Column(Integer, nullable=False)
    other_count = Column(Integer, nullable=False)
    trailer_count = Column(Integer, nullable=False)
    parody_count = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    updated = Column(DateTime(timezone=True), nullable=False)

    relations = relationship("AnimeRelationTable", backref='anime')


class AnimeRelationTable(Base):
    __tablename__ = 'anime_relation'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    anime_pk = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey('anime.id'), nullable=False)
    related_aid = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=False)
    relation_type = Column(
        Enum(
            'sequel',
            'prequel',
            'same setting',
            'alternative setting',
            'alternative version',
            'music video',
            'character',
            'side story',
            'parent story',
            'summary',
            'full story',
            'other'),
        nullable=False)


class AnimeTitleTable(Base):
    __tablename__ = 'anime_title'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    aid = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=False, index=True)
    titletype = Column(Unicode(512), nullable=True)
    lang = Column(Unicode(512), nullable=True)
    title = Column(Unicode(512), nullable=True)


class AnimeDescTable(Base):
    __tablename__ = 'anime_description'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    aid = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=False)
    part = Column(Integer, nullable=False)
    description = Column(Unicode(8194), nullable=True)
    max_part = Column(Integer, nullable=False)

    updated = Column(DateTime(timezone=True), nullable=False)
