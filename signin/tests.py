from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.sessions.backends.db import SessionStore
from django.db import connection
from django.contrib import messages
from django.http import HttpResponseRedirect
from signup.controllers import encrypt_password
from uploadBarang.models import User
   
class LoginTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.session = SessionStore()
        self.session.save()
        self.home_url = '/'

        user_password_encrypt = encrypt_password('testpassword')
        admin_password_encrypt = encrypt_password('adminpassword')

        self.test_user = User(
            password=user_password_encrypt,
            username='testuser',
            email='test@test.com',
            first_name='test',
            last_name='user',
            tel_number=0
        )
        self.test_user.save()

        self.admin_user = User(
            password=admin_password_encrypt,
            username='adminuser',
            email='admin@test.com',
            first_name='admin',
            last_name='user',
            is_admin=True,
            tel_number=0
        )
        self.admin_user.save()

    def tearDown(self):
        self.test_user.delete()
        self.admin_user.delete()

    def test_login_successful_user(self):
        # Test successful login with correct credentials
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('login'), {"username": "testuser", "password": "testpassword"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        self.assertTrue('username' in self.client.session) # check if session variable is set
        self.assertTrue('is_admin' in self.client.session)
        self.assertTrue('email' in self.client.session)
        self.assertTrue('first_name' in self.client.session)

    def test_login_successful_admin(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('login'), {"username": "adminuser", "password": "adminpassword"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin")
        self.assertTrue('username' in self.client.session) # check if session variable is set
        self.assertTrue('is_admin' in self.client.session)
        self.assertTrue('email' in self.client.session)
        self.assertTrue('first_name' in self.client.session)

    def test_already_login_successful_admin(self):
        response = self.client.post(reverse('login'), {"username": "adminuser", "password": "adminpassword"})
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, "/admin")
    
    def test_already_login_successful_user(self):
        response = self.client.post(reverse('login'), {"username": "testuser", "password": "testpassword"})
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertRedirects(response, '/')

    def test_login_failed(self):
        # Test login with incorrect password
        response = self.client.post(reverse('login'), {"username": "testuser", "password": "password"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login')) # check redirect url
        self.assertFalse('username' in self.client.session) # check if session variable is not set
        self.assertFalse('is_admin' in self.client.session)
        self.assertFalse('email' in self.client.session)
        self.assertFalse('first_name' in self.client.session)
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Login failed. Password incorrect.')

    def test_login_user_not_found(self):
        # Test login with non-existent user
        response = self.client.post(reverse('login'), {"username": "user", "password": "testpassword"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login')) # check redirect url
        self.assertFalse('username' in self.client.session) # check if session variable is not set
        self.assertFalse('is_admin' in self.client.session)
        self.assertFalse('email' in self.client.session)
        self.assertFalse('first_name' in self.client.session)
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Sorry we could not find your account.')

    def test_logout_view(self):
        # Login user
        login_url = reverse('login')
        response = self.client.post(login_url, {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)

        # Logout user
        logout_url = reverse('logout')
        response = self.client.get(logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.home_url)

    def test_logout_view_deletes_session_variables(self):
        # Set up session variables
        session = self.client.session
        session['username'] = 'testuser'
        session['is_admin'] = False
        session['email'] = 'test@test.com'
        session['first_name'] = 'test'
        session.save()

        # Logout user
        logout_url = reverse('logout')
        response = self.client.get(logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.home_url)

        # Check that session variables have been deleted
        session = self.client.session
        self.assertFalse(session.get('has_username', False))
        self.assertIsNone(session.get('username', None))
        self.assertIsNone(session.get('is_admin', None))
        self.assertIsNone(session.get('email', None))
        self.assertIsNone(session.get('first_name', None))

    def test_logout_view_handles_no_session_variables(self):
        # Logout user without any session variables set
        logout_url = reverse('logout')
        response = self.client.get(logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.home_url)



