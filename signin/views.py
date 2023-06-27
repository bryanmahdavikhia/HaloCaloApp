from django.shortcuts import render, redirect
from django.contrib.messages import constants as messages
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db import connection
from uploadBarang.models import User
from signup.controllers import decrypt_password
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def login(request):
    if request.session.has_key('username'):
        return check_role(request)
    
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.warning(request, 'Sorry we could not find your account.')
            return redirect("login")

        if decrypt_password(user, password):
            request.session['username'] = user.username
            request.session['is_admin'] = user.is_admin
            request.session['email'] = user.email
            request.session['first_name'] = user.first_name
            request.session['is_seller'] = user.is_seller
            return check_role(request)
        else:
            messages.warning(request, 'Login failed. Password incorrect.')
            return redirect("login")
    return render(request, "login.html", {"has_username":request.session.has_key("username")})

def logout(request):
    try:
        del request.session['username']
        del request.session['is_admin']
        del request.session['email']
        del request.session['first_name']
        request.session['has_username'] = False
    except KeyError:
        pass
    return HttpResponseRedirect("/")

def check_role(request):
    if request.session['is_admin']:
        return HttpResponseRedirect("/admin")
    else:
        # ini masih temp ya
        return redirect("home")
