from django.urls import path

from . import views

urlpatterns = [
    path('<str:id>', views.viewlisting, name='index'),
    path('validate_token/', views.validate_token, name='validate_token'),
    path('make_token/', views.make_token, name='make_token'),
    path('change_visibility/', views.change_visibility, name='change_visibility'),
    path('change_availability/', views.change_availability, name='change_availability')
]