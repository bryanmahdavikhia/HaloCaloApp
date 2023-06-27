from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import connection
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
from detail import views as vw
import uuid
import json

class TestView(TestCase):
    def setUp(self):
        self.SIGNIN_URL = '/signin'
        self.LISTING_URL = '/listing/'

    def test_make_token_post(self):
        self.session = MagicMock()
        self.request = MagicMock()
        self.request.method = 'POST'
        listing_id = "616e889f-806f-4c8f-a812-ccb7beb65ba0"
        self.request.POST = {'listing_id': listing_id}
        response = vw.make_token(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.LISTING_URL + str(listing_id), response['Location'])
    
    def test_make_token_non_post(self):
        self.session = MagicMock()
        self.request = MagicMock()
        self.request.method = 'GET'
        response = vw.make_token(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.SIGNIN_URL, response['Location'])

    def test_change_availability_post(self):
        self.session = MagicMock()
        self.request = MagicMock()   
        self.request.method = 'POST'
        listing_id = "616e889f-806f-4c8f-a812-ccb7beb65ba0"
        vis_string = "true"
        self.request.POST = {'listing_id': listing_id, 'vis_string': vis_string}
        response = vw.change_availability(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.LISTING_URL + str(listing_id), response['Location'])

    def test_change_availability_non_post(self):
        self.session = MagicMock()
        self.request = MagicMock()   
        self.request.method = 'GET'
        response = vw.change_availability(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.SIGNIN_URL, response['Location'])

    def test_change_visibility_post(self):
        self.session = MagicMock()
        self.request = MagicMock()   
        self.request.method = 'POST'
        listing_id = "616e889f-806f-4c8f-a812-ccb7beb65ba0"
        vis_string = "true"
        self.request.POST = {'listing_id': listing_id, 'vis_string': vis_string}
        response = vw.change_visibility(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.LISTING_URL + str(listing_id), response['Location'])

    def test_change_visibility_non_post(self):
        self.session = MagicMock()
        self.request = MagicMock()   
        self.request.method = 'GET'
        response = vw.change_visibility(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.SIGNIN_URL, response['Location'])

    def test_viewlisting_with_valid_id(self):
        session = self.client.session
        session['username'] = 'testuser'
        session.save()
        response = self.client.get(f'/listing/616e889f-806f-4c8f-a812-ccb7beb65ba0')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail.html')

    def test_viewlisting_with_invalid_id(self):
        response = self.client.get(f'/listing/1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listing_unavailable.html')

    def test_check_listing_with_valid_id(self):
        result = vw.check_listing("616e889f-806f-4c8f-a812-ccb7beb65ba0")
        self.assertTrue(result)

    def test_check_listing_with_invalid_id(self):
        result = vw.check_listing("2")
        self.assertFalse(result)

    def test_validate_valid_token_post(self):
        data = {'token': 'b71ae5ba-6f12-432a-855e-ace41f2c1ceb'}
        response = self.client.post(reverse('validate_token'), json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'is_valid_token': True})

    def test_validate_invalid_token_post(self):
        data = {'token': '5678'}
        response = self.client.post(reverse('validate_token'), json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'is_valid_token': False})

    def test_validate_token_non_post(self):
        self.session = MagicMock()
        self.request = MagicMock()   
        self.request.method = 'GET'
        response = vw.validate_token(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.SIGNIN_URL, response['Location'])