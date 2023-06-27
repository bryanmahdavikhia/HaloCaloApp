from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse

from django.views.decorators.http import require_http_methods

from uploadBarang import controllers as cr
from uploadBarang import queries as qr
from uploadBarang import models as md
from signin import urls
from django.http import Http404, HttpResponse

import uuid

UPLOAD_IMG_HMTL = 'uploadImage.html'
UPLOAD_PDF_HTML = 'uploadPDF.html'
UPLOAD_SUCCESS_STR = 'File uploaded successfully'

firebase_connector = cr.FirebaseConnector()

@require_http_methods(["POST", "GET"])
def upload_documents(request):
    if 'username' not in request.session:
        return redirect(reverse('login'))

    if request.session['is_seller'] == True:
        return redirect(reverse('listingDocuments'))

    if request.method == "POST":
        username = request.session['username']
        if cr.check_user_already_upload_still_on_progress(username):
            context = {
                "has_username" : request.session.__contains__('username')
            }
            messages.error(request, 'You have already uploaded your documents and it is still being verified.')
            return HttpResponse(content=render(request, UPLOAD_IMG_HMTL, context), status=400)

        ktp_file = request.FILES['file']
        selfie_file = request.FILES['file2']

        username = request.session['username']
        first_name = request.session['first_name']
        email = request.session['email']

        try:
            is_file_exist = md.SellerVerificationDocuments.objects.get(seller_username=username)
        except md.SellerVerificationDocuments.DoesNotExist:
            is_file_exist = None
        
        if is_file_exist == None:
            firebase_connector.upload_ktp(ktp_file, selfie_file, username)
        else:
            firebase_connector.upload_ktp(ktp_file, selfie_file, username, reupload="yes")
            
        messages.success(request, UPLOAD_SUCCESS_STR)
        cr.send_verification_document_received_email(first_name, email)
        context = {
            "has_username" : request.session.__contains__('username')
        }
        return render(request, UPLOAD_IMG_HMTL, context)
    else:
        context = {
            "has_username" : request.session.__contains__('username')
        }
        return render(request, UPLOAD_IMG_HMTL, context)

@require_http_methods(["POST", "GET"])
def upload_listing_documents(request):
    if 'username' not in request.session:
        return redirect(reverse('login'))

    if request.session['is_seller'] == False:
        return redirect(reverse('verificationDocuments'))
    
    if request.method == "POST":
        bukti_file = request.FILES['file']
        event_name = request.POST.get('event')
        
        username = request.session['username']
        first_name = request.session['first_name']
        email = request.session['email']

        listing_id = str(uuid.uuid4())
        event_id = cr.get_event_id_from_database(event_name.split('[')[0][:-1], event_name.split('[')[1][:-1])

        firebase_connector.upload_pdf(bukti_file, username, listing_id, event_id)
        messages.success(request, UPLOAD_SUCCESS_STR)
        cr.send_listing_document_received_email(first_name, email, listing_id)
        context = {
            "has_username" : request.session.__contains__('username')
        }
        return render(request, UPLOAD_PDF_HTML, context)
    else:
        context = {
            'events': cr.get_events_from_database(),
            "has_username" : request.session.__contains__('username')
        }

        return render(request, UPLOAD_PDF_HTML, context)

@require_http_methods(["POST", "GET"])
def reupload_listing_documents(request, listing_id):
    if 'username' not in request.session:
        return redirect(reverse('login'))

    if request.session['is_seller'] == False:
        return redirect(reverse('verificationDocuments'))

    listing_object = md.Listing.objects.get(id=listing_id)
    listing_docs_object = md.ListingVerificationDocuments.objects.get(listing_id=listing_id)

    if (request.session['username'] == listing_object.seller_username) == False:
        raise Http404("Page not found")

    if (str(listing_docs_object.verification_status_id) != 'e5573012-185a-4b6c-bc43-715d5a1edcdf') == True:
        raise Http404("Page not found")
    
    if request.method == "POST":
        bukti_file = request.FILES['file']
        event_id = listing_object.event_id

        firebase_connector.upload_pdf(bukti_file, listing_object.seller_username, listing_id, event_id, reupload="yes")
        messages.success(request, UPLOAD_SUCCESS_STR)
        listing_docs_object.verification_status_id = 'fe2caca5-be86-45b1-997e-5a7a2bcf2a6e'
        listing_object.date_created = qr.get_date()
        listing_docs_object.save()
        
        context = {
            "has_username" : request.session.__contains__('username')
        }
        return render(request, UPLOAD_PDF_HTML, context)
    else:
        context = {
            'events': cr.get_events_from_database(),
            "has_username" : request.session.__contains__('username')
        }

        return render(request, UPLOAD_PDF_HTML, context)