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

# db.define_table("post",
#                 Field('email', default=get_user_email),
#                 Field('content', 'text'),
#                 Field('post_date', 'datetime', default=get_time),
#                 Field('is_reply', 'reference post'),
#                 )
#
# db.define_table('thumb',
#                 Field('user_email', default=get_user_email()),
#                 Field('post_id', 'reference post'),
#                 Field('rating', 'integer', default=0)
#                 )

db.define_table('country',
                Field('name', 'string'),
                Field('biography', 'string'),
                )

db.define_table('place',
                Field('name', 'string'),
                Field('country', 'reference country'),
                Field('thumbnail', 'text')
                )

db.define_table(
    'user',
    Field('user_email', default=get_user_email, writable=False),
    Field('username', 'string'),
    Field('biography', 'string'),
)

db.define_table('posts',
                Field('title', default=""),
                Field('post_text', default=""),
                Field('username', default=""),
                Field('email', default=get_user_email()),
                Field('user', 'reference auth_user'),
                Field('image', 'text', default=""),
                Field('overall', 'integer', default=0, IS_INT_IN_RANGE=(0, 6)),
                Field('beach', 'integer', default=0, IS_INT_IN_RANGE=(0, 11)),
                Field('sights', 'integer', default=0, IS_INT_IN_RANGE=(0, 11)),
                Field('food', 'integer', default=0, IS_INT_IN_RANGE=(0, 11)),
                Field('night', 'integer', default=0, IS_INT_IN_RANGE=(0, 11)),
                Field('shop', 'integer', default=0, IS_INT_IN_RANGE=(0, 11)),
                )

db.define_table('likes',
                Field('is_like', 'boolean'),
                Field('post', 'reference posts'),
                Field('name', default=""),
                Field('email', default=get_user_email()),
                )

db.define_table('travels',
                Field('has_traveled', 'boolean'),
                Field('post', 'reference posts'),
                Field('name', default=""),
                Field('email', default=get_user_email()),
                )

# db.define_table('user',
#                 Field('user_email', default=get_user_email(), reference=auth, writable=False),
#                 Field('user_name', 'string'),
#                 Field('biography', 'string'),
#                 Field('thumbnail', 'text'),
#                 )


db.define_table(
    'comment',
    Field('post', 'reference posts'),
    Field('username', 'reference user'),
    Field('content', 'string'),
)


db.define_table(
    'review',
    Field('author', 'string'),
    Field('email', default=get_user_email()),
    Field('rating', 'integer', default=0, requires=IS_INT_IN_RANGE(0, 11)),
    Field('description', 'text'),
)

db.review.id.readable = db.review.id.writable = False
db.review.email.writable = False
# db.review.user_email.readable = db.review.user_email.writable = False

db.commit()
