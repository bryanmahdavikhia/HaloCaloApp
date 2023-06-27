from django.test import Client, TestCase
from django.urls import reverse
from datetime import datetime
from uploadBarang.models import User, Events, Listing
from signup.controllers import encrypt_password

class ViewsTestCase(TestCase):

    @classmethod
    def setUpTestData(self):

        self.client = Client()

        # Create a User object
        user_password_encrypt = encrypt_password('testpassword')

        self.user = User.objects.create(
            username='testuser',
            email='testuser@example.com',
            password=user_password_encrypt,
            first_name='John',
            last_name='Doe',
            tel_number='1234567890',
        )   
        # Create an Event object
        self.event = Events.objects.create(
            title='Test Event',
            category='Test Category',
            date=datetime.now(),
            venue='Test Venue',
            image_url='https://example.com/image.jpg',
        )   
        # Create a Listing object
        self.listing = Listing.objects.create(
            seller_username='testuser',
            is_public=True,
            is_verified=True,
            is_sold=False,
            event_id=self.event.id
        )

    def test_profile_view_with_authenticated_user(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('index'))
    
        # Perform the remaining assertions on the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userprofile.html')
        self.assertQuerysetEqual(response.context['activelistings'], [])
        self.assertQuerysetEqual(response.context['processinglistings'], [])
        self.assertQuerysetEqual(response.context['rejectedlistings'], [])

    def test_index_view_with_unauthenticated_user(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/signin")

    def tearDown(self):
        self.listing.delete()
        self.event.delete()
        self.user.delete()

class ProfilePageTest(TestCase):

    @classmethod
    def setUpTestData(self):

        self.client = Client()        
        user_password_encrypt = encrypt_password('testpassword')

        self.user = User.objects.create(
            username='testuser',
            email='testuser@example.com',
            password=user_password_encrypt,
            first_name='John',
            last_name='Doe',
            tel_number='1234567890',
        )   
        # Create an Event object
        self.event = Events.objects.create(
            title='Test Event',
            category='Test Category',
            date=datetime.now(),
            venue='Test Venue',
            image_url='https://example.com/image.jpg',
        )   
        # Create a Listing object
        self.listing = Listing.objects.create(
            seller_username='testuser',
            is_public=True,
            is_verified=True,
            is_sold=False,
            event_id=self.event.id
        )

        self.session = self.client.session
        self.session['username'] = 'testuser'
        self.session.save()

    def test_profile_page_renders_correctly(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userprofile.html')
        
        # Check if the userdata is rendered on the page
        self.assertContains(response, response.context['userdata'].first_name)
        self.assertContains(response, response.context['userdata'].last_name)
        self.assertContains(response, response.context['userdata'].username)
        self.assertContains(response, response.context['userdata'].tel_number)
        self.assertContains(response, response.context['userdata'].email)

    def tearDown(self):
        self.listing.delete()
        self.event.delete()
        self.user.delete()