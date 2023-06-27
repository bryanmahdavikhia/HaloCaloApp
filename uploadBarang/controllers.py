import firebase_admin
from firebase_admin import credentials, storage

import datetime
import base64
import uuid

from django.db import connection
from django.core.mail import send_mail

from uploadBarang import queries as qr
from uploadBarang import models as md

# Global
SET_SEARCH_PATH = "SET search_path TO public"

class FirebaseConnector():

    def __init__(self):
        self.config = {
            'apiKey': "AIzaSyD9jkiGNZweidaU_spdu54UxQX_fM9Sws0",
            'authDomain': "halocalo-fb.firebaseapp.com",
            'databaseURL': "https://halocalo-fb-default-rtdb.firebaseio.com",
            'projectId': "halocalo-fb",
            'storageBucket': "halocalo-fb.appspot.com",
            'messagingSenderId': "292142272602",
            'appId': "1:292142272602:web:3802904e2d58c376618863",
            'serviceAccount': "serviceAccount.json",
        }

        # Initialize the Firebase app with your service account credentials
        cred = credentials.Certificate(self.config['serviceAccount'])

        # Initialize the default app if it hasn't been initialized yet
        try:
            app = firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate('serviceAccount.json')
            firebase_admin.initialize_app(cred, {
                'storageBucket': self.config['storageBucket']
            })

        # Create a reference to the Firebase Storage bucket
        self.bucket = storage.bucket()

    def upload_ktp(self, ktp_file, selfie_file, username, reupload=None):
        """Upload KTP and user selfie with KTP into Firebase and create new 
        verification documents observation on Supabase using the `inputPathToDatabase` function."""

        ktp_file_name = "verification/{}/".format(username) + 'KTP_Only.{}'.format('jpg')
        selfie_file_name = "verification/{}/".format(username) + 'Selfie_KTP.{}'.format('jpg')

        # Check the file extensions and set the content types accordingly
        if ktp_file.name.endswith('.png'):
            ktp_content_type = 'image/png'
        if selfie_file.name.endswith('.png'):
            selfie_content_type = 'image/png'

        if ktp_file.name.endswith('.jpg') or ktp_file.name.endswith('.jpeg'):
            ktp_content_type = 'image/jpeg'
        if selfie_file.name.endswith('.jpg') or selfie_file.name.endswith('.jpeg'):
            selfie_content_type = 'image/jpeg'

        # Upload the files
        ktp_blob = self.bucket.blob(ktp_file_name)
        ktp_blob.upload_from_file(ktp_file, content_type=ktp_content_type)
        selfie_blob = self.bucket.blob(selfie_file_name)
        selfie_blob.upload_from_file(selfie_file, content_type=selfie_content_type)

        # Set the `content-length` metadata for the uploaded files
        ktp_file_size = ktp_blob.size
        selfie_file_size = selfie_blob.size

        ktp_blob.metadata = {"content-length": str(ktp_file_size)}
        selfie_blob.metadata = {"content-length": str(selfie_file_size)}

        # Input to Relational-Database
        if reupload == None:
            input_path_to_database("verification", username, 
                                ktp_file_name=ktp_file_name, selfie_file_name=selfie_file_name)
        else:
            seller_file = md.SellerVerificationDocuments.objects.get(seller_username=username)
            seller_file.verification_status_id = 'fe2caca5-be86-45b1-997e-5a7a2bcf2a6e'
            seller_file.save()

            seller_obj = md.User.objects.get(username=username)
            seller_obj.date_seller = qr.get_date()
            seller_obj.save()

    def retrieve_ktp(self, username):
        """Retrieve KTP and user selfie with KTP from Firebase Storage and return their URLs."""

        ktp_file_name = "verification/{}/KTP_Only.jpg".format(username)
        selfie_file_name = "verification/{}/Selfie_KTP.jpg".format(username)

        ktp_blob = self.bucket.blob(ktp_file_name)
        selfie_blob = self.bucket.blob(selfie_file_name)

        ktp_url = ktp_blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
        selfie_url = selfie_blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')

        return ktp_url, selfie_url

    def upload_pdf(self, pdf_file, username, uuid, event_id, reupload=None):
        """Upload listing 'proof' document PDF into Firebase and create new 
        verification documents observation on Supabase using the `inputPathToDatabase` function."""

        pdf_file_name = "listing/{}/{}.pdf".format(username, uuid)

        # Upload the files
        pdf_blob = self.bucket.blob(pdf_file_name)
        pdf_blob.upload_from_file(pdf_file, content_type='application/pdf')

        # Set the `content-length` metadata for the uploaded files
        pdf_file_size = pdf_blob.size
        pdf_blob.metadata = {"content-length": str(pdf_file_size)}

        # Input to Relational-Database
        if reupload == None:
            input_path_to_database("listing", username,
                                pdf_file_name=pdf_file_name, listing_id=uuid, event_id=event_id)

    def retrieve_pdf(self, username, id):
        """Download listing 'proof; document PDF from Firebase and 
        return it as a PDF data."""

        pdf_file_name = "listing/{}/{}.pdf".format(username, id)
        pdf_blob = self.bucket.blob(pdf_file_name)

        pdf_url = pdf_blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
        return pdf_url

