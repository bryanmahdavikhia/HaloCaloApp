import unittest
from unittest.mock import patch, MagicMock

import uuid 

from django.db import connection
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.http import Http404

from uploadBarang import queries as qr
from uploadBarang import controllers as cr
from uploadBarang import views as vw
from uploadBarang import models as md

# Global
SET_SEARCH_PATH = "SET search_path TO public"
THIS_IS_WRONG_STR = "this is wrong"

IMAGE_JPEG_STR = 'image/jpeg'
TEST_JPG_STR = 'test.jpg'

IMAGE_PNG_STR = 'image/png'
TEST_PNG_STR = 'test.png'

TEST_USER_EMAIL_STR = 'test_user@test.com'
TEST_DATE_STR = '2023-03-22 00:00:00'

TEST_PDF_STR = 'path/pdf'

TEST_EMAIL_DEV_STR = 'halocalo.dev@gmail.com'

class UploadKTPViewTest(TestCase):
    def setUp(self):
        self.request = MagicMock()

    def test_upload_documents_not_logged_in(self):
        self.request.method = 'GET'
        response = vw.upload_documents(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual('/signin/', response['Location'])
    
    def test_upload_documents_logged_in_already_seller(self):
        self.request.method = 'GET'
        self.request.session = {'username': 'test_user', 'is_seller': True}
        response = vw.upload_documents(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual('/upload/listing-documents', response['Location'])

    def test_upload_documents_logged_in_not_seller(self):
        self.request.method = 'GET'
        self.request.session = {'username': 'test_user', 'is_seller': False}
        response = vw.upload_documents(self.request)
        self.assertEqual(response.status_code, 200)

class TestUploadVerificationJPEGOnView(TestCase):
    def setUp(self):
        self.request = MagicMock()

    def test_upload_document_post_with_jpeg(self):
        self.new_user = md.User(
            password='password',
            username='test_user',
            first_name='test',
            last_name='test',
            email=TEST_USER_EMAIL_STR,
            tel_number='12345'
        )
        self.new_user.save()

        self.request.method = 'POST'
        self.request.FILES = {
            'file': SimpleUploadedFile(TEST_JPG_STR, b'test_content', content_type=IMAGE_JPEG_STR),
            'file2': SimpleUploadedFile(TEST_JPG_STR, b'test_content', content_type=IMAGE_JPEG_STR)
        }
        self.request.session = {
            'username': self.new_user.username, 
            'first_name': self.new_user.first_name, 
            'email': self.new_user.email, 
            'is_seller': False
        }
        
        response = vw.upload_documents(self.request)
        self.assertEqual(response.status_code, 200)

        self.new_verification_docs = md.SellerVerificationDocuments.objects.get(seller_username=self.new_user.username)
        self.new_verification_docs.delete()
        self.new_user.delete()

class TestUploadVerificationPNGOnView(TestCase):
    def setUp(self):
        self.request = MagicMock()
        
    def test_upload_document_post_with_png(self):
        self.new_user = md.User(
            password='password',
            username='test_user',
            first_name='test',
            last_name='test',
            email=TEST_USER_EMAIL_STR,
            tel_number='12345'
        )
        self.new_user.save()

        self.request.method = 'POST'
        self.request.FILES = {
            'file': SimpleUploadedFile(TEST_PNG_STR, b'test_content', content_type=IMAGE_PNG_STR),
            'file2': SimpleUploadedFile(TEST_PNG_STR, b'test_content', content_type=IMAGE_PNG_STR)
        }
        self.request.session = {
            'username': self.new_user.username, 
            'first_name': self.new_user.first_name, 
            'email': self.new_user.email, 
            'is_seller': False
        }
        
        response = vw.upload_documents(self.request)
        self.assertEqual(response.status_code, 200)

        self.new_verification_docs = md.SellerVerificationDocuments.objects.get(seller_username=self.new_user.username)
        self.new_verification_docs.delete()
        self.new_user.delete()

class TestUploadVerificationRejectedOnView(TestCase):
    def setUp(self):
        self.request = MagicMock()
        
    def test_upload_document_post_but_rejected(self):
        self.new_user = md.User(
            password='password',
            username='test_user',
            first_name='test',
            last_name='test',
            email=TEST_USER_EMAIL_STR,
            tel_number='12345'
        )
        self.new_user.save()
        existing_verification_docs_id = str(uuid.uuid4())
        self.existing_verification_docs = md.SellerVerificationDocuments(
            id=existing_verification_docs_id,
            seller_username=self.new_user.username,
            path_ktp='ktp',
            path_selfie='selfie',
            verification_status_id='e5573012-185a-4b6c-bc43-715d5a1edcdf'
        )
        self.existing_verification_docs.save()

        self.request.method = 'POST'
        self.request.FILES = {
            'file': SimpleUploadedFile(TEST_JPG_STR, b'test_content', content_type=IMAGE_JPEG_STR),
            'file2': SimpleUploadedFile(TEST_JPG_STR, b'test_content', content_type=IMAGE_JPEG_STR)
        }
        self.request.session = {
            'username': self.new_user.username, 
            'first_name': self.new_user.first_name, 
            'email': self.new_user.email, 
            'is_seller': False
        }
        
        response = vw.upload_documents(self.request)
        self.assertEqual(response.status_code, 200)

        self.existing_verification_docs.delete()
        self.new_user.delete()


class UploadPDFViewTest(TestCase):
    def setUp(self):
        self.request = MagicMock()

    def test_upload_listing_not_logged_in(self):
        self.request.method = 'GET'
        response = vw.upload_listing_documents(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/signin/')
    
    def test_upload_listing_logged_in_not_seller(self):
        self.request.method = 'GET'
        self.request.session = {'username': 'test_user', 'is_seller': False}
        response = vw.upload_listing_documents(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/upload/verification-documents')

    def test_upload_listing_logged_in_already_seller(self):
        self.request.method = 'GET'
        self.request.session = {'username': 'test_user', 'is_seller': True}
        response = vw.upload_listing_documents(self.request)
        self.assertEqual(response.status_code, 200)

    def test_upload_listing_document_post(self):
        self.new_user = md.User(
            password='password',
            username='test_user_for_listing',
            first_name='test',
            last_name='test',
            email=TEST_USER_EMAIL_STR,
            tel_number='12345'
        )
        self.new_user.save()

        self.event_id = str(uuid.uuid4())
        self.event = md.Events(
            id=self.event_id,
            category='test',
            date=TEST_DATE_STR,
            title='test',
            venue='test',
            image_url='test'
        )
        self.event.save()

        self.request.method = 'POST'
        self.request.FILES = {
            'file': SimpleUploadedFile(TEST_JPG_STR, b'test_content', content_type=IMAGE_JPEG_STR)
        }
        self.request.session = {
            'username': self.new_user.username,
            'first_name': self.new_user.first_name, 
            'email': self.new_user.email, 
            'is_seller': True
        }
        self.request.POST = {
            'event': 'test [test]'
        }

        response = vw.upload_listing_documents(self.request)
        self.assertEqual(response.status_code, 200)

        self.get_new_listing = md.Listing.objects.get(seller_username=self.new_user.username)
        self.get_listing_documents = md.ListingVerificationDocuments.objects.get(listing_id=self.get_new_listing.id)
        self.get_listing_documents.delete()
        self.get_new_listing.delete()
        self.get_new_event = md.Events.objects.get(id=self.event_id)
        self.get_new_event.delete()
        self.new_user.delete()

class ReuploadPDFViewTest(TestCase):
    def setUp(self):
        self.request = MagicMock()

    def test_reupload_listing_not_logged_in(self):
        self.request.method = 'GET'
        response = vw.reupload_listing_documents(self.request, "<str:id>")
        self.assertEqual(response.status_code, 302)
    
    def test_reupload_listing_logged_in_not_seller(self):
        self.request.method = 'GET'
        self.request.session = {'username': 'test_user', 'is_seller': False}
        response = vw.reupload_listing_documents(self.request, "<str:id>")
        self.assertEqual(response.status_code, 302)

    def test_reupload_listing_not_the_seller(self):
        self.new_user = md.User(
            password='password',
            username='test_user_for_reupload',
            first_name='test',
            last_name='test',
            email=TEST_USER_EMAIL_STR,
            tel_number='12345'
        )
        self.new_user.save()

        self.event_id = str(uuid.uuid4())
        self.event = md.Events(
            id=self.event_id,
            category='test',
            date=TEST_DATE_STR,
            title='test',
            venue='test',
            image_url='test'
        )
        self.event.save()

        self.listing_id = str(uuid.uuid4())
        self.listing = md.Listing(
            id=self.listing_id,
            seller_username=self.new_user.username,
            event_id=self.event.id
        )
        self.listing.save()

        self.listing_verification_docs_id = str(uuid.uuid4())
        self.listing_verification_docs = md.ListingVerificationDocuments(
            id=self.listing_verification_docs_id,
            path_pdf=TEST_PDF_STR,
            listing_id=self.listing_id
        )
        self.listing_verification_docs.save()

        self.request.method = 'GET'
        self.request.session = {'username': 'not_the_seller', 'is_seller': True}

        with self.assertRaises(Http404):
            response = vw.reupload_listing_documents(self.request, self.listing_id)

        self.listing_verification_docs.delete()
        self.listing.delete()
        self.event.delete()
        self.new_user.delete()

    def test_reupload_listing_already_verified(self):
        self.new_user = md.User(
            password='password',
            username='test_user_for_reupload1',
            first_name='test',
            last_name='test',
            email=TEST_USER_EMAIL_STR,
            tel_number='12345'
        )
        self.new_user.save()

        self.event_id = str(uuid.uuid4())
        self.event = md.Events(
            id=self.event_id,
            category='test',
            date=TEST_DATE_STR,
            title='test',
            venue='test',
            image_url='test'
        )
        self.event.save()

        self.listing_id = str(uuid.uuid4())
        self.listing = md.Listing(
            id=self.listing_id,
            seller_username=self.new_user.username,
            event_id=self.event.id
        )
        self.listing.save()

        self.listing_verification_docs_id = str(uuid.uuid4())
        self.listing_verification_docs = md.ListingVerificationDocuments(
            id=self.listing_verification_docs_id,
            path_pdf=TEST_PDF_STR,
            listing_id=self.listing_id,
            verification_status_id='425652d0-637b-4602-8369-ee33be10e198'
        )
        self.listing_verification_docs.save()

        self.request.method = 'GET'
        self.request.session = {'username': self.new_user.username, 'is_seller': True}

        with self.assertRaises(Http404):
            response = vw.reupload_listing_documents(self.request, self.listing_id)

        self.listing_verification_docs.delete()
        self.listing.delete()
        self.event.delete()
        self.new_user.delete()

    def test_reupload_listing_success(self):
        self.new_user = md.User(
            password='password',
            username='test_user_for_reupload2',
            first_name='test',
            last_name='test',
            email=TEST_USER_EMAIL_STR,
            tel_number='12345'
        )
        self.new_user.save()

        self.event_id = str(uuid.uuid4())
        self.event = md.Events(
            id=self.event_id,
            category='test',
            date=TEST_DATE_STR,
            title='test',
            venue='test',
            image_url='test'
        )
        self.event.save()

        self.listing_id = str(uuid.uuid4())
        self.listing = md.Listing(
            id=self.listing_id,
            seller_username=self.new_user.username,
            event_id=self.event.id
        )
        self.listing.save()

        self.listing_verification_docs_id = str(uuid.uuid4())
        self.listing_verification_docs = md.ListingVerificationDocuments(
            id=self.listing_verification_docs_id,
            path_pdf=TEST_PDF_STR,
            listing_id=self.listing_id,
            verification_status_id='e5573012-185a-4b6c-bc43-715d5a1edcdf'
        )
        self.listing_verification_docs.save()

        self.request.method = 'POST'
        self.request.FILES = {
            'file': SimpleUploadedFile(TEST_JPG_STR, b'test_content', content_type=IMAGE_JPEG_STR)
        }
        self.request.session = {
            'username': self.new_user.username, 
            'first_name': self.new_user.first_name,
            'email': self.new_user.email, 
            'is_seller': True
        }

        response = vw.reupload_listing_documents(self.request, self.listing_id)
        self.assertEqual(response.status_code, 200)

        self.listing_verification_docs.delete()
        self.listing.delete()
        self.event.delete()
        self.new_user.delete()
    
    def test_reupload_listing_get(self):
        self.new_user = md.User(
            password='password',
            username='test_user_for_reupload2',
            first_name='test',
            last_name='test',
            email=TEST_USER_EMAIL_STR,
            tel_number='12345'
        )
        self.new_user.save()

        self.event_id = str(uuid.uuid4())
        self.event = md.Events(
            id=self.event_id,
            category='test',
            date=TEST_DATE_STR,
            title='test',
            venue='test',
            image_url='test'
        )
        self.event.save()

        self.listing_id = str(uuid.uuid4())
        self.listing = md.Listing(
            id=self.listing_id,
            seller_username=self.new_user.username,
            event_id=self.event.id
        )
        self.listing.save()

        self.listing_verification_docs_id = str(uuid.uuid4())
        self.listing_verification_docs = md.ListingVerificationDocuments(
            id=self.listing_verification_docs_id,
            path_pdf=TEST_PDF_STR,
            listing_id=self.listing_id,
            verification_status_id='e5573012-185a-4b6c-bc43-715d5a1edcdf'
        )
        self.listing_verification_docs.save()

        self.request.method = 'GET'
        self.request.FILES = {
            'file': SimpleUploadedFile(TEST_JPG_STR, b'test_content', content_type=IMAGE_JPEG_STR)
        }
        self.request.session = {
            'username': self.new_user.username, 
            'first_name': self.new_user.first_name,
            'email': self.new_user.email, 
            'is_seller': True
        }

        response = vw.reupload_listing_documents(self.request, self.listing_id)
        self.assertEqual(response.status_code, 200)

        self.listing_verification_docs.delete()
        self.listing.delete()
        self.event.delete()
        self.new_user.delete()

class TestUploadKTPTest(unittest.TestCase):
    def setUp(self):
        self.firebase_connector = cr.FirebaseConnector()

    def test_upload_ktp(self):
        self.new_user = md.User(
            password='password',
            username='test_user',
            first_name='test',
            last_name='test',
            email=TEST_USER_EMAIL_STR,
            tel_number='12345'
        )
        self.new_user.save()

        # Create KTP file and selfie file
        ktp_content = b"test_ktp_content"
        selfie_content = b"test_selfie_content"
        ktp_file = SimpleUploadedFile("test_ktp.jpg", ktp_content, content_type=IMAGE_JPEG_STR)
        selfie_file = SimpleUploadedFile("test_selfie.jpg", selfie_content, content_type=IMAGE_JPEG_STR)

        self.firebase_connector.upload_ktp(ktp_file, selfie_file, self.new_user.username)
        
        url1, url2 = self.firebase_connector.retrieve_ktp(self.new_user.username)
        self.assertIsNotNone(url1)
        self.assertIsNotNone(url2)

        self.verification_documents = md.SellerVerificationDocuments.objects.get(
            seller_username=self.new_user.username
        )
        self.verification_documents.delete()
        self.new_user.delete()

class TestUploadPDFTest(unittest.TestCase):
    def setUp(self):
        self.firebase_connector = cr.FirebaseConnector()
        self.username = 'ralfidzaky'

    def test_upload_pdf(self):
        self.event_id = str(uuid.uuid4())
        self.event = md.Events(
            id=self.event_id,
            category='test',
            date=TEST_DATE_STR,
            title='test',
            venue='test',
            image_url='test'
        )
        self.event.save()
        
        # Create PDF file
        pdf_content = b"test_pdf_content"
        pdf_file = SimpleUploadedFile("test_pdf.pdf", pdf_content, content_type="application/pdf")

        # Generate UUID for listing ID
        listing_uuid = uuid.uuid4()
        self.firebase_connector.upload_pdf(pdf_file, self.username, listing_uuid, self.event.id)

        url = self.firebase_connector.retrieve_pdf(self.username, listing_uuid)
        self.assertIsNotNone(url)
        self.listing_documents = md.ListingVerificationDocuments.objects.get(
            listing_id=listing_uuid
        )
        self.listing_documents.delete()
        self.get_new_listing = md.Listing.objects.get(id=listing_uuid)
        self.get_new_listing.delete()
        self.get_new_event = md.Events.objects.get(id=self.event_id)
        self.get_new_event.delete()

class TestGetEventFromDatabase(TestCase):
    def test_get_event_from_database(self):
        # Call the function being tested
        result = cr.get_events_from_database()
        self.assertIsNotNone(result)

class TestGetEventIdFromDatabase(TestCase):
    def test_get_event_id_from_database(self):
        # Create event
        self.event_id = str(uuid.uuid4())
        self.event = md.Events(
            id=self.event_id,
            category='test',
            date=TEST_DATE_STR,
            title='test',
            venue='test',
            image_url='test'
        )
        self.event.save()

        # Call the function being tested
        result = cr.get_event_id_from_database('test', 'test')

        self.assertIsNotNone(result)
        self.assertEqual(uuid.UUID(self.event_id), result)

        self.event.delete()

class TestSendVerificationDocumentReceivedEmail(TestCase):
    def test_send_verification_document_received_email_success(self):
        username = 'Test User'
        email = 'testuser@example.com'

        cr.send_verification_document_received_email(username, email)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'HaloCalo - Account Verification')
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_DEV_STR)
        self.assertEqual(mail.outbox[0].to, [email])

class TestSendListingDocumentReceivedEmail(TestCase):
    def test_send_listing_document_received_email_success(self):
        username = 'Test User'
        email = 'testuser@example.com'
        listing_id = 12345

        cr.send_listing_document_received_email(username, email, listing_id)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'HaloCalo - Listing Document')
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_DEV_STR)
        self.assertEqual(mail.outbox[0].to, [email])

