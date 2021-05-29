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
from py4web.utils.form import Form, FormStyleBulma

import uuid
import random

url_signer = URLSigner(session)


def user_name():
    user = db(db.auth_user.email == get_user_email()).select().first()
    return user.first_name + " " + user.last_name if user else None


def get_tl():
    user = db(db.auth_user.email == get_user_email()).select().first()
    return user.thumbnail if user else None


def get_name_from_email(e):
    """Given the email of a user, returns the name."""
    user = db(db.auth_user.email == e).select().first()
    return "" if user is None else user.first_name + " " + user.last_name


def get_username():
    curr_user = db(db.auth_user.email == get_user_email()).select().first()
    return curr_user.username if curr_user is not None else "Unknown"


def get_biography():
    curr_user = db(db.auth_user.email == get_user_email()).select().first()
    return curr_user.biography if curr_user is not None else "Unknown"


# controller for each page on website

@action('index')
@action.uses(db, auth, session, 'index.html')
def index():
    return dict(name=user_name())


@action('profile')
@action.uses(db, auth.user, 'profile.html')
def profile():
    return dict(
        user_name=user_name(),
        upload_thumbnail_url=URL('upload_thumbnail', signer=url_signer),
        delete_profilepic_url=URL('delete_profilepic', signer=url_signer),
        curr_email=get_user_email(),
        get_profile_url=URL('get_profile', signer=url_signer),
        username=get_username(),
        bio=get_biography(),
    )


# controllers needed for profile.html


@action('upload_thumbnail', method="POST")
@action.uses(db, auth, url_signer.verify())
def upload_thumbnail():
    tl = request.json.get("tl")
    db.auth_user.update_or_insert(
        (db.auth_user.email == get_user_email()),
        thumbnail=tl
    )
    return "ok"


@action('delete_profilepic', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def delete_profilepic():
    db.auth_user.update_or_insert(
        (db.auth_user.email == get_user_email()),
        thumbnail=""
    )
    return "ok"


@action('get_profile')
@action.uses(db, auth.user, url_signer.verify())
def get_profile():
    tl = get_tl()
    return dict(
        tl=tl,
    )


# @action('edit_bio')
# @action.uses(db, auth.user, 'editProfile.html')
# def edit_profile():
#     edit = Form(db.auth_user, csrf_session=session, formstyle=FormStyleBulma)
#     tl = request.json.get("tl")
#     db.auth_user.update(
#         (db.auth_user.email == get_user_email()),
#         thumbnail=tl
#     )
#     if edit.accepted:  # post request
#         # We simply redirect; the insertion already happened.
#         redirect(URL('profile'))
#     # Either this is a GET request, or this is a POST but not accepted = with errors.
#     return dict(form=edit)


# TODO: UPDATE FEED

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
        get_travels_url=URL('get_travels', signer=url_signer),
        add_travel_url=URL('add_travel', signer=url_signer),
        delete_travel_url=URL('delete_travel', signer=url_signer),
        curr_email=get_user_email(),
        curr_name=n
    )

@action('get_posts')
@action.uses(db, url_signer.verify())
def get_posts():
    posts = db(db.posts).select().as_list()
    likes = db(db.likes.email == get_user_email()).select().as_list()
    travels = db(db.travels.email == get_user_email()).select().as_list()

    # Add all people who liked each post to each post
    for p in posts:
        post_likes = db(db.likes.post == p["id"]).select()
        p["likers"] = []
        p["dislikers"] = []
        r = db(db.auth_user.email == p["email"]).select().first()
        username = r.username
        p["username"] = username
        for like in post_likes:
            if like["is_like"]:
                p["likers"].append(like["name"])
            else:
                p["dislikers"].append(like["name"])

    # Add all people who has traveled to same place as post to each post
    for p in posts:
        post_travels = db(db.travels.post == p["id"]).select()
        p["travelers"] = []
        r = db(db.auth_user.email == p["email"]).select().first()
        username = r.username
        p["username"] = username
        for t in post_travels:
            if t["has_traveled"]:
                p["travelers"].append(t["name"])

    return dict(posts=posts, 
                likes=likes,
                travels=travels,
                curr_user=get_user_email())


