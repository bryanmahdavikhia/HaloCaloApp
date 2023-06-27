from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods

from uploadBarang import models as ub_md
from signup import controllers as cr

SIGNUP_HTML_STR = "signup.html"

@require_http_methods(["POST", "GET"])
def signup(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password1"]
        password2 = request.POST["password2"]
        f_name = request.POST["f_name"]
        l_name = request.POST["l_name"]
        tel_num = request.POST['tel_num']

        try:
            is_already_user = ub_md.User.objects.get(username=username)
        except ub_md.User.DoesNotExist:
            is_already_user = None

        if is_already_user is not None:
            return render(request, SIGNUP_HTML_STR, {'msg':'Username Exists'})
        elif len(password)<8:
            return render(request, SIGNUP_HTML_STR, {'msg':'Password need to be at least 8 Character long'})
        elif password != password2:
            return render(request, SIGNUP_HTML_STR, {'msg':'Password did not match'})
        else:
            hashed_password = cr.encrypt_password(password)
            new_user = ub_md.User(
                password=hashed_password,
                username=username,
                email=email,
                first_name=f_name,
                last_name=l_name,
                tel_number=tel_num
            )
            new_user.save()
            return HttpResponseRedirect("/signin")
    else:
        return render(request, SIGNUP_HTML_STR)

