import os
import sys
import unittest
import json # For direct manipulation of users.json if needed

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, data_manager
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

# Create a Flask app instance for testing
# Load configuration for testing
# It's often better to use a separate config file for testing (e.g., config.TestConfig)
# For now, we'll modify the config directly.
app = create_app(SECRET_KEY='test_secret_key_for_auth') # Provide a dummy secret key
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for tests
app.config['LOGIN_DISABLED'] = False # Ensure login is not globally disabled

# Define a base path for data files if necessary, though data_manager should handle it
# DATA_FILE = data_manager.data_file # or the direct path if data_manager is not initialized yet

class AuthTests(unittest.TestCase):

    def setUp(self):
        """Set up test variables and initial state before each test."""
        self.client = app.test_client()

        # Store original users and then clear/prepare users.json for tests
        self.original_users_content = data_manager.read_users_file() # Read raw content
        self.original_users = data_manager.get_users() # Get parsed users

        # Define a standard test user
        self.test_user_username = "testuser"
        self.test_user_password = "password"
        self.test_user_hashed_password = generate_password_hash(self.test_user_password)

        # Clean up any existing test user to ensure a clean state for registration tests
        # And ensure no other users exist to simplify some tests
        users_for_setup = {} # Start with an empty user dict for a cleaner slate
        data_manager.save_users(users_for_setup)


    def tearDown(self):
        """Clean up and restore initial state after each test."""
        # Restore original users from the raw content
        data_manager.write_users_file(self.original_users_content)
        # Ensure data_manager reloads from file if it caches
        data_manager.users = data_manager.load_data()


    # Test Cases will be added here
    def test_successful_registration(self):
        """Test successful user registration."""
        response = self.client.post('/register', data={
            'username': self.test_user_username,
            'password': self.test_user_password,
            'confirm_password': self.test_user_password
        }, follow_redirects=True) # Follow redirect to check final destination and flashed messages

        self.assertEqual(response.status_code, 200) # Should redirect to login, then render login page

        # Check if user was actually created in the data store
        registered_user = User.get(self.test_user_username)
        self.assertIsNotNone(registered_user)
        self.assertEqual(registered_user.username, self.test_user_username)

        # Check for flashed message on the login page
        self.assertIn(b"Registration successful! Please login.", response.data)

    def test_registration_existing_username(self):
        """Test registration with an already existing username."""
        # First, create the user directly so they exist in the system
        existing_users = data_manager.get_users()
        existing_users[self.test_user_username] = {
            "username": self.test_user_username,
            "password_hash": self.test_user_hashed_password,
            "wallet_balance": 0
        }
        data_manager.save_users(existing_users)

        response = self.client.post('/register', data={
            'username': self.test_user_username, # Attempt to register with the same username
            'password': self.test_user_password,
            'confirm_password': self.test_user_password
        })

        self.assertEqual(response.status_code, 200) # Should re-render the registration form
        self.assertIn(b"Username already exists. Please choose a different one.", response.data)
        # Ensure the original user was not overwritten with a new hash or anything (optional, as User.get would fail later if so)
        user_in_db = User.get(self.test_user_username)
        self.assertTrue(check_password_hash(user_in_db.password_hash, self.test_user_password))

    def test_registration_password_mismatch(self):
        """Test registration with mismatching password and confirm_password."""
        response = self.client.post('/register', data={
            'username': self.test_user_username,
            'password': self.test_user_password,
            'confirm_password': 'adifferentpassword'
        })

        self.assertEqual(response.status_code, 200) # Should re-render the registration form
        self.assertIn(b"Passwords must match.", response.data)

        # Ensure user was not created
        self.assertIsNone(User.get(self.test_user_username))

    def test_successful_login(self):
        """Test successful user login."""
        # Pre-register the user
        users = data_manager.get_users()
        users[self.test_user_username] = {
            "username": self.test_user_username,
            "password_hash": self.test_user_hashed_password, # Use the pre-hashed password
            "wallet_balance": 0
        }
        data_manager.save_users(users)

        response = self.client.post('/login', data={
            'username': self.test_user_username,
            'password': self.test_user_password
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200) # Successful login redirects to index
        self.assertIn(b"Welcome", response.data) # Assuming 'Welcome' is on the index page after login

        # Check session variable (more direct way to confirm login)
        with self.client.session_transaction() as session:
            self.assertTrue(session.get('_user_id') == self.test_user_username)

    def test_login_wrong_password(self):
        """Test login with correct username but wrong password."""
        # Pre-register the user
        users = data_manager.get_users()
        users[self.test_user_username] = {
            "username": self.test_user_username,
            "password_hash": self.test_user_hashed_password,
            "wallet_balance": 0
        }
        data_manager.save_users(users)

        response = self.client.post('/login', data={
            'username': self.test_user_username,
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, 200) # Should re-render login form
        self.assertIn(b"Invalid username or password.", response.data)

        # Ensure user is not logged in
        with self.client.session_transaction() as session:
            self.assertIsNone(session.get('_user_id'))

    def test_login_nonexistent_user(self):
        """Test login with a username that does not exist."""
        response = self.client.post('/login', data={
            'username': "nonexistentuser",
            'password': "anypassword"
        })

        self.assertEqual(response.status_code, 200) # Should re-render login form
        self.assertIn(b"Invalid username or password.", response.data)

        # Ensure no user is logged in
        with self.client.session_transaction() as session:
            self.assertIsNone(session.get('_user_id'))

if __name__ == '__main__':
    unittest.main()
