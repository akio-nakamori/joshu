#!/usr/bin/env python
# -*- coding: utf-8 -*-

import db
import app
import sqlalchemy


class Unknown(object):
    _pk = None
    _path = None
    _ed2khash = None

    def __init__(self, path=None, ed2khash=None):
        super(Unknown, self).__init__()
        if path:
            self._path = path
        if ed2khash:
            self._ed2khash = ed2khash
        self._get_db_data()

    def _get_db_data(self, close=True):
        sess = db.get_session()
        if self._pk:
            res = sess.query(db.UnknownTable).filter_by(pk=self._pk).all()
        elif self._path:
            res = sess.query(db.UnknownTable).filter_by(path=self._path).all()
        if res and len(res) > 0:
            self.db_data = res[0]
            app.log("Found db_data for file: {}".format(self.db_data))
        self._close_db_session(sess)

    def _close_db_session(self, session):
         session.close()

    def _db_commit(self, session):
        try:
            session.commit()
            app.log("Object saved to database: {}".format(self.db_data))
        except sqlalchemy.exc.DBAPIError as e:
            if self.db_data:
                app.log("Failed to update data {}: {}".format(self.db_data, e))
            else:
                app.log("Failed to update db: {}".format(e))
            session.rollback()

    def add(self):
        new = Unknown(path=self._path, ed2khash=self._ed2khash)
        # commit to sql database
        sess = db.get_session()
        sess.add(new)

        if new:
            sess.db_data = new
            self._db_commit(sess)
            self._close_db_session(sess)
            self._updated.set()