def input_path_to_database(doc_type, username, ktp_file_name=None, 
                        selfie_file_name=None, pdf_file_name=None,
                        listing_id=None, event_id=None):
    """Create new observation (row) into Supabase based on Listing or
    Verification documents that were uploaded by the users."""

    if doc_type == 'verification':
        seller_verification_id = str(uuid.uuid4())
        query, query_update_username = qr.input_verification_ktp_docs_to_db(
            username, ktp_file_name, selfie_file_name, seller_verification_id
        )
        
        cursor = connection.cursor()
        cursor.execute(SET_SEARCH_PATH)
        cursor.execute(query)
        cursor.execute(query_update_username)
    elif doc_type == 'listing':
        listing_verification_id = str(uuid.uuid4())
        query_listing, query_listing_document = qr.input_verification_listing_docs_to_db(
            username, listing_id, pdf_file_name, event_id, listing_verification_id)

        cursor = connection.cursor()
        cursor.execute(SET_SEARCH_PATH)
        cursor.execute(query_listing)
        cursor.execute(query_listing_document)

def check_user_already_upload_still_on_progress(username):
    try:
        user_verification_docs = md.SellerVerificationDocuments.objects.get(seller_username=username)
    except md.SellerVerificationDocuments.DoesNotExist:
        user_verification_docs = None
    
    if user_verification_docs == None:
        return False
    else:
        if (str(user_verification_docs.verification_status_id) == 'e5573012-185a-4b6c-bc43-715d5a1edcdf'):
            return False
        return True

def get_events_from_database():
    """Get list of events that are present in the Supabase."""

    query = qr.get_events()
    
    cursor = connection.cursor()
    cursor.execute(SET_SEARCH_PATH)
    cursor.execute(query)
    events = cursor.fetchall()

    return list(set([item[0] for item in events]))

def get_event_id_from_database(title, category):
    """Get event id based on the title and seating category from Supabase."""

    event_id = md.Events.objects.get(title=title, category=category).id

    return event_id

def send_verification_document_received_email(username, email):
    subject = 'HaloCalo - Account Verification'
    body = f"""
Dear {username},

We hope this message finds you well. We are writing to confirm that we have received your account verification documents and we appreciate your prompt action in submitting them. Thank you for your cooperation in this matter.

Please note that our team is working diligently to process your verification as soon as possible. Rest assured that we will review your documents thoroughly and ensure that your account is verified promptly and securely.

If we require any further information or documentation from you, we will be in touch via email or phone. Otherwise, please allow us some time to complete the verification process, after which we will notify you of the outcome.

If you have any questions or concerns in the meantime, please do not hesitate to reach out to us at halocalo.dev[at]gmail.com.

Once again, thank you for your cooperation in verifying your account with us.

Best regards,
HaloCalo Team"""
    
    from_email = 'halocalo.dev@gmail.com'
    to_email = [f'{email}']

    send_mail(subject, body, from_email, to_email, fail_silently=False)

def send_listing_document_received_email(username, email, listing_id):
    subject = 'HaloCalo - Listing Document'
    body = f"""
Dear {username},

We would like to take this opportunity to thank you for choosing our platform to list your item. We are writing to confirm that we have received your listing documents and we appreciate your prompt action in submitting them. Thank you for your cooperation in this matter.

Please note that our team is working diligently to process your listing as soon as possible. In the meantime, we encourage you to check the following URL regularly to ensure that your listing has been successfully uploaded into our system: halocalo.store/listing/{listing_id}.

Rest assured that we will review your documents thoroughly and ensure that your listing is processed promptly and accurately.

If we require any further information or documentation from you, we will be in touch via email or phone. Otherwise, please allow us some time to complete the processing of your listing, after which we will notify you of the outcome.

If you have any questions or concerns in the meantime, please do not hesitate to reach out to us at halocalo.dev[at]gmail.com.

Once again, thank you for choosing our platform and for your cooperation in listing your item with us.

Best regards,
HaloCalo Team"""

    from_email = 'halocalo.dev@gmail.com'
    to_email = [f'{email}']

    send_mail(subject, body, from_email, to_email, fail_silently=False)