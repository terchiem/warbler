"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows
from psycopg2 import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

app.config['TESTING'] = True

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        test_user_1 = User.signup(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD",
            image_url="random_url"
        )

        test_user_2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD",
            image_url="random_url"
        )

        db.session.commit()

        self.user1 = test_user_1
        self.user2 = test_user_2

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.user1.messages), 0)
        self.assertEqual(len(self.user1.followers), 0)
    
    def test_user_repr(self):
        """Does User Repr work?"""

        self.assertEqual(self.user1.__repr__(), f"<User #{self.user1.id}: {self.user1.username}, {self.user1.email}>")

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        # userone = User.query.get(self.user1.id)
        # usertwo = User.query.get(self.user2.id)
        # userone.following.append(usertwo)
        # db.session.commit()
        # self.assertEqual(usertwo.is_followed_by(userone), True)

        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(self.user1.is_following(self.user2), True)

        """Does is_following successfully detect when user1 is not following user2?"""

        self.user1.following.pop()
        db.session.commit()

        self.assertEqual(self.user1.is_following(self.user2), False)

    ##do not put docstring inside of the middle of the function/ DOCSTRING VERY FIRST THING IN THE FUNCTION
    ##try to divide tests (one question per test)
    ##line 103 -> python knows that you added in following but inside of the database it's not going to be added until you session.add(user2) (since talking to database itself is expensive)

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""
        self.user2.following.append(self.user1)
        db.session.commit()
        
        self.assertEqual(self.user1.is_followed_by(self.user2), True)

        self.user2.following.append(self.user1)
        db.session.commit()

        self.assertEqual(self.user1.is_followed_by(self.user2), True)

        """Does is_followed_by successfully detect when user1 is not followed by user2?"""

        self.user2.following.pop()
        db.session.commit()

        self.assertEqual(self.user1.is_followed_by(self.user2), False)
    
    def test_singup(self):
        """Does User.create successfully create a new user given valid credentials?"""

        User.query.delete()

        test_user = User.signup("test1","testemail","password","randomurl")
        db.session.commit()

        self.assertEqual(len(User.query.all()), 1)
        self.assertEqual(test_user.username, 
                         "test1",)
        self.assertEqual(test_user.email, 
                        "testemail",)
        self.assertNotEqual(test_user.password,
                        "password",)

        """Does User.create fail to create a new user if any of the validations?"""


        self.assertEqual(len(User.query.all()), 1)

        User.signup("test1","testemail","password","randomurl")

        with self.assertRaises(exc.IntegrityError): 
            db.session.commit()

        ##

    def test_authenticate(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""

        self.assertEqual(User.authenticate(self.user1.username, "HASHED_PASSWORD"), self.user1)

        """Does User.authenticate fail to return a user when the username is invalid?"""

        self.assertEqual(User.authenticate("wrong_username", "HASHED_PASSWORD"), False)

        """Does User.authenticate fail to return a user when the password is invalid?"""

        self.assertEqual(User.authenticate(self.user1.username, "WRONG_PASSWORD"), False)
