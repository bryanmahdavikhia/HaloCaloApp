from django.urls import path
from selectedFeat import views as vw

urlpatterns = [
    path('', vw.event_list, name='event_list'),
    path('search/', vw.event_list_with_search, name='event_list_with_search'),
    path('<str:event_name>/listings/', vw.listing_list, name='listing_list'),
    path('events/<str:event_name>/listings/<str:selected_category>/filtered/', vw.listing_list, name='listing_list_filtered'),
]