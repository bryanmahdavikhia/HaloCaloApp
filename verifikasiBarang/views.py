import uuid
from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.db import connection
from collections import namedtuple
from datetime import datetime
from django.views.decorators.http import require_http_methods
from uploadBarang.controllers import FirebaseConnector
from verifikasiBarang import controllers as cr

import os

firebase_connector = FirebaseConnector()
signin = "/signin"

def tuple_fetch(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def check_admin(request):

    if request.session.has_key('username'):
        return request.session['is_admin']
    else:
        return False

@require_http_methods(["GET"])
def index(request):   
    is_admin = check_admin(request)

    if is_admin:
        return render(request, 'adminhub.html', {"has_username" : request.session.has_key('username'), "username" : request.session["username"]})
    else:
        return HttpResponseRedirect(signin)

@require_http_methods(["GET"])    
def seller_verification_index(request): 

    if check_admin(request):
        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("SELECT auth_user.*, seller_verification_documents.path_ktp, seller_verification_documents.path_selfie, seller_verification_documents.verification_status_id FROM auth_user INNER JOIN seller_verification_documents ON auth_user.username = seller_verification_documents.seller_username where date_seller is not null;")
        result = []
        result = tuple_fetch(cursor)
        result_sorted = sorted(result, key=lambda x: x.date_seller)
        cursor.close()   
        return render(request, 'seller_verification.html', {"result" : result_sorted, "has_username" : request.session.has_key('username')})
    else:
        return HttpResponseRedirect(signin)

@require_http_methods(["GET"])
def listing_verification_index(request):

    if check_admin(request):
        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("select listing.*, events.title, events.category, events.date, events.venue, listing_verification_documents.path_pdf, listing_verification_documents.notes, listing_verification_documents.verification_status_id from listing inner join events on listing.event_id = events.id inner join listing_verification_documents on listing_verification_documents.listing_id = listing.id")
        result = []
        result = tuple_fetch(cursor)
        result_sorted = sorted(result, key=lambda x: x.date_created)
        cursor.close()
        return render(request, 'listing_verification.html', {"result" : result_sorted, "has_username" : request.session.has_key('username')})
    else:
        return HttpResponseRedirect(signin)
    
@require_http_methods(["GET"])
def verify_listing(request, id):

    if check_admin(request):
        today = datetime.today().strftime('%Y-%m-%d')
        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("UPDATE listing SET is_verified = true, date_verified = %s WHERE id = %s;", [today, str(id)])
        cursor.execute("UPDATE listing_verification_documents SET verification_status_id = %s WHERE listing_id = %s;", ['425652d0-637b-4602-8369-ee33be10e198', id])
        cursor.close()

        # Send automated email when listing is verified.
        cr.send_listing_accepted_email(str(id))

        return HttpResponseRedirect("/admin/listing-verification")
    else:
        return HttpResponseRedirect(signin)

@require_http_methods(["GET"])
def verify_seller(request, id):

    if check_admin(request):
        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("update auth_user set is_seller = true where username = '" + str(id) + "';")
        cursor.execute("UPDATE seller_verification_documents SET verification_status_id = %s WHERE seller_username = %s;", ['425652d0-637b-4602-8369-ee33be10e198', id])
        cursor.close()

        # Send automated email when user is verified.
        cr.send_user_accepted_email(str(id))

        return HttpResponseRedirect("/admin/seller-verification")
    else:
        return HttpResponseRedirect(signin)

@require_http_methods(["GET", "POST"])
def reject_listing(request, id):

    if check_admin(request):
        if request.method == 'POST':
            notes = request.POST.get('notes')
            listing_id = id

            cursor = connection.cursor()
            cursor.execute("SET search_path TO public")
            cursor.execute("update listing set is_verified = false, date_verified = NULL where id = %s;", [id])
            query = "UPDATE listing_verification_documents SET notes = %s, verification_status_id = %s WHERE listing_id = %s"
            cursor.execute(query, [notes, 'e5573012-185a-4b6c-bc43-715d5a1edcdf', str(listing_id)])
            cursor.close()

            # Send automated email when listing is rejected.
            cr.send_listing_rejected_email(str(id))

            return HttpResponseRedirect("/admin/listing-verification")
            
        return render(request, 'reject_listing.html', {"id" : id, "has_username" : request.session.has_key('username')}) 
    else:
        return HttpResponseRedirect(signin)

@require_http_methods(["GET", "POST"])
def reject_seller(request, id):

    if check_admin(request):
        if request.method == 'POST':
            notes = request.POST.get('notes')
            username = id

            cursor = connection.cursor()
            cursor.execute("SET search_path TO public")
            cursor.execute("update auth_user set is_seller = false where username = '" + str(username) + "';")
            query = "UPDATE seller_verification_documents SET notes = %s, verification_status_id = %s WHERE seller_username = %s"
            cursor.execute(query, [notes, 'e5573012-185a-4b6c-bc43-715d5a1edcdf', str(username)])
            cursor.close()

            # Send automated email when user is rejected.
            cr.send_user_rejected_email(str(username))

            return HttpResponseRedirect("/admin/seller-verification")
            
        return render(request, 'reject_seller.html', {"username" : id, "has_username" : request.session.has_key('username')}) 
    else:
        return HttpResponseRedirect(signin)

@require_http_methods(["GET"])
def retrieve_ktp(request, id):
    if check_admin(request):

        ktp_url, selfie_url = firebase_connector.retrieve_ktp(id)
        context = {
            'image_data': ktp_url,
            'has_username' : request.session.has_key("username"),
            'file' : "KTP",
            'username' : id
        }

        return render(request, 'show_seller_image.html', context) 
    else:
        return HttpResponseRedirect(signin)

@require_http_methods(["GET"])
def retrieve_selfie(request, id):
    if check_admin(request):
        
        ktp_url, selfie_url = firebase_connector.retrieve_ktp(id)
        context = {
            'image_data': selfie_url,
            'has_username' : request.session.has_key("username"),
            'file' : "Selfie",
            'username' : id
        }

        return render(request, 'show_seller_image.html', context) 
    else:
        return HttpResponseRedirect(signin)

@require_http_methods(["GET"])
def retrieve_listing_pdf(request, username, id):
    if check_admin(request):

        pdf_url = firebase_connector.retrieve_pdf(username, id)
        context = {
            'pdf_url': pdf_url,
            'has_username' : request.session.has_key("username")
        }

        return render(request, 'show_listing_image.html', context)
    else:
        return HttpResponseRedirect(signin)

@require_http_methods(["GET", "POST"])
def events(request):
    if check_admin(request):
        cursor = connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.execute("select * from events;")
        result = []
        result = tuple_fetch(cursor)

        if request.method == 'POST':
            title = request.POST.get('title')
            category = request.POST.get('category')
            date = request.POST.get('date')
            venue = request.POST.get('venue')
            image_url = request.POST.get('image_url')
            new_id = str(uuid.uuid4())

            cursor = connection.cursor()
            cursor.execute("SET search_path TO public")
            cursor.execute("insert into events (id, title, category, date, venue, image_url) values (%s, %s, %s, %s, %s, %s);", [new_id, title, category, date, venue, image_url])
            cursor.close()

            return HttpResponseRedirect("/admin/events")

        return render(request, 'events.html', {"result" : result, "has_username" : request.session.has_key('username')})
    else:
        return HttpResponseRedirect(signin)