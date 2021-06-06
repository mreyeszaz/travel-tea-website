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
import datetime

url_signer = URLSigner(session)


def get_time():
    return datetime.datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
    # return datetime.datetime.utcnow()


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

def get_userid():
    curr_user = db(db.auth_user.email == get_user_email()).select().first()
    return curr_user.id if curr_user is not None else "Unknown"

def get_biography():
    curr_user = db(db.auth_user.email == get_user_email()).select().first()
    return curr_user.biography if curr_user is not None else "Unknown"

def get_total_posts(db):
    num_posts = db(db.posts).count()
    print(num_posts)
    return num_posts

def get_place_components(place, category, properties):
    place_components = place.split(", ")
    type_of_place = ""

    if category == "poi":
        type_of_place = properties["category"]
        place_components.append(type_of_place)
        return place_components
    elif category == "address":
        place_name = place_components[0]
        place_components.insert(0, place_name)
        place_components.append(category)
    elif category == "neighborhood":
        place_name = place_components[0]
        place_components.insert(0, place_name)
        place_components.append(category)
    return place_components

    
# controller for each page on website

@action('index')
@action.uses(db, auth, session, 'index.html')
def index():
    explored = db(db.place).count()
    total_users = db(db.auth_user).count()
    return dict(name=user_name(),
                explored=explored,
                total_users=total_users)


