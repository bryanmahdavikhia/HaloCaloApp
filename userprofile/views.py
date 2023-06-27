from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.db import connection
from collections import namedtuple
import uuid
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse

signin = "/signin"

def tuple_fetch(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def index(request):
    if request.session.has_key('username'):
        username = request.session['username']

        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("select auth_user.*, notes, status FROM auth_user LEFT JOIN seller_verification_documents ON auth_user.username = seller_verification_documents.seller_username LEFT JOIN verification_status ON seller_verification_documents.verification_status_id = verification_status.id where username = %s;", [username])
        userdata = []
        userdata = tuple_fetch(cursor)[0]

        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("SELECT listing.*, title, category, date, venue, notes, image_url, verification_status.status FROM listing cross join events cross join listing_verification_documents cross join verification_status WHERE listing.event_id = events.id AND listing_verification_documents.listing_id = listing.id AND verification_status.id = listing_verification_documents.verification_status_id AND seller_username = %s AND verification_status.status = '1_verified';", [username])
        activelistings = []
        activelistings = tuple_fetch(cursor)

        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("SELECT listing.*, title, category, date, venue, notes, image_url, verification_status.status FROM listing cross join events cross join listing_verification_documents cross join verification_status WHERE listing.event_id = events.id AND listing_verification_documents.listing_id = listing.id AND verification_status.id = listing_verification_documents.verification_status_id AND seller_username = %s AND verification_status.status = '0_on_process';", [username])
        processinglistings = []
        processinglistings = tuple_fetch(cursor)

        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("SELECT listing.*, title, category, date, venue, notes, image_url, verification_status.status FROM listing cross join events cross join listing_verification_documents cross join verification_status WHERE listing.event_id = events.id AND listing_verification_documents.listing_id = listing.id AND verification_status.id = listing_verification_documents.verification_status_id AND seller_username = %s AND verification_status.status = '2_rejected';", [username])
        rejectedlistings = []
        rejectedlistings = tuple_fetch(cursor)

        cursor.close()

        context = {
            "userdata" : userdata,
            "has_username" : request.session.has_key('username'),
            "activelistings" : activelistings,
            "processinglistings" : processinglistings,
            "rejectedlistings" : rejectedlistings,
        }

        return render(request, 'userprofile.html', context)

    else:
        return HttpResponseRedirect(signin)