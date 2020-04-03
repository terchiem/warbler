"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

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

        self.user1 = User.signup("user1", "test1@test.com", "password", None)
        self.user2 = User.signup("user2", "test2@test.com", "password", None)
        
        db.session.commit()

        self.uid1 = self.user1.id
        self.uid2 = self.user2.id

    def tearDown(self):
        db.session.rollback()

    def setup_messages_and_likes(self):
        m1 = Message(text="user1 message", user_id=self.user1.id)
        m2 = Message(text="user2 message", user_id=self.user2.id)
        db.session.add_all([m1, m2])
        db.session.commit()

        self.m1_id = m1.id
        self.m2_id = m2.id

        like = Likes(user_id=self.user1.id, message_id=m2.id)
        db.session.add(like)
        db.session.commit()

    def test_users_show(self):
        """test user show profile page"""

        with self.client as c:

            resp = c.get(f'/users/{self.uid1}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@user1', html)
            self.assertIn('fa fa-map-marker', html)


    def test_invalid_user_profile(self):
        """test invalid user profile page"""

        with self.client as c:

            resp = c.get(f"/users/9999")

            self.assertEqual(resp.status_code, 404)


    def test_user_homepage(self):
        """test user_home_page"""
    
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

            resp = c.get(f"/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@user1', html)

    def test_homepage_loggedout(self):
        """Test if user is directed to home page when logged out"""

        with self.client as c:

            resp = c.get(f"/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sign up', html)

    def test_users_list(self):
        """Test if all the users show up on the /users"""
        with self.client as c:

            resp = c.get(f"/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@user1', html)
            self.assertIn('@user2', html)

    def test_user_search(self):
        """Check if search bar returns the correct user"""

        with self.client as c:  

            resp = c.get(f"/users?q=user1")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@user1', html)

    ##test for searching user that does not exist

    def test_user_follow(self):
        "Check if user1 follows user2, user1's following list goes up by one, and user 2 is followed by user 1"
        ### TODO: add html for following list number goes up

        with self.client as c:  
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

            ##user 1 follows user 2
            resp = c.post(f"/users/follow/{self.uid2}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            ##check if user 2 is followed by user 1
            resp = c.get(f"/users/{self.uid1}/followers")
            html_user2 = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@user2', html)
            self.assertIn('@user1',html_user2)

    def test_user_unfollow(self):
        """Check if user 1 unfollows user2, user1 does not exist in the following list of user 2. """

        with self.client as c:  
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1
        
            #initial condition (user 1 follows user 2)
            user1 = User.query.get(self.uid1)
            user2 = User.query.get(self.uid2)

            user1.following.append(user2)
            db.session.commit()

            #user 1 unfollows user2, user 2 does not existi in user 1 following list.
            resp = c.post(f"/users/stop-following/{self.uid2}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            #checking if user 1 does not exist in user 2 follower list.
            resp = c.get(f"/users/{self.uid2}/followers")
            html_user2 = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('@user2', html)
            self.assertNotIn('@user1', html_user2)
            
        
    def test_user_follow_unauthorized(self):
        """Check if user can follow another user while being unauthorized """

        with self.client as c:  

            resp = c.post(f"/users/follow/{self.uid2}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sign up', html)
            self.assertIn('Access unauthorized.', html)


    def test_like_page(self):  
        """check if liked messages show up on your likes list when logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

            self.setup_messages_and_likes()

            resp = c.get(f"/users/{self.uid1}/likes", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('user2 message', html)

    def test_user_likes_message(self):
        """"check if user can like a message and if it shows up in the like page"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid2

            #create messages for user 1 and user 2
            self.setup_messages_and_likes()       

            #user 2 likes the message of user1    

            resp = c.post(f"/messages/{self.m1_id}/like", follow_redirects=True)
            html = resp.get_data(as_text=True) 

            self.assertEqual(resp.status_code, 200)
            self.assertIn('user1 message', html)

    def test_user_unliking_message(self):
        """"check if user can unlike a message and if it does not show up in the like page"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1
            
            self.setup_messages_and_likes()

            resp = c.post(f"/messages/{self.m2_id}/like", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('user2 message', html)

    def test_log_in(self):
        """check if user can log in with the right password and username"""

        with self.client as c:

            resp = c.post("/login", data = {"username":"user1", "password":"password" }, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@user1', html)

            with c.session_transaction() as sess:
                self.assertEqual(sess.get("CURR_USER_KEY"), self.uid1)

    def test_log_out(self):
        """check if user can logout"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

            resp = c.get("/logout", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            with c.session_transaction() as sess:
                self.assertIsNone(sess.get("CURR_USER_KEY"))
