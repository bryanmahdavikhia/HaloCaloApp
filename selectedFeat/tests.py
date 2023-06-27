from django.test import TestCase, RequestFactory
from uploadBarang import models as ub_md
from unittest.mock import MagicMock
from selectedFeat import views as vw
import uuid

DATE_STR = '2023-03-22 00:00:00'

class EventListViewTestCase(TestCase):
    def setUp(self):
        self.request = MagicMock()

    def test_event_list(self):
        self.request.method = 'GET'
        response = vw.event_list(self.request)
        self.assertEqual(response.status_code, 200)

class EventListWithSearchViewTestCase(TestCase):
    def setUp(self):
        self.request = MagicMock()

    def test_event_list_with_search(self):
        self.request.method = 'GET'
        self.request.GET = {'title': ''}
        response = vw.event_list_with_search(self.request)
        self.assertEqual(response.status_code, 200)

    def test_event_list_with_search_event_using_search(self):
        self.request.method = 'GET'
        self.request.GET = {'title': 'dewa'}
        response = vw.event_list_with_search(self.request)
        context = response.context_data
        events = context['events']
        self.assertGreater(len(events), 0)
        self.assertEqual(response.status_code, 200)

class ListingListViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = ub_md.User.objects.create(
            username='test',
            password='password123',
            is_admin=False,
            first_name='John',
            last_name='Doe',
            email='johndoe@example.com',
            tel_number='555-1234',
            is_seller=True,
        )

        self.listing = ub_md.Listing.objects.create(
            seller_username=self.user.username,
            is_sold=False,
            is_public=True,
            is_verified=True,
            event_id="0d9de09b-d7a1-4b28-b0f2-138201610fc6",
        )


    def test_listing_list_have_listing(self):
        request = self.factory.get('/')
        response = vw.listing_list(request, 'DEWA 19 - Pesta Rakyat')
        self.assertEqual(response.status_code, 200)

    def test_listing_list_not_have_listing(self):
        event_id = str(uuid.uuid4())
        event = ub_md.Events(
            id=event_id,
            category='Silver',
            date=DATE_STR,
            title='test',
            venue='test',
            image_url='test'
        )
        event.save()

        request = self.factory.get('/')
        response = vw.listing_list(request, 'test')
        self.assertEqual(response.status_code, 200)

        context = response.context_data
        msg = context['no_listings_message']
        self.assertEqual(msg, "No listings yet")

        event.delete()

    def test_listing_list_filtered_by_category(self):
        event_id = str(uuid.uuid4())
        event = ub_md.Events(
            id=event_id,
            category='Silver',
            date=DATE_STR,
            title='test',
            venue='test',
            image_url='test'
        )
        event.save()

        listing = ub_md.Listing(
            id=str(uuid.uuid4()),
            event_id=event_id,
            seller_username='test',
            is_public=True,
            is_verified=True
        )
        listing.save()

        request = self.factory.get('/', {'category': 'Silver'})
        response = vw.listing_list(request, 'test')

        self.assertEqual(response.status_code, 200)

        listing.delete()
        event.delete()

    def test_listing_list_filtered_by_invalid_category(self):
        event_id = str(uuid.uuid4())
        event = ub_md.Events(
            id=event_id,
            category='Silver',
            date=DATE_STR,
            title='test',
            venue='test',
            image_url='test'
        )
        event.save()

        listing = ub_md.Listing(
            id=str(uuid.uuid4()),
            event_id=event_id,
            seller_username='test',
            is_public=True,
            is_verified=True
        )
        listing.save()

        request = self.factory.get('/', {'category': 'Gold'})
        response = vw.listing_list(request, 'test')

        self.assertEqual(response.status_code, 200)

        listing.delete()
        event.delete()