from django.db import models
import uuid

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    password = models.CharField(max_length=128)
    is_admin = models.BooleanField(default=False)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    tel_number = models.CharField(max_length=20)
    is_seller = models.BooleanField(default=False)
    date_seller = models.DateTimeField(blank=True)

    class Meta:
        managed = False
        db_table = 'auth_user'

class Events(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.TextField()
    date = models.DateTimeField(blank=True)
    title = models.TextField()
    venue = models.TextField()
    image_url = models.TextField()
    banner_url = models.TextField()
    banner_url_2 = models.TextField()

    class Meta:
        managed = False
        db_table = 'events' # the name of the existing table in your PostgreSQL database

class Listing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller_username = models.TextField() # Foreign Key to User (username)
    date_created = models.DateTimeField(auto_now_add=True)
    date_verified = models.DateTimeField(null=True, blank=True)
    is_sold = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    event_id = models.TextField() # Foreign Key to Events (id)

    class Meta:
        managed = False
        db_table = 'listing'

class ListingToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing_id = models.TextField() # Foreign Key to Listing (id)

    class Meta:
        managed = False
        db_table = 'listing_token'

class ListingVerificationDocuments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    path_pdf = models.TextField()
    notes = models.TextField(blank=True)
    listing_id = models.TextField() # Foreign Key to Listing (id)
    verification_status_id = models.TextField(default='fe2caca5-be86-45b1-997e-5a7a2bcf2a6e') # Foreign Key to Verification Status (id)

    class Meta:
        managed = False
        db_table = 'listing_verification_documents'

class SellerVerificationDocuments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller_username = models.TextField() # Foreign Key to User (username)
    path_ktp = models.TextField()
    path_selfie = models.TextField()
    notes = models.TextField(blank=True)
    verification_status_id = models.TextField(default='fe2caca5-be86-45b1-997e-5a7a2bcf2a6e') # Foreign Key to Verification Status (id)

    class Meta:
        managed = False
        db_table = 'seller_verification_documents'
    
class VerificationStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.TextField()

    class Meta:
        managed = False
        db_table = 'verification_status'

