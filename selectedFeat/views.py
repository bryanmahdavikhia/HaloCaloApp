from uploadBarang import models as ub_md
from django.template.response import TemplateResponse
from fuzzywuzzy import process
from django.core.paginator import Paginator
from django.db.models import F, OuterRef, Subquery
from django.http import JsonResponse
from django.template.loader import render_to_string

from django.views.decorators.http import require_http_methods

@require_http_methods(["POST", "GET"])
def event_list(request):
    events = list_events(request)
    featured_event_1 = get_listing("DEWA 19 - Pesta Rakyat")
    featured_event_2 = get_listing("BLACKPINK - Born Pink Tour")
    return TemplateResponse(
        request, 
        'event_list.html', 
        {
            'has_username': request.session.has_key("username"),
            'events': events, 
            "featured_event_1":featured_event_1, 
            "featured_event_2":featured_event_2
        }
    )

@require_http_methods(["POST", "GET"])
def list_events(request):
    events = {}
    all_events = ub_md.Events.objects.all()
    for event in all_events:
        event_title = event.title
        if event_title not in events:
            events[event_title] = {
                'event': event,
                'id': event.id,
                'num_listings': 0,
                'image_url': event.image_url,
                'title': event_title,
            }
        num_listings = ub_md.Listing.objects.filter(
            event_id=event.id, is_verified=True, is_public=True,
            seller_username__in=ub_md.User.objects.filter(is_seller=True).values_list('username', flat=True)
        ).count()
        events[event_title]['num_listings'] += num_listings

    events = list(events.values())
    paginator = Paginator(events, 9)
    page = request.GET.get('page')
    events = paginator.get_page(page)
    return events

def get_listing(title):
    events = ub_md.Events.objects.filter(title=title)
    events_id = events.values_list('id', flat=True)
    event = ub_md.Events.objects.get(id=events_id[0])
    listings = {
        "listing":[],
        "title": title,
        "image_url": event.image_url,
        "category": event.category,
        "date": event.date,
        "venue": event.venue,
        "banner_url_2": event.banner_url_2,
    }
    
    for id in events_id:
        card = (list(ub_md.Listing.objects.filter(
            event_id=event.id, is_verified=True, is_public=True,
            seller_username__in=ub_md.User.objects.filter(is_seller=True).values_list('username', flat=True)
        )))
        if len(card) == 0:
            continue
        else:
            listings["listing"].extend(card)
    listings['listing'] = listings['listing'][:2]

    return listings

@require_http_methods(["POST", "GET"])
def event_list_with_search(request):
    events = ub_md.Events.objects.all()
    title_query = request.GET.get('title')
    if title_query:
        titles = [event.title for event in events]
        closest_title = process.extractOne(title_query, titles)[0]
        print(closest_title)
        events = events.filter(title=closest_title)

    return TemplateResponse(
        request, 
        'event_list_search.html', 
        {   
            'has_username': request.session.has_key("username"),
            'events': events
        }
    )

@require_http_methods(["POST", "GET"])
def listing_list(request, event_name, selected_category=None):
    events = ub_md.Events.objects.filter(title=event_name)
    event_ids = events.values_list('id', flat=True)
    events_subquery = ub_md.Events.objects.filter(id=OuterRef('event_id')).values('category')

    auth_user_usernames = ub_md.User.objects.filter(is_seller=True).values_list('username', flat=True)

    listings = ub_md.Listing.objects.filter(
        event_id__in=event_ids,
        is_public=True,
        is_verified=True,
        seller_username__in=auth_user_usernames
    ).annotate(
        category=Subquery(events_subquery)
    )

    event_list = ub_md.Events.objects.filter(
        id__in=event_ids
    )

    categories = listings.values_list('category', flat=True).distinct()
    category_filters = ['All'] + list(categories)

    selected_category = request.GET.get('category', 'All')
    if selected_category != 'All':
        listings = listings.filter(category=selected_category)

    listings = list(listings.values())
    paginator = Paginator(listings, 9)
    page = request.GET.get('page')
    listings = paginator.get_page(page)

    list_event = list_events(request)

    context = {
        'has_username': request.session.has_key("username"),
        'events': events,
        'listings': listings,
        'category_filters': category_filters,
        'selected_category': selected_category,
        'event_name': event_name,
        'event_category': event_list[0].category,
        'event_image_url': event_list[0].image_url,
        'event_banner_url': event_list[0].banner_url,
        'event_date': event_list[0].date,
        'event_venue': event_list[0].venue,
        'list_event' : list_event
    }

    if not listings:
        context['no_listings_message'] = "No listings yet"

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        context['template_name'] = 'listing_list_filtered.html'
        return JsonResponse({'html': render_to_string(context['template_name'], context)}, status=200)
        
    return TemplateResponse(request, 'listing_list.html', context)