"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

import uuid
import random

url_signer = URLSigner(session)

# controller for each page on website

@action('index')
@action.uses(db, auth, 'index.html')
def index():
    print("User:", get_user_email())
    return dict()


@action('profile')
@action.uses(db, auth.user, 'profile.html')
def profile():
    return dict()


@action('feed')
@action.uses(db, auth.user, 'feed.html')
def feed():
    r = db(db.auth_user.email == get_user_email()).select().first()
    n = r.first_name + " " + r.last_name if r is not None else "Unknown"
    return dict(
        # COMPLETE: return here any signed URLs you need.
        get_posts_url=URL('get_posts', signer=url_signer),
        add_post_url=URL('add_post', signer=url_signer),
        delete_post_url=URL('delete_post', signer=url_signer),
        get_likes_url=URL('get_likes', signer=url_signer),
        add_like_url=URL('add_like', signer=url_signer),
        flip_like_url=URL('flip_like', signer=url_signer),
        delete_like_url=URL('delete_like', signer=url_signer),
        curr_email=get_user_email(),
        curr_name=n
    )


@action('discover')
@action.uses(db, auth.user, 'discover.html')
def discover():
    return dict(
        search_url = URL('search', signer=url_signer),
    )


@action('search')
@action.uses()
def search():
    q = request.params.get("q")
    results = [q + ":" + str(uuid.uuid1()) for _ in range(random.randint(2, 6))]
    return dict(results=results)


# controllers needed for feed.html

@action('get_posts')
@action.uses(db, url_signer.verify())
def get_posts():
    posts = db(db.posts).select().as_list()
    likes = db(db.likes.email == get_user_email()).select().as_list()

    # Add all people who liked each post to each post
    for p in posts:
        post_likes = db(db.likes.post == p["id"]).select()
        p["likers"] = []
        p["dislikers"] = []
        for like in post_likes:
            if like["is_like"]:
                p["likers"].append(like["name"])
            else:
                p["dislikers"].append(like["name"])

    return dict(posts=posts, likes=likes)


@action('add_post', method='POST')
@action.uses(db, auth.user, url_signer.verify())
def add_post():
    r = db(db.auth_user.email == get_user_email()).select().first()
    n = r.first_name + " " + r.last_name if r is not None else "Unknown"
    pid = db.posts.insert(
        post_text=request.json.get('post_text'),
        name=n,
        email=get_user_email(),
    )
    return dict(id=pid, name=n, email=get_user_email())


@action('delete_post')
@action.uses(db, auth.user, url_signer.verify())
def delete_post():
    pid = request.params.get('id')
    db(db.posts.id == pid).delete()
    return "ok"


@action('get_likes')
@action.uses(url_signer.verify(), db)
def get_likes():
    return dict(likes=db(db.likes).select().as_list())


@action('add_like', method="POST")
@action.uses(url_signer.verify(), db)
def add_like():
    r = db(db.auth_user.email == get_user_email()).select().first()
    n = r.first_name + " " + r.last_name if r is not None else "Unknown"
    pid = db.likes.insert(
        is_like=request.json.get('is_like'),
        post=request.json.get('post'),
        email=get_user_email(),
        name=n,
    )
    return dict(id=pid)


@action('flip_like', method="POST")
@action.uses(url_signer.verify(), db)
def flip_like():
    like_id = request.json.get('id')
    assert like_id is not None
    new_val = request.json.get('is_like')
    assert new_val is not None
    db(db.likes.id == like_id).update(is_like=new_val)
    return "ok"


@action('delete_like', method="POST")
@action.uses(url_signer.verify(), db)
def delete_like():
    like_id = request.json.get('id')
    assert like_id is not None
    db(db.likes.id == like_id).delete()
    return "ok"
