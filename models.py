"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.define_table(
    'user',
    Field('user_email', default=get_user_email, writable=False),
    Field('username', 'string'),
    Field('biography', 'string'),
)

db.define_table(
    'country',
    Field('name', 'string'),
    Field('biography', 'string'),
    Field('places', 'refernce place')
)

db.define_table(
    'place',
    Field('name', 'string'),
    Field('country', 'reference country'),
    Field('type', 'string')
)

db.define_table(
    'post',
    Field('username', 'reference user'),
    Field('content', 'string'),
    Field('likes', 'int'),
    Field('comments', 'string')
)

db.define_table(
    'comment',
    Field('post', 'refernece post'),
    Field('username', 'reference user'),
    Field('content', 'string'),
)

db.commit()
