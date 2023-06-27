import django
from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.db import connection
from collections import namedtuple
import uuid
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie

listing = "/listing/"
signin = "/signin"

def tuple_fetch(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

# Create your views here.
@require_http_methods(["GET"])
def viewlisting(request, id):

    if check_listing(id):

        username = ""

        if request.session.has_key("username"):
            username = request.session['username']

        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("SELECT listing.*, title, category, date, venue, image_url FROM listing cross join events where listing.event_id = events.id and listing.id = %s;", [id])
        result = []
        result = tuple_fetch(cursor)
        res = result[0]
        event_title = str(res[8])
        seller_username = res[0]
        cursor.execute("select * from auth_user where username = '" + seller_username + "'")
        seller = []
        seller = tuple_fetch(cursor)
        sellerinfo = seller[0]
        cursor.execute("select listing_token.id as token from listing inner join listing_token on listing.id = listing_token.listing_id where listing.id = %s;", [id])
        tokens = []
        tokens = tuple_fetch(cursor)
        cursor.execute("SELECT listing.*, title, category, date, venue, image_url FROM listing cross join events where listing.event_id = events.id and listing.id != %s and listing.is_verified = true and listing.is_public = true and events.title = %s LIMIT 3;", [id, event_title])
        cards = []
        cards = tuple_fetch(cursor)
        cursor.close()

        return render(request, 'detail.html', {"cards" : cards, "res" : res, "username" : username, "tokens" : tokens, "sellerinfo" : sellerinfo, "has_username" : request.session.has_key("username")})
    
    else:
        return render(request, 'listing_unavailable.html', {"has_username" : request.session.has_key('username')})

@require_http_methods(["POST"])
def make_token(request):
    if request.method == 'POST':
        listing_id = request.POST.get('listing_id')
        new_token = str(uuid.uuid4())
        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("insert into listing_token (id, listing_id) values (%s, %s);", [new_token, listing_id])
        cursor.close()
        return HttpResponseRedirect(listing + str(listing_id))
    
    else:
        # Change to Landing Page when there is Landing Page
        return HttpResponseRedirect("/signin")

@require_http_methods(["POST"])    
def change_visibility(request):
    if request.method == 'POST':
        listing_id = request.POST.get('listing_id')
        vis_string = request.POST.get('vis_string')
        vis = False

        if vis_string == "true":
            vis = True

        print(vis)

        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("update listing set is_public = %s where id = %s", [vis, listing_id])
        cursor.close()
        return HttpResponseRedirect(listing + str(listing_id))
    
    else:
        # Change to Landing Page when there is Landing Page
        return HttpResponseRedirect(signin)
    
@require_http_methods(["POST"])    
def change_availability(request):
    if request.method == 'POST':
        listing_id = request.POST.get('listing_id')
        vis_string = request.POST.get('vis_string')
        vis = False

        if vis_string == "true":
            vis = True

        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("update listing set is_sold = %s where id = %s", [vis, listing_id])
        cursor.close()
        return HttpResponseRedirect(listing + str(listing_id))
    
    else:
        # Change to Landing Page when there is Landing Page
        return HttpResponseRedirect(signin)

@require_http_methods(["POST"])
@csrf_protect
def validate_token(request):
    if request.method == 'POST':

        payload = json.loads(request.body)
        token = payload.get('token')
        id = payload.get('id')

        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("select listing_token.id as token from listing inner join listing_token on listing.id = listing_token.listing_id where listing.id = %s;", [id])
        tokens = []
        tokens = tuple_fetch(cursor)
        cursor.close()
        tokens_array = []

        for i in tokens:
            tokens_array.append(str(i[0]))

        if token in tokens_array:
            cursor = connection.cursor()
            cursor.execute("SET search_path TO public")
            cursor.execute("delete from listing_token where id = %s;", [token])
            cursor.close()
            return JsonResponse({'is_valid_token': True})
        else:
            return JsonResponse({'is_valid_token': False})
    
    else:
        # Change to Landing Page when there is Landing Page
        return HttpResponseRedirect(signin)
        
def check_listing(id):
    try:
        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("select is_verified, seller_username from listing where id = %s;", [id])
        result = []
        result = tuple_fetch(cursor)
        is_verified = result[0][0]
        seller_username = result[0][1]
        cursor.execute("select is_seller from auth_user where username = '" + seller_username + "'")
        result = []
        result = tuple_fetch(cursor)
        is_seller = result[0][0]
        cursor.close()
    
    except (IndexError, django.db.utils.DataError):
        return False
    
    else:
        return is_verified and is_seller