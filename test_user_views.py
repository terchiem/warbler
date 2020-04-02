"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()


    # test user show profile page
        # go to testuser's page
        # test for 200
        # test html for testuser name

    # test invalid user profile page
        # go to invalid user
        # test for 404

    # test user homepage
        # go to root
        # test for 200
        # test html for testuser details

    # test homepage logged out
        # log out
        # go to root
        # test for 200
        # test html for logged out page

    # test users list
        # go to '/users'
        # test for 200
        # test html for users

    # test user search
        # go to '/users' with param arguments
        # test for 200
        # test if user is in html

    # test user follow
        # post to '/users/follow/<int:follow_id>'
        # test for 200
        # check current user's following list

    # test user unfollow
        # post to '/users/stop-following/<int:follow_id>'
        # test for 200
        # check current user's following list is empty

    # test user follow unauthorized
        # log out
        # post to '/users/follow/<int:follow_id>'
        # test for 200
        # test for "Access unauthorized."

    # test user likes page
        # create msgs and likes
        # go to '/users/<int:user_id>/likes'
        # test for 200
        # check if liked messages are there

    # test user liking a message
        # make user2
        # make msg
        # test liking route for 200
        # test user's msg added to user's likes

    # test user unliking a message
        # make user2
        # make msg
        # make like
        # test liking route for 200
        # test user's msg is not in user's likes

    # test user liking a message unauthorized
        # log out
        # post to ''
        # test for 200
        # test for "Access unauthorized."

    # test user log in

    # test user log out
