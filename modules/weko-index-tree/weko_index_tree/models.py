# -*- coding: utf-8 -*-
#
# This file is part of WEKO3.
# Copyright (C) 2017 National Institute of Informatics.
#
# WEKO3 is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# WEKO3 is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WEKO3; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.

"""Models for weko-index-tree."""

from datetime import datetime

from flask import current_app
from invenio_db import db
from sqlalchemy.dialects import mysql
from sqlalchemy.event import listen
from weko_records.models import Timestamp
# from sqlalchemy_utils.types import UUIDType
# from invenio_records.models import RecordMetadata


class Index(db.Model, Timestamp):
    """
    Represent an index.

    The Index object contains a ``created`` and  a ``updated``
    properties that are automatically updated.
    """

    __tablename__ = 'index'

    __table_args__ = (
        db.UniqueConstraint('parent', 'position', name='uix_position'),
    )

    id = db.Column(db.BigInteger, primary_key=True, unique=True)
    """Identifier of the index."""

    parent = db.Column(db.BigInteger, nullable=False, default=0)
    """Parent Information of the index."""

    position = db.Column(db.Integer, nullable=False, default=0)
    """Children position of parent."""

    index_name = db.Column(db.Text, nullable=True, default='')
    """Name of the index."""

    index_name_english = db.Column(db.Text, nullable=False, default='')
    """English Name of the index."""

    comment = db.Column(db.Text, nullable=True, default='')
    """Comment of the index."""

    more_check = db.Column(db.Boolean(name='more_check'), nullable=False,
                             default=False)
    """More Status of the index."""

    display_no = db.Column(db.Integer, nullable=False, default=0)
    """Display number of the index."""

    harvest_public_state = db.Column(db.Boolean(name='harvest_public_state'),
                                     nullable=False, default=True)
    """Harvest public State of the index."""

    display_format = db.Column(db.Text,nullable=True, default='1')
    """The Format of Search Resault."""

    image_name = db.Column(db.Text, nullable=False,default='')
    """The Name of upload image."""

    public_state = db.Column(db.Boolean(name='public_state'), nullable=False,
                             default=False)
    """Public State of the index."""

    public_date = db.Column(
        db.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
        nullable=True)
    """Public Date of the index."""

    recursive_public_state = db.Column(
        db.Boolean(name='recs_public_state'), nullable=True, default=False)
    """Recursive Public State of the index."""

    browsing_role = db.Column(db.Text, nullable=True)
    """Browsing Role of the  ."""

    recursive_browsing_role = db.Column(
        db.Boolean(name='recs_browsing_role'), nullable=True, default=False)
    """Recursive Browsing Role of the index."""

    contribute_role = db.Column(db.Text, nullable=True)
    """Contribute Role of the index."""

    recursive_contribute_role = db.Column(
        db.Boolean(name='recs_contribute_role'), nullable=True, default=False)
    """Recursive Browsing Role of the index."""

    browsing_group = db.Column(db.Text, nullable=True)
    """Browsing Group of the  ."""

    recursive_browsing_group = db.Column(
        db.Boolean(name='recs_browsing_group'), nullable=True, default=False)
    """Recursive Browsing Group of the index."""

    contribute_group = db.Column(db.Text, nullable=True)
    """Contribute Group of the index."""

    recursive_contribute_group = db.Column(
        db.Boolean(name='recs_contribute_group'), nullable=True, default=False)
    """Recursive Browsing Group of the index."""

    owner_user_id = db.Column(db.Integer, nullable=True, default=0)
    """Owner user id of the index."""

    # index_items = db.relationship('IndexItems', back_populates='index', cascade='delete')

    def __iter__(self):
        for name in dir(Index):
            if not name.startswith('__') and not name.startswith('_') \
                 and name not in dir(Timestamp):
                value = getattr(self, name)
                if value is None:
                    value = ""
                if isinstance(value, str) or isinstance(value, bool) \
                        or isinstance(value, datetime) \
                        or isinstance(value, int):
                    yield (name, value)
    # format setting for community admin page

    def __str__(self):
        """Representation."""
        return 'Index <id={0.id}, index_name={0.index_name_english}>'.format(self)

# class IndexItems(db.Model):
#     """"""
#     __tablename__ = 'index_item'
#
#     id = db.Column(db.BigInteger,
#                    db.ForeignKey(Index.id),
#                    primary_key=True, nullable=False)
#     """Identifier of the index."""
#
#     rid = db.Column(UUIDType,
#                     db.ForeignKey(RecordMetadata.id,
#                                   ondelete='RESTRICT'),
#                     primary_key=True, nullable=False)
#     """Record identifier."""
#
#     index = db.relationship(Index, back_populates='index_item')


def index_removed_or_inserted(mapper, connection, target):
    current_app.config['WEKO_INDEX_TREE_UPDATED'] = True


listen(Index, 'after_insert', index_removed_or_inserted)
listen(Index, 'after_delete', index_removed_or_inserted)
listen(Index, 'after_update', index_removed_or_inserted)

class IndexStyle(db.Model, Timestamp):

    __tablename__ = 'index_style'

    id = db.Column(db.String(100), primary_key=True)
    """identifier for index style setting."""

    width = db.Column(db.Text, nullable=False, default='')
    """Index area width."""

    @classmethod
    def create(cls, community_id, **data):
        try:
            with db.session.begin_nested():
                obj = cls(id=community_id, **data)
                db.session.add(obj)
            db.session.commit()
            return obj
        except Exception as ex:
            current_app.logger.debug(ex)
            db.session.rollback()
        return

    @classmethod
    def get(cls, community_id):
        """Get a style."""
        return cls.query.filter_by(id=community_id).one_or_none()

    @classmethod
    def update(cls, community_id, **data):
        """
        Update the index detail info.

        :param index_id: Identifier of the index.
        :param detail: new index info for update.
        :return: Updated index info
        """
        try:
            with db.session.begin_nested():
                style = cls.get(community_id)
                if not style:
                    return

                for k, v in data.items():
                    if "width" in k:
                        setattr(style, k, v)
                db.session.merge(style)
            db.session.commit()
            return style
        except Exception as ex:
            current_app.logger.debug(ex)
            db.session.rollback()
        return


__all__ = ('Index',
           'IndexStyle',)
