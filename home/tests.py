from django.test import TestCase
from django.urls import reverse
from datetime import datetime
from uploadBarang.models import User, Events, Listing

class ViewsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a User object
        user = User.objects.create(
            username='testuser',
            email='testuser@example.com',
            password='testpass',
            first_name='John',
            last_name='Doe',
            tel_number='1234567890',
        )

        # Create an Event object
        event = Events.objects.create(
            title='Test Event',
            category='Test Category',
            date=datetime.now(),
            venue='Test Venue',
            image_url='https://example.com/image.jpg',
            banner_url='https://example.com/banner.jpg',
            banner_url_2='https://example.com/banner2.jpg',
        )

        # Create a Listing object
        listing = Listing.objects.create(
            seller_username='testuser',
            is_public=True,
            is_verified=True,
            is_sold=False,
            event_id=event.id
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_user_model(self):
        user = User.objects.get(username='testuser')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.tel_number, '1234567890')
        self.assertFalse(user.is_seller)

    def test_event_model(self):
        event = Events.objects.get(title='Test Event')
        self.assertEqual(event.category, 'Test Category')
        self.assertEqual(event.venue, 'Test Venue')
        self.assertEqual(event.image_url, 'https://example.com/image.jpg')
        self.assertEqual(event.banner_url, 'https://example.com/banner.jpg')
        self.assertEqual(event.banner_url_2, 'https://example.com/banner2.jpg')

    def test_listing_model(self):
        listing = Listing.objects.get(seller_username='testuser')
        self.assertTrue(listing.is_public)
        self.assertTrue(listing.is_verified)
        self.assertFalse(listing.is_sold)

    def tearDown(self):
        Listing.objects.filter(seller_username='testuser').delete()
        Events.objects.filter(title='Test Event').delete()
        User.objects.filter(username='testuser').delete()