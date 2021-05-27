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

def get_name_from_email(e):
    """Given the email of a user, returns the name."""
    user = db(db.auth_user.email == e).select().first()
    return "" if user is None else user.first_name + " " + user.last_name


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
        # get_profile_url=URL('get_profile', signer=url_signer),
        # add_thumbnail_url=URL('add_thumbnail', signer=url_signer),
    )


# controllers needed for profile.html


@action('upload_thumbnail', method="POST")
@action.uses(db, auth, url_signer.verify())
def upload_thumbnail():
    # name = db(db.auth_user.email == get_user_email()).first_name
    # tl = request.json.get("tl")
    # db(db.user.id).update(thumbnail=tl)
    # db(db.user.id).update(thumbnail=thumbnail)
    return "ok"


@action('delete_profilepic', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def delete_profilepic():
    db(db.user.user_email == get_user_email()).thumbnail = ""
    return "ok"

#
# @action('get_profile')
# @action.uses(db, url_signer.verify())
# def get_profile():
#     users = db(db.user).select().as_list()
#
#     return dict(users=users)


# @action('add_thumbnail')
# @action.uses(db, auth.user, url_signer.verify())
# def add_thumbnail():
#     r = db(db.auth_user.email == get_user_email()).select().first()
#     n = r.first_name + " " + r.last_name if r is not None else "Unknown"
#     uid = db.user.insert(
#         user_email=get_user_email(),
#         user_name=n,
#         thumbnail=request.json.get('thumbnail'),
#     )
#     return dict(id=uid, email=get_user_email())


@action('feed')
@action.uses(db, auth.user, 'feed.html')
def feed():
    r = db(db.auth_user.email == get_user_email()).select().first()
    n = r.first_name + " " + r.last_name if r is not None else "Unknown"
    curr_username = r.username
    return dict(
        # COMPLETE: return here any signed URLs you need.
        get_posts_url=URL('get_posts', signer=url_signer),
        add_post_url=URL('add_post', signer=url_signer),
        posts_url = URL('posts', signer=url_signer),
        delete_url = URL('delete_post', signer=url_signer),
        get_rating_url = URL('get_rating', signer=url_signer),
        set_thumb_url = URL('set_thumb', signer=url_signer),
        get_thumb_url = URL('get_thumb', signer=url_signer),
        user_email = auth.current_user.get('email'),
        user_name = auth.current_user.get('first_name') + " " + auth.current_user.get('last_name'),
        
        get_likes_url=URL('get_likes', signer=url_signer),
        add_like_url=URL('add_like', signer=url_signer),
        flip_like_url=URL('flip_like', signer=url_signer),
        delete_like_url=URL('delete_like', signer=url_signer),

        curr_email=get_user_email(),
        curr_name=n,
        curr_username=curr_username
    )


# controllers needed for feed.html
# loads up all the posts on the page
@action('posts', method="GET")
@action.uses(db, auth.user, session, url_signer.verify())
def get_posts():
    # 
    # 
    all_posts = []
    main_posts = db(db.post.is_reply == None).select(orderby=~db.post.post_date).as_list()
    for post in main_posts:
        all_posts.append(post)
        replies = db(db.post.is_reply == post.get("id")).select(orderby=~db.post.post_date).as_list()
        for reply in replies:
            all_posts.append(reply)

    for post in all_posts:
        post['user'] = get_name_from_email(post.get("email"))

    return dict(posts=all_posts)

@action('posts',  method="POST")
@action.uses(db, auth.user)  # Needed stuff put inot action.uses
def save_post():
   
    #id might be NONE 
    id = request.json.get('id') 

    content = request.json.get('content')
    is_reply = request.json.get('is_reply')

    if (id == None):
        id = db.post.insert(
        content = content,
        
        is_reply = is_reply
        # is_reply = request.json.get('is_reply')
        )
    else:
        db(db.post.id == id).update(content = content, is_reply = is_reply)
        # db(db.post.id == id).update(content = request.json.get('content'), is_reply = request.json.get('is_reply'))

    #
    # If id is None=>this means that this is a new post needs te inserted inro db
    # Else => If id is not None, then it needs to be updated into the db
    return dict(content=content, id=id)

@action('delete_post',  method="POST")
@action.uses(db, auth.user, session, url_signer.verify())
def delete_post():
    db((db.post.email == auth.current_user.get("email")) &
       (db.post.id == request.json.get('id'))).delete()
    return "deleted post!"
#get specific rating for the post 
@action('get_rating')
@action.uses(db, url_signer.verify(),auth.user)
def get_rating():
    post_id = request.params.get('post_id')
    email = auth.current_user.get('email')
    assert post_id is not None
    rating_entry = db((db.thumb.post_id == post_id) &
                      (db.thumb.user_email == email)).select().first()
                    
    rating = rating_entry.rating if rating_entry is not None else 0
    return dict(rating=rating)



    
# receives whether thumb set or not
@action('set_thumb', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def set_thumb():
    post_id = request.json.get('post_id')
    email = auth.current_user.get('email')
    rating = request.json.get('rating')
    db.thumb.update_or_insert(
        ((db.thumb.post_id == post_id) & (db.thumb.user_email == email)),
        user_email=email,
        post_id=post_id,
        rating=rating
    )
    return "thumb set!"

@action('get_thumb')
@action.uses(url_signer.verify(), db, auth.user)
def get_thumb():
    post_id = request.params.get('post_id')
    rating = request.params.get('rating')
    name_string = ""
    comma_add = 0
    # Select all thumbs that have same rating and post id
    thumbs = db((db.thumb.rating == rating) &
                (db.thumb.post_id == post_id)).select().as_list()
    # Append to name_string (STRING) the first/last names of users based on email present in thumbs
    for t in thumbs:
        if comma_add == 1:
            name_string = name_string + ", "
        # To access first and last name of user
        user = db(db.auth_user.email == t['user_email']).select().first()
        name_string = name_string + "" + user.first_name + " " + user.last_name
        comma_add = 1
    return dict(name_string=name_string)


@action('add_post', method='POST')
@action.uses(db, auth.user, url_signer.verify())
def add_post():
    r = db(db.auth_user.email == get_user_email()).select().first()
    n = r.username if r is not None else "Unknown"
    pid = db.posts.insert(
        post_text=request.json.get('post_text'),
        username=n,
        email=get_user_email(),
    )
    print(n)
    return dict(id=pid, username=n, email=get_user_email())


#@action('delete_post')
#@action.uses(db, auth.user, url_signer.verify())
#def delete_post():
#    pid = request.params.get('id')
#    db(db.posts.id == pid).delete()
#    return "ok"


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
    results = [q + ":" + str(uuid.uuid1()) for _ in range(random.randint(2, 6))]
    return dict(results=results)


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
    # rows = db(db.review.user_email == get_user_email()).select()
    rows = db(db.review).select()
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
    generated_id = 0
    location = db(db.place.id == generated_id).select().first()