class QueriesTestCase(TestCase):
    
    def test_input_verification_ktp_docs_to_db(self):
        seller_verification_id = str(uuid.uuid4())
        username = "testuser"
        ktp_file_name = "testktp.jpg"
        selfie_file_name = "testselfie.jpg"
        expected_query = """
            INSERT INTO
            
            seller_verification_documents 
            (id, seller_username, path_ktp, path_selfie, notes, verification_status_id)
            
            VALUES
            ('{}', '{}', '{}', '{}', '{}', '{}')
        """.format(
            seller_verification_id,
            username, 
            ktp_file_name,
            selfie_file_name,
            "",
            "fe2caca5-be86-45b1-997e-5a7a2bcf2a6e"
        )

        expected_query_2 = f"""
            UPDATE  auth_user
            SET     date_seller = '{qr.get_date()}'
            WHERE   username = '{username}';
        """

        expected_query = expected_query.replace("\n", "")
        expected_query = " ".join(expected_query.split())

        expected_query_2 = expected_query_2.replace("\n", "")
        expected_query_2 = " ".join(expected_query_2.split())

        actual_query, actual_query_2 = qr.input_verification_ktp_docs_to_db(username, ktp_file_name, selfie_file_name, seller_verification_id)
        actual_query = actual_query.replace("\n", "")
        actual_query = " ".join(actual_query.split())

        actual_query_2 = actual_query_2.replace("\n", "")
        actual_query_2 = " ".join(actual_query_2.split())

        self.assertEqual(actual_query, expected_query)
        self.assertNotEqual(THIS_IS_WRONG_STR, expected_query)

        self.assertEqual(actual_query_2, expected_query_2)
        self.assertNotEqual(THIS_IS_WRONG_STR, expected_query_2)
        
    def test_input_verification_listing_docs_to_db(self):
        listing_verification_id = str(uuid.uuid4())
        username = "testuser"
        listing_id = "123"
        pdf_filename = "testlisting.pdf"
        event_id = uuid.uuid4()
        expected_listing_query = """
            INSERT INTO

            listing
            (id, seller_username, date_created, is_sold, is_public, is_verified, event_id)

            VALUES
            ('{}', '{}', '{}', '{}', '{}', '{}', '{}')
        """.format(
            listing_id,
            username,
            qr.get_date(),
            "false",
            "false",
            "false",
            event_id
        )
        expected_listing_document_query = """
            INSERT INTO

            listing_verification_documents
            (id, path_pdf, notes, listing_id, verification_status_id)

            VALUES
            ('{}', '{}', '{}', '{}', '{}')
        """.format(
            listing_verification_id,
            pdf_filename,
            "",
            listing_id,
            "fe2caca5-be86-45b1-997e-5a7a2bcf2a6e"
        )
        expected_listing_query = expected_listing_query.replace("\n", "")
        expected_listing_query = " ".join(expected_listing_query.split())

        expected_listing_document_query = expected_listing_document_query.replace("\n", "")
        expected_listing_document_query = " ".join(expected_listing_document_query.split())

        listing_query, listing_document_query = qr.input_verification_listing_docs_to_db(username, listing_id, pdf_filename, event_id, listing_verification_id)
        listing_query = listing_query.replace("\n", "")
        listing_query = " ".join(listing_query.split())

        listing_document_query = listing_document_query.replace("\n", "")
        listing_document_query = " ".join(listing_document_query.split())

        self.assertEqual(listing_query, expected_listing_query)
        self.assertEqual(listing_document_query, expected_listing_document_query)
        self.assertNotEqual(THIS_IS_WRONG_STR, expected_listing_query)
        self.assertNotEqual(THIS_IS_WRONG_STR, expected_listing_document_query)
        
    def test_get_events(self):
        expected_query = """
            SELECT  title || ' [' || category || ']'
            FROM    events;
        """

        expected_query = expected_query.replace("\n", "")
        expected_query = " ".join(expected_query.split())

        actual_query = qr.get_events().replace("\n", "")
        actual_query = " ".join(actual_query.split())
        
        self.assertEqual(actual_query, expected_query)
        self.assertNotEqual(THIS_IS_WRONG_STR, expected_query)

    def test_get_event_id(self):
        expected_query = """
            SELECT  id
            FROM    events
            WHERE   title = '{}'
                    AND category = '{}'
        """.format('satu', 'platinum')

        expected_query = expected_query.replace("\n", "")
        expected_query = " ".join(expected_query.split())

        actual_query = qr.get_event_id('satu', 'platinum').replace("\n", "")
        actual_query = " ".join(actual_query.split())
        
        self.assertEqual(actual_query, expected_query)
        self.assertNotEqual(THIS_IS_WRONG_STR, expected_query)

