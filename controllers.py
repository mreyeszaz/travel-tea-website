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
from .extract_info import extract_country_info, country_info, get_country_flag_link

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
        curr_email=get_user_email(),
        curr_name=n
    )

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
        r = db(db.auth_user.email == p["email"]).select().first()
        username = r.username
        p["username"] = username
        for like in post_likes:
            if like["is_like"]:
                p["likers"].append(like["name"])
            else:
                p["dislikers"].append(like["name"])

    return dict(posts=posts, 
                likes=likes, 
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
        image=request.json.get('image')
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

# @action('feed')
# @action.uses(db, auth.user, 'feed.html')
# def feed():
#     r = db(db.auth_user.email == get_user_email()).select().first()
#     n = r.first_name + " " + r.last_name if r is not None else "Unknown"
#     curr_username = r.username
#     return dict(
#         # COMPLETE: return here any signed URLs you need.
#         get_posts_url=URL('get_posts', signer=url_signer),
#         add_post_url=URL('add_post', signer=url_signer),
#         delete_url = URL('delete_post', signer=url_signer),
#         get_rating_url = URL('get_rating', signer=url_signer),
#         set_thumb_url = URL('set_thumb', signer=url_signer),
#         get_thumb_url = URL('get_thumb', signer=url_signer),
#         user_email = auth.current_user.get('email'),
#         user_name = auth.current_user.get('first_name') + " " + auth.current_user.get('last_name'),
#
#         get_likes_url=URL('get_likes', signer=url_signer),
#         add_like_url=URL('add_like', signer=url_signer),
#         flip_like_url=URL('flip_like', signer=url_signer),
#         delete_like_url=URL('delete_like', signer=url_signer),
#
#         curr_email=get_user_email(),
#         curr_name=n,
#         curr_username=curr_username
#     )
#
#
# # controllers needed for feed.html
# # loads up all the posts on the page
# @action('posts', method="GET")
# @action.uses(db, auth.user, session, url_signer.verify())
# def get_posts():
#     #
#     #
#     all_posts = []
#     main_posts = db(db.post.is_reply == None).select(orderby=~db.post.post_date).as_list()
#     for post in main_posts:
#         all_posts.append(post)
#         replies = db(db.post.is_reply == post.get("id")).select(orderby=~db.post.post_date).as_list()
#         for reply in replies:
#             all_posts.append(reply)
#
#     for post in all_posts:
#         post['user'] = get_name_from_email(post.get("email"))
#
#     return dict(posts=all_posts)
#
# @action('posts',  method="POST")
# @action.uses(db, auth.user)  # Needed stuff put inot action.uses
# def save_post():
#
#     #id might be NONE
#     id = request.json.get('id')
#
#     content = request.json.get('content')
#     is_reply = request.json.get('is_reply')
#
#     if (id == None):
#         id = db.post.insert(
#         content = content,
#
#         is_reply = is_reply
#         # is_reply = request.json.get('is_reply')
#         )
#     else:
#         db(db.post.id == id).update(content = content, is_reply = is_reply)
#         # db(db.post.id == id).update(content = request.json.get('content'), is_reply = request.json.get('is_reply'))
#
#     #
#     # If id is None=>this means that this is a new post needs te inserted inro db
#     # Else => If id is not None, then it needs to be updated into the db
#     return dict(content=content, id=id)
#
# @action('delete_post',  method="POST")
# @action.uses(db, auth.user, session, url_signer.verify())
# def delete_post():
#     db((db.post.email == auth.current_user.get("email")) &
#        (db.post.id == request.json.get('id'))).delete()
#     return "deleted post!"
#
# #get specific rating for the post
# @action('get_rating')
# @action.uses(db, url_signer.verify(),auth.user)
# def get_rating():
#     post_id = request.params.get('post_id')
#     email = auth.current_user.get('email')
#     assert post_id is not None
#     rating_entry = db((db.thumb.post_id == post_id) &
#                       (db.thumb.user_email == email)).select().first()
#
#     rating = rating_entry.rating if rating_entry is not None else 0
#     return dict(rating=rating)
#
#
#
#
# # receives whether thumb set or not
# @action('set_thumb', method="POST")
# @action.uses(url_signer.verify(), auth.user, db)
# def set_thumb():
#     post_id = request.json.get('post_id')
#     email = auth.current_user.get('email')
#     rating = request.json.get('rating')
#     db.thumb.update_or_insert(
#         ((db.thumb.post_id == post_id) & (db.thumb.user_email == email)),
#         user_email=email,
#         post_id=post_id,
#         rating=rating
#     )
#     return "thumb set!"
#
# @action('get_thumb')
# @action.uses(url_signer.verify(), db, auth.user)
# def get_thumb():
#     post_id = request.params.get('post_id')
#     rating = request.params.get('rating')
#     name_string = ""
#     comma_add = 0
#     # Select all thumbs that have same rating and post id
#     thumbs = db((db.thumb.rating == rating) &
#                 (db.thumb.post_id == post_id)).select().as_list()
#     # Append to name_string (STRING) the first/last names of users based on email present in thumbs
#     for t in thumbs:
#         if comma_add == 1:
#             name_string = name_string + ", "
#         # To access first and last name of user
#         user = db(db.auth_user.email == t['user_email']).select().first()
#         name_string = name_string + "" + user.first_name + " " + user.last_name
#         comma_add = 1
#     return dict(name_string=name_string)
#
#
# #@action('add_post', method='POST')
# #@action.uses(db, auth.user, url_signer.verify())
# #def add_post():
# #    r = db(db.auth_user.email == get_user_email()).select().first()
# #    n = r.username if r is not None else "Unknown"
#  #   pid = db.posts.insert(
#  #       post_text=request.json.get('post_text'),
#  #       username=n,
#  #       email=get_user_email(),
#  #   )
#  #   print(n)
#  #   return dict(id=pid, username=n, email=get_user_email())
#
#
# #@action('delete_post')
# #@action.uses(db, auth.user, url_signer.verify())
# #def delete_post():
# #    pid = request.params.get('id')
# #    db(db.posts.id == pid).delete()
# #    return "ok"
#
#
# @action('get_likes')
# @action.uses(url_signer.verify(), db)
# def get_likes():
#     return dict(likes=db(db.likes).select().as_list())
#
#
# @action('add_like', method="POST")
# @action.uses(url_signer.verify(), db)
# def add_like():
#     r = db(db.auth_user.email == get_user_email()).select().first()
#     n = r.first_name + " " + r.last_name if r is not None else "Unknown"
#     pid = db.likes.insert(
#         is_like=request.json.get('is_like'),
#         post=request.json.get('post'),
#         email=get_user_email(),
#         name=n,
#     )
#     return dict(id=pid)
#
#
# @action('flip_like', method="POST")
# @action.uses(url_signer.verify(), db)
# def flip_like():
#     like_id = request.json.get('id')
#     assert like_id is not None
#     new_val = request.json.get('is_like')
#     assert new_val is not None
#     db(db.likes.id == like_id).update(is_like=new_val)
#     return "ok"
#
#
# @action('delete_like', method="POST")
# @action.uses(url_signer.verify(), db)
# def delete_like():
#     like_id = request.json.get('id')
#     assert like_id is not None
#     db(db.likes.id == like_id).delete()
#     return "ok"

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
    country_bio = extract_country_info(country_name)
    return dict(country_name=country_name,
                country_bio=country_bio)

@action('insert_all_countries', method=["GET", "POST"])
@action.uses(db, auth.user)
def insert_all_countries():
    for country_obj in country_info:
        rating_id = db.country_rating.insert(
            beaches=0, 
            sights=0, 
            food=0, 
            nightlife=0, 
            shopping=0,
        )

        country_name = country_obj["name"]
        country_code = country_obj["code"]
        country_bio = extract_country_info(country_name)
        country_flag = get_country_flag_link(country_code)
        
        db.country.insert(
            name=country_name,
            code=country_code,
            biography=country_bio,
            thumbnail=country_flag,
            country_rating=rating_id,
        )

    return "ok"
