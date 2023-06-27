from django.urls import path
from . import views

urlpatterns = [
	path('logout', views.logout, name='logout'),
    path('', views.login, name='login'),
    # path('index', views.success_login, name='success_login'),
]