@action('profile')
@action.uses(db, auth.user, 'profile.html')
def profile():
    return dict(
        user_name=user_name(),
        upload_thumbnail_url=URL('upload_thumbnail', signer=url_signer),
        delete_profilepic_url=URL('delete_profilepic', signer=url_signer),
        delete_post_url=URL('delete_post', signer=url_signer),
        curr_email=get_user_email(),
        get_profile_url=URL('get_profile'),
        get_posts_url=URL('get_posts'),
        add_bio_url=URL('add_bio', signer=url_signer),
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
@action.uses(db, auth.user)
def get_profile():
    curr_user = db(db.auth_user.email == get_user_email()).select().first()
    bio = curr_user.biography if curr_user is not None else "Unknown"
    tl = curr_user.thumbnail if curr_user is not None else "Unknown"
    uid = curr_user.id if curr_user is not None else "Unknown"
    return dict(
        tl=tl,
        uid=uid,
        bio=bio,
    )


@action('add_bio', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_bio():
    bio = request.json.get('bio')
    db.auth_user.update_or_insert(
        (db.auth_user.email == get_user_email()),
        biography=bio,
    )
    return "ok"


# TODO: UPDATE FEED

@action('feed')
@action.uses(db, auth.user, 'feed.html')
def feed():
    r = db(db.auth_user.email == get_user_email()).select().first()
    n = r.first_name + " " + r.last_name if r is not None else "Unknown"
    apostrophe = "'s"
    if n[-1] == "s": apostrophe = apostrophe[:-1]
    return dict(
        # COMPLETE: return here any signed URLs you need.
        get_posts_url=URL('get_posts'),
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
        curr_name=n,
        apostrophe=apostrophe,
        num_posts=get_total_posts(db)
    )


@action('get_posts')
@action.uses(db)
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

    # Add the location name, country and location type to each post
    for p in posts:
        place_id = p["place"]
        place_info = db(db.place.id == place_id).select().first()
        p["place_name"] = place_info.name
        p["place_address"] = place_info.address 
        p["place_city"] = place_info.city
        p["place_state"] = place_info.state
        country_info = db(db.country.id == place_info.country).select().first()
        p["country_id"] = country_info.id
        p["place_country"] = country_info.name
        p["place_kind"] = place_info.type

    return dict(posts=posts, 
                likes=likes,
                travels=travels,
                curr_user=get_user_email())


@action('add_post', method='POST')
@action.uses(db, auth.user, url_signer.verify())
def add_post():
    r = db(db.auth_user.email == get_user_email()).select().first()
    n = get_username()
    place = request.json.get('place')
    place_properties = request.json.get('place_properties')
    place_type = request.json.get('place_type')
    place_components = get_place_components(place, place_type, place_properties)
    print(place_components)
    if (len(place_components) < 6):
        name = place_components[0]
        address = place_components[0]
        *other, city, state, country, type = place_components
    else:
        name, address, *other, city, state, country, type = place_components
    print("Place added: ")
    print(place)
    print("Place properties: ")
    print(place_properties)
    print("Place type: ")
    print(place_type)
    print("------------------------")

    country_id = db(db.country.name == country).select().first()


    place_id = db.place.update_or_insert(
        name=name,
        address=address,
        city=city,
        state=state,
        country=country_id,
        type=type,
    )

    if not place_id:
        place_id = (db(db.place.name == name).select().first()).id

    pid = db.posts.insert(
        place=place_id,
        country=country,
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
        time=get_time(),
    )

    # Recalculate the country's average
    posts_about_country = db(db.posts.country == country).select(db.posts.beach, 
                                                                 db.posts.sights, 
                                                                 db.posts.food, 
                                                                 db.posts.night, 
                                                                 db.posts.shop)

    avg_beach = avg_sights = avg_food = avg_night = avg_shop = 0
    tot_posts = len(posts_about_country)
    country_info = db(db.country.id == country_id).select().first()
    country_rating_id = country_info.country_rating

    for p in posts_about_country:
        avg_beach += p.beach
        avg_sights += p.sights
        avg_food += p.food
        avg_night += p.night
        avg_shop += p.shop
    avg_beach /= tot_posts 
    avg_sights /= tot_posts
    avg_food /= tot_posts
    avg_night /= tot_posts
    avg_shop /= tot_posts

    db.country_rating.update_or_insert(
        db.country_rating.id == country_rating_id,
        beaches=avg_beach,
        sights=avg_sights,
        food=avg_food,
        nightlife=avg_night,
        shopping=avg_shop
    )
    print(avg_beach, avg_sights, avg_food, avg_night, avg_shop)

    return dict(id=pid, 
                name=n, 
                email=get_user_email(),
                place_name=name,
                place_address=address,
                place_city=city,
                place_state=state,
                place_kind=type,
                place_country=country,
                cid=country_id.id,
                time=get_time()
                )


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
    post_id = request.json.get('post')
    pid = db.likes.insert(
        is_like=request.json.get('is_like'),
        post=post_id,
        email=get_user_email(),
        name=n,
    )
    db(db.posts.id == post_id).update(
        num_like=request.json.get('num_like'),
        num_dislike=request.json.get('num_dislike'),
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

    post_id = request.json.get('post')
    db(db.posts.id == post_id).update(
        num_like=request.json.get('num_like'),
        num_dislike=request.json.get('num_dislike'),
    )
    return "ok"


@action('delete_like', method="POST")
@action.uses(url_signer.verify(), db)
def delete_like():
    like_id = request.json.get('id')
    assert like_id is not None
    db(db.likes.id == like_id).delete()

    post_id = request.json.get('post')
    db(db.posts.id == post_id).update(
        num_like=request.json.get('num_like'),
        num_dislike=request.json.get('num_dislike'),
    )
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
    post_id = request.json.get('post')
    db(db.posts.id == post_id).update(
        num_travel=request.json.get('num_travel'),
    )
    return dict(id=pid)


@action('delete_travel', method="POST")
@action.uses(url_signer.verify(), db)
def delete_travel():
    tid = request.json.get('id')
    assert tid is not None
    db(db.travels.id == tid).delete()

    post_id = request.json.get('post')
    db(db.posts.id == post_id).update(
        num_travel=request.json.get('num_travel'),
    )

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
        p = (db.posts.title.contains(qq))
    else:
        t = db.country.id > 0

    country_results = db(t).select(db.country.ALL).as_list()
    post_results = db(p).select(db.posts.ALL).as_list()
    return dict(country_results=country_results,
                post_results=post_results)


@action('faq')
@action.uses(auth, 'faq.html')
def faq():
    return dict()


@action('resources')
@action.uses(auth.user, 'resources.html')
def resources():
    return dict()


@action('review')
@action.uses(db, auth.user, 'review.html')
def review():
    # rows = db.review
    # rows = db(db.review).select()
    return dict(rows=db(db.review).select(), url_signer=url_signer)


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
    posts_info = db(db.posts.country == country_info.name).select()
    print("# OF POSTS: " + str(len(posts_info)))
    num_posts = len(posts_info)
    if num_posts < 1:
        db.country_rating.update_or_insert(
            db.country_rating.id == country_info.country_rating,
            beaches=0,
            sights=0,
            food=0,
            nightlife=0,
            shopping=0
        )

    assert country_info is not None
    country_name = country_info.name
    country_bio = country_info.biography
    country_flag = country_info.thumbnail
    country_rating_id = country_info.country_rating
    country_rating=country_rating_id
    rating_info = db(db.country_rating.id == country_rating_id).select().first()
    return dict(country_name=country_name,
                country_bio=country_bio, 
                country_flag=country_flag,
                country_rating=country_rating,
                beach=rating_info.beaches,
                sights=rating_info.sights,
                food=rating_info.food,
                night=rating_info.nightlife,
                shop=rating_info.shopping,
                get_country_rating_url=URL('get_country_rating',country_id),
                get_posts_url=URL('get_posts'),
                delete_post_url=URL('delete_post', signer=url_signer),
                get_country_url=URL('get_country', country_id),
                curr_email=get_user_email
                )

@action('get_country/<country_id:int>', method=["GET", "POST"])
@action.uses(db, auth.user)
def get_country(country_id=None):
    country_info = db(db.country.id == country_id).select().first()
    return dict(country_id=country_id, country_name=country_info.name)

@action('get_country_rating/<country_id:int>')
@action.uses(auth.user, db)
def get_country_rating(country_id=None):
    country = db(db.country.id == country_id).select().first()
    rating_id = country.country_rating
    ratings = db(db.country_rating.id == rating_id).select().as_list()
    return dict(ratings=ratings)


@action('insert_all_countries', method=["GET", "POST"])
@action.uses(db, auth.user)
def insert_all_countries():
    for country_obj in country_info:
        user = db(db.auth_user.email == get_user_email()).select().first()
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
        
        country_id = db.country.insert(
            name=country_name,
            code=country_code,
            biography=country_bio,
            thumbnail=country_flag,
            country_rating=rating_id,
        )

    return "ok"

@action('delete_all_countries', method=["GET", "POST"])
@action.uses(db, auth.user)
def delete_all_countries():
    db(db.country).delete()
    db(db.country_rating).delete()

    return "ok"


