from django.shortcuts import render
from uploadBarang.models import Listing, Events, User
# Create your views here.

def get_listing(title):
    events = Events.objects.filter(title=title)
    events_id = events.values_list('id', flat=True)
    event = Events.objects.get(id=events_id[0])
    listings = {
        "listing":[],
        "title": title,
        "image_url": event.image_url,
        "overlay_img": event.banner_url_2,
        "category": event.category,
        "date": event.date,
        "venue": event.venue
    }
    
    for event_id in events_id:
        card = list(Listing.objects.filter(
            event_id=event_id,
            is_verified=True,
            is_public=True,
            seller_username__in=User.objects.filter(is_seller=True).values_list('username', flat=True)
        ))
        if len(card) > 0:
            listings["listing"].extend(card)

    listings['listing'] = listings['listing'][:2]

    return listings

def discover_events():
    events = Events.objects.all()
    listings_dict = {}
    for event in events:
        event_title = event.title
        if event_title not in listings_dict:
            listings_dict[event_title] = {
                'event': event,
                'id': event.id,
                'num_listings': 0,
                'image_url': event.image_url,
                'banner_url': event.banner_url,
                'title': event_title,
            }
        num_listings = Listing.objects.filter(
            event_id=event.id, is_verified=True, is_public=True,
            seller_username__in=User.objects.filter(is_seller=True).values_list('username', flat=True)
        ).count()
        listings_dict[event_title]['num_listings'] += num_listings

    listings_dict = list(listings_dict.values())
        
    return listings_dict

def home(request):
    events_new = get_listing("DEWA 19 - Pesta Rakyat")
    events_dont_miss = get_listing("BLACKPINK - Born Pink Tour")
    discover = discover_events()
    context = {
        'has_username': request.session.has_key("username"),
        'events_new': events_new,
        'events_dont_miss': events_dont_miss,
        'discover_events': discover,
    }
    return render(request, 'home.html', context=context)