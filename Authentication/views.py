from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import message, send_mail, EmailMessage
from django.shortcuts import redirect,render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.encoding import force_bytes
from . tokens import generate_token


# Create your views here.
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from Task import settings


def home(request):
    return render(request,"Authentication/index.html")




def signup(request, message=None):
    if request.method=="POST":
        username = request.POST['UserName']
        name = request.POST['name']
        email = request.POST['email']
        Pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        phone = request.POST['phone']
        dob = request.POST['dob']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request, "Email already registered")
            return redirect('home')

        if len(username)>10:
            messages.error(request,"Username must under 10 characters")

        if Pass1 != pass2:
            messages.error(request, "Passwords didn't match")

        if not username.isalnum():
            messages.error(request, "Username will alpha numeric")
            return redirect("home")

        myUser = User.objects.create_user(username,email,Pass1)
        myUser.name = name
        myUser.phone = phone
        myUser.dob = dob
        myUser.is_active = False

        myUser.save()
        messages.success(request, "Your Account has been successfully created")

        #Welcome Email
        subject = "Welcome to Task - Django Login!!"
        message = "Hello" + myUser.name + "!! \n" + "Welcome to IGTAPPS!! \n Thankyou \n We have also sent you a confirmation Email , Please confirm your Email Address"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myUser.email]
        send_mail(subject,message,from_email,to_list,fail_silently = True)

        #Confirm Email
        current_site = get_current_site(request)
        email_subject = "Confirm your email at Task - Django Login!!"
        message2 = render_to_string('email_confirmation.html', {
            'name': myUser.name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myUser.pk)),
            'token': generate_token.make_token(myUser),
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myUser.email],

        )
        email.fail_silently= True
        email.send()
        return redirect('signin')

    return render(request,"Authentication/signup.html")

def signin(request):
    if request.method == 'POST':
        username = request.POST['UserName']
        Pass1 = request.POST['Pass1']
        user = authenticate(username=username,Password=Pass1)

        if user is not None:
            login(request,user)
            name = user.name
            return render(request, "Authentication/index.html",{'name': name})

        else:
            messages.error(request,"Your Account has been created successfully")
            return redirect('home')



    return render(request,"Authentication/signin.html")

def signout(request):
    logout(request)
    message.success(request, "Logged out successfully")
    return redirect('home')


def force_text():
    pass


def activate(request,uidb64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myUser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myUser = None

    if myUser is not None and generate_token.check_token(myUser,token):
        myUser.is_active = True
        myUser.save()
        login(request,myUser)
        return redirect('home')
    else:
        return render(request,'activation_failed.html')

