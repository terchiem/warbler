"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows, Likes

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


        db.session.commit()

        self.user1 = test_user_1

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(text="test message", user_id=self.user1.id)

        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.text, "test message")
        self.assertIsNotNone(m.timestamp)
    

    def test_create_message(self):
        """ Does a message get added to a user's list of messages? """
    
        m = Message(text="test message", timestamp=None, user_id=self.user1.id)
        
        db.session.add(m)
        db.session.commit()

        # does the message get added to the user's message list?
        self.assertEqual(len(self.user1.messages), 1)

        # does the user's message text match what was created?
        self.assertEqual(self.user1.messages[0].text, "test message")


    def test_liking_message(self):
        """ Can a user like a message? """

        user2 = User.signup(
            email="test2",
            username="test2",
            password="password",
            image_url="random_url"
        )

        m = Message(text="test message", timestamp=None, user_id=self.user1.id)
        
        db.session.add(m)
        db.session.commit()

        like = Likes(user_id=user2.id, message_id=m.id)

        db.session.add(like)
        db.session.commit()

        # is message added to user's likes?
        self.assertEqual(len(user2.likes), 1)

        # does the user's liked message match the original message?
        self.assertEqual(user2.likes[0].id, m.id)

