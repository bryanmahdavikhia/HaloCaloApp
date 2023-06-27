from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from django.db import connection
from django.core import mail
from unittest import mock
import uuid

from .views import check_admin, index, events

from verifikasiBarang import controllers as cr
from uploadBarang import models as ub_md

# Global
RALFIDZAKY_STR = 'ralfidzaky'
LISTING_ID_STR = 'fdb3b1e6-4eca-4e7d-bed3-23925fc35a2f'

class TestSendEmails(TestCase):
    def test_send_to_accepted_user(self):
        username = RALFIDZAKY_STR
        cr.send_user_accepted_email(username)

        try:
            self.get_user = ub_md.User.objects.get(username=username)
        except ub_md.User.DoesNotExist:
            self.get_user = None
        user_email = self.get_user.email

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'HaloCalo - Account Verification Accepted')
        self.assertEqual(mail.outbox[0].from_email, 'halocalo.dev@gmail.com')
        self.assertEqual(mail.outbox[0].to, [user_email])

    def test_send_to_rejected_user(self):
        username = RALFIDZAKY_STR
        cr.send_user_rejected_email(username)

        try:
            self.get_user = ub_md.User.objects.get(username=username)
        except ub_md.User.DoesNotExist:
            self.get_user = None
        user_email = self.get_user.email

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'HaloCalo - Account Verification Rejected')
        self.assertEqual(mail.outbox[0].from_email, 'halocalo.dev@gmail.com')
        self.assertEqual(mail.outbox[0].to, [user_email])

    def test_send_to_accepted_listing(self):
        listing_id = LISTING_ID_STR
        cr.send_listing_accepted_email(listing_id)

        try:
            self.get_listing = ub_md.Listing.objects.get(id=listing_id)
        except ub_md.Listing.DoesNotExist:
            self.get_listing = None
        listing_seller_username = self.get_listing.seller_username
        
        try:
            self.get_user = ub_md.User.objects.get(username=listing_seller_username)
        except ub_md.User.DoesNotExist:
            self.get_user = None
        user_email = self.get_user.email


        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'HaloCalo - Listing Document Accepted')
        self.assertEqual(mail.outbox[0].from_email, 'halocalo.dev@gmail.com')
        self.assertEqual(mail.outbox[0].to, [user_email])

    def test_send_to_rejected_listing(self):
        listing_id = LISTING_ID_STR
        cr.send_listing_rejected_email(listing_id)

        try:
            self.get_listing = ub_md.Listing.objects.get(id=listing_id)
        except ub_md.Listing.DoesNotExist:
            self.get_listing = None
        listing_seller_username = self.get_listing.seller_username
        
        try:
            self.get_user = ub_md.User.objects.get(username=listing_seller_username)
        except ub_md.User.DoesNotExist:
            self.get_user = None
        user_email = self.get_user.email

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'HaloCalo - Listing Document Rejected')
        self.assertEqual(mail.outbox[0].from_email, 'halocalo.dev@gmail.com')
        self.assertEqual(mail.outbox[0].to, [user_email])

class TestView(TestCase):
    def setUp(self):
        self.SIGNIN_URL = '/signin'

    def test_index_as_admin(self):
        session = self.client.session
        session['username'] = 'admin'
        session['is_admin'] = True
        session.save()

        response = self.client.get(reverse(index))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'adminhub.html')

    def test_index_as_nonadmin(self):
        session = self.client.session
        session['username'] = 'user'
        session['is_admin'] = False
        session.save()

        response = self.client.get(reverse(index))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.SIGNIN_URL, response['Location'])

    def test_verify_listing_as_admin(self):
        session = self.client.session
        session['username'] = 'admin'
        session['is_admin'] = True
        session.save()

        uuid = '616e889f-806f-4c8f-a812-ccb7beb65ba0'
        response = self.client.get(reverse('verify_listing', args=[uuid]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual('/admin/listing-verification', response['Location'])

    def test_verify_listing_as_nonadmin(self):
        session = self.client.session
        session['username'] = 'user'
        session['is_admin'] = False
        session.save()

        response = self.client.get(reverse('verify_listing', args=[1]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.SIGNIN_URL, response['Location'])

    def test_verify_seller_as_admin(self):
        session = self.client.session
        session['username'] = 'admin'
        session['is_admin'] = True
        session.save()

        username = 'john_doe'
        response = self.client.get(reverse('verify_seller', args=[username]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual('/admin/seller-verification', response['Location'])

    def test_verify_seller_as_nonadmin(self):
        session = self.client.session
        session['username'] = 'user'
        session['is_admin'] = False
        session.save()

        response = self.client.get(reverse('verify_seller', args=['seller']))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.SIGNIN_URL, response['Location'])

    def test_reject_listing_as_admin(self):
        session = self.client.session
        session['username'] = 'admin'
        session['is_admin'] = True
        session.save()

        self.listing_id = '616e889f-806f-4c8f-a812-ccb7beb65ba0'

        data = {'notes': 'This listing is not appropriate'}
        response = self.client.post(reverse('reject_listing', args=[self.listing_id]), data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual('/admin/listing-verification', response['Location'])

        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("SELECT is_verified FROM listing WHERE id = %s;", [self.listing_id])
        result = cursor.fetchone()
        cursor.close()
        self.assertFalse(result[0])

    def test_reject_listing_as_nonadmin(self):
        session = self.client.session
        session['username'] = 'nonadmin'
        session['is_admin'] = False
        session.save()

        self.listing_id = '616e889f-806f-4c8f-a812-ccb7beb65ba0'

        data = {'notes': 'This listing is not appropriate'}
        response = self.client.post(reverse('reject_listing', args=[self.listing_id]), data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.SIGNIN_URL, response['Location'])

    def test_reject_seller_as_admin(self):
        session = self.client.session
        session['username'] = 'admin'
        session['is_admin'] = True
        session.save()

        self.seller_username = 'mrizkyca'

        data = {'notes': 'This seller is not appropriate'}
        response = self.client.post(reverse('reject_seller', args=[self.seller_username]), data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual('/admin/seller-verification', response['Location'])

        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("SELECT is_seller FROM auth_user WHERE username = %s;", [self.seller_username])
        result = cursor.fetchone()
        cursor.close()
        self.assertFalse(result[0])

    def test_reject_seller_as_nonadmin(self):
        session = self.client.session
        session['username'] = 'user'
        session['is_admin'] = False
        session.save()

        self.seller_username = 'seller'

        response = self.client.post(reverse('reject_seller', args=['seller_username']), data={'notes': 'Reason for rejection'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.SIGNIN_URL, response['Location'])

    def test_events_as_admin(self):
        session = self.client.session
        session['username'] = 'admin'
        session['is_admin'] = True
        session.save()
        
        response = self.client.get(reverse('events'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events.html')

    def test_events_as_non_admin(self):
        session = self.client.session
        session['username'] = 'user'
        session['is_admin'] = False
        session.save()

        response = self.client.get(reverse('events'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.SIGNIN_URL, response['Location'])