class ModelTest(TestCase):
    def test_user_verification_docs_model_combined(self):
        self.new_user = md.User(
            password='password',
            username='test_model_user',
            first_name='test',
            last_name='test',
            email='test_model_user@test.com',
            tel_number='12345'
        )
        self.new_user.save()

        self.new_seller_verification_docs_id = str(uuid.uuid4())
        self.new_seller_verification_docs = md.SellerVerificationDocuments(
            id=self.new_seller_verification_docs_id,
            seller_username=str(md.User.objects.get(username='test_model_user').username),
            path_ktp='path/ktp',
            path_selfie='path/ktp_selfie'
        )
        self.new_seller_verification_docs.save()

        self.new_user_get = md.User.objects.get(username='test_model_user')
        self.new_seller_verification_docs = md.SellerVerificationDocuments.objects.get(id=self.new_seller_verification_docs_id)
        self.assertIsNotNone(self.new_user_get)
        self.assertIsNotNone(self.new_seller_verification_docs)

        self.new_seller_verification_docs.delete()
        self.new_user_get.delete()

    def test_token_listing_model(self):
        self.token = str(uuid.uuid4())
        self.listing_token = md.ListingToken(
            id=self.token,
            listing_id='143fdd43-23d9-4ea7-b9f3-eae35e700c07'
        )
        self.listing_token.save()

        self.new_listing_token_get = md.ListingToken.objects.get(id=self.token)
        self.assertIsNotNone(self.new_listing_token_get)
        self.new_listing_token_get.delete()

    def test_event_listing_listing_docs_model_combined(self):
        self.event_id = str(uuid.uuid4())
        self.event = md.Events(
            id=self.event_id,
            category='Silver',
            date=TEST_DATE_STR,
            title='test',
            venue='test',
            image_url='test'
        )
        self.event.save()

        self.listing_id = str(uuid.uuid4())
        self.listing = md.Listing(
            id=self.listing_id,
            seller_username=str(md.User.objects.get(username='ralfidzaky').username),
            event_id=str(md.Events.objects.get(id=self.event_id).id)
        )
        self.listing.save()


        self.listing_verification_docs_id = str(uuid.uuid4())
        self.listing_verification_docs = md.ListingVerificationDocuments(
            id=self.listing_verification_docs_id,
            path_pdf=TEST_PDF_STR,
            listing_id=self.listing_id,
        )
        self.listing_verification_docs.save()

        self.new_event_get = md.Events.objects.get(id=self.event_id)
        self.new_listing_get = md.Listing.objects.get(id=self.listing_id)
        self.new_listing_verification_docs = md.ListingVerificationDocuments.objects.get(id=self.listing_verification_docs_id)
        self.assertIsNotNone(self.new_event_get)
        self.assertIsNotNone(self.new_listing_get)
        self.assertIsNotNone(self.new_listing_verification_docs)

        self.new_listing_verification_docs.delete()
        self.new_listing_get.delete()
        self.new_event_get.delete()

    def test_verification_status(self):
        self.new_verification_status_id = str(uuid.uuid4())
        self.verification_status = md.VerificationStatus(
            id=self.new_verification_status_id,
            status='test status'
        )
        self.verification_status.save()

        self.new_verification_status_get = md.VerificationStatus.objects.get(id=self.new_verification_status_id)
        self.assertIsNotNone(self.new_verification_status_get)
        self.new_verification_status_get.delete()