@action('add_post', method='POST')
@action.uses(db, auth.user, url_signer.verify())
def add_post():
    r = db(db.auth_user.email == get_user_email()).select().first()
    n = get_username()
    pid = db.posts.insert(
        post_text=request.json.get('post_text'),
        username=n,
        email=get_user_email(),
        user=r.id,
        image=request.json.get('image'),
        title=request.json.get('title'),
        overall=request.json.get('overall'),
        beach=request.json.get('beach'),
        sights=request.json.get('sights'),
        food=request.json.get('food'),
        night=request.json.get('night'),
        shop=request.json.get('shop'),
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


@action('get_travels')
@action.uses(url_signer.verify(), db)
def get_travels():
    return dict(travels=db(db.travels).select().as_list())


@action('add_travel', method="POST")
@action.uses(url_signer.verify(), db)
def add_travel():
    r = db(db.auth_user.email == get_user_email()).select().first()
    n = r.first_name + " " + r.last_name if r is not None else "Unknown"
    pid = db.travels.insert(
        has_traveled=request.json.get('has_traveled'),
        post=request.json.get('post'),
        email=get_user_email(),
        name=n,
    )
    return dict(id=pid)


@action('delete_travel', method="POST")
@action.uses(url_signer.verify(), db)
def delete_travel():
    tid = request.json.get('id')
    assert tid is not None
    db(db.travels.id == tid).delete()
    return "ok"


# more page controllers

@action('discover')
@action.uses(db, auth.user, 'discover.html')
def discover():
    return dict(
        search_url=URL('search', signer=url_signer),
    )

# search controller for discover page

@action('search')
@action.uses()
def search():
    q = request.params.get("q")
    if q:
        qq = q.strip()
        t = (db.country.name.contains(qq))
    else:
        t = db.country.id > 0

    results = db(t).select(db.country.ALL).as_list()
    return dict(results=results)

# ------- THIS IS REFERENCE FOR SEARCH BAR -----
# @action('search_country')
# @action.uses(db, url_signer.verify())
# def get_products():
#     """Gets the list of products, possibly in response to a query."""
#     t = request.params.get('q')
#     if t:
#         tt = t.strip()
#         q = ((db.product.product_name.contains(tt)) |
#              (db.product.description.contains(tt)))
#     else:
#         q = db.product.id > 0
#     # This is a bit simplistic; normally you would return only some of
#     # the products... and add pagination... this is up to you to fix.
#     products = db(q).select(db.product.ALL).as_list()
#     # Fixes some fields, to make it easy on the client side.
#     for p in products:
#         p['desired_quantity'] = min(1, p['quantity'])
#         p['cart_quantity'] = 0
#     return dict(
#         products=products,
#     )


@action('faq')
@action.uses(auth, 'faq.html')
def faq():
    return dict()


@action('resources')
@action.uses(auth.user, 'resources.html')
def resources():
    return dict()


@action('review')
@action.uses(auth.user, 'review.html')
def review():
    rows = db(db.review.email == get_user_email()).select()
    # rows = db(db.review).select()
    return dict(rows=rows, url_signer=url_signer)


@action('reviewForm', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'reviewForm.html')
def reviewForm():
    # Insert form: no record= in it.
    revForm = Form(db.review, csrf_session=session, formstyle=FormStyleBulma)
    if revForm.accepted:  # post request
        # We simply redirect; the insertion already happened.
        redirect(URL('review'))
    # Either this is a GET request, or this is a POST but not accepted = with errors.
    return dict(form=revForm)

@action('random_location', method=["GET"])
@action.uses(db, auth.user, "random_location.html")
def random_location():
    country_ids = db().select(db.country.id).as_list()
    id_list = [country['id'] for country in country_ids]
    random_location_id = random.choice(id_list)
    random_location = db(db.place.id == random_location_id).select().first()
    redirect(URL('country_profile', random_location_id))

@action('country_profile/<country_id:int>', method=["GET", "POST"])
@action.uses(db, auth.user, "country_profile.html")
def country_profile(country_id=None):
    assert country_id is not None

    country_info = db(db.country.id == country_id).select().first()
    assert country_info is not None
    country_name = country_info.name
    country_bio = country_info.biography
    return dict(country_name=country_name,
                country_bio=country_bio)
