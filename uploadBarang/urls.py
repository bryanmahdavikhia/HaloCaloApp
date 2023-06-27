from django.urls import path

from uploadBarang import views

urlpatterns = [
    path('verification-documents', views.upload_documents, name='verificationDocuments'),
    path('listing-documents', views.upload_listing_documents, name='listingDocuments'),
    path('listing-documents/<str:listing_id>/reupload', views.reupload_listing_documents, name='reuploadListingDocuments'),
]