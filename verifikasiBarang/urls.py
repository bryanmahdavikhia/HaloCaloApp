from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('seller-verification', views.seller_verification_index, name='index'),
    path('listing-verification', views.listing_verification_index, name='listing_verification'),
    path('verify-listing/<str:id>', views.verify_listing, name='verify_listing'),
    path('verify-seller/<str:id>', views.verify_seller, name='verify_seller'),
    path('reject-listing/<str:id>', views.reject_listing, name='reject_listing'),
    path('reject-seller/<str:id>', views.reject_seller, name='reject_seller'),
    path('view-seller-docs-ktp/<str:id>', views.retrieve_ktp, name='view_seller_docs_ktp'),
    path('view-seller-docs-selfie/<str:id>', views.retrieve_selfie, name='view_seller_docs_selfie'),
    path('view-listing-docs-pdf/<str:username>/<str:id>', views.retrieve_listing_pdf, name='retrieve_listing_pdf'),
    path('events', views.events, name='events'),
]