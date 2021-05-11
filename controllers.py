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
    return dict()


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
