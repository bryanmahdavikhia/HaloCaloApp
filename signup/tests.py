from django.test import TestCase
from django.db import connection
from django.contrib.sessions.backends.db import SessionStore

from unittest.mock import MagicMock

from signup import views as vw
from signup import controllers as cr
from uploadBarang import models as ub_md

class SignUpViewTest(TestCase):
    def setUp(self):
        self.request = MagicMock()

    def test_request_method_get(self):
        self.request.method = 'GET'
        self.response = vw.signup(self.request)

        self.assertEqual(self.response.status_code, 200)

    def test_request_method_not_get_not_post(self):
        self.request.method = 'PUT'
        self.response = vw.signup(self.request)

        self.assertEqual(self.response.status_code, 405)

    def test_request_method_post_password_less_than_eight(self):
        self.request.method = 'POST'
        self.request.POST = {
            'email': 'user_less_than_8@gmail.com',
            'username': 'user_less_than_8',
            'password1': '12345',
            'password2': '12345',
            'f_name': 'test_user',
            'l_name': 'signup',
            'tel_num': '0231231242194'
        }

        self.response = vw.signup(self.request)

        try:
            self.get_created_user = ub_md.User.objects.get(username=self.request.POST['username'])
        except ub_md.User.DoesNotExist:
            self.get_created_user = None

        self.assertIsNone(self.get_created_user)

    def test_request_method_post_user_already_exist(self):
        self.request.method = 'POST'
        self.request.POST = {
            'email': 'ralfidzaky@gmail.com',
            'username': 'ralfidzaky',
            'password1': '12345678',
            'password2': '12345678',
            'f_name': 'test_user',
            'l_name': 'signup',
            'tel_num': '0231231242194'
        }

        self.response = vw.signup(self.request)
        self.get_created_user = ub_md.User.objects.get(username=self.request.POST['username'])
        self.assertIsNotNone(self.get_created_user)

    def test_request_method_post_password_diff(self):
        self.request.method = 'POST'
        self.request.POST = {
            'email': 'user_pass_beda@gmail.com',
            'username': 'user_pass_beda',
            'password1': '12345678',
            'password2': '87654321',
            'f_name': 'test_user',
            'l_name': 'signup',
            'tel_num': '0231231242194'
        }

        self.response = vw.signup(self.request)

        try:
            self.get_created_user = ub_md.User.objects.get(username=self.request.POST['username'])
        except ub_md.User.DoesNotExist:
            self.get_created_user = None

        self.assertIsNone(self.get_created_user)

    def test_request_method_post_work(self):
        self.request.method = 'POST'
        self.request.POST = {
            'email': 'user_ok@gmail.com',
            'username': 'user_ok',
            'password1': '12345678',
            'password2': '12345678',
            'f_name': 'test_user',
            'l_name': 'signup',
            'tel_num': '0231231242194'
        }
        self.response = vw.signup(self.request)

        try:
            self.get_created_user = ub_md.User.objects.get(username=self.request.POST['username'])
        except ub_md.User.DoesNotExist:
            self.get_created_user = None

        self.assertIsNotNone(self.get_created_user)
        self.assertEqual(self.response.status_code, 302)

        if self.get_created_user is not None:
            self.get_created_user.delete()

class ControllerTest(TestCase):
    def test_enrypt_decrypt_password(self):
        original_password = '12345678'
        hashed_password = cr.encrypt_password(original_password)
        create_mock_user = ub_md.User(
            password=hashed_password,
            username='test_model_user',
            first_name='test',
            last_name='test',
            email='test_model_user@test.com',
            tel_number='12345'
        )
        result = cr.decrypt_password(create_mock_user, '12345678')
        print(result)