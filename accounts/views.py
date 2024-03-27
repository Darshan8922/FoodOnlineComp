from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
from .models import User, userProfile
from django.contrib import messages, auth
from vendor.forms import *
from .utils import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode


#Restrict the vendor for accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        return False
    

#Restrict the customer for accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        return False



# Create your views here.
def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already Logged In.')
        return redirect('myAccount')
    elif request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using the form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()
            # create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email,
                                            password=password)
            user.role = User.CUSTOMER
            user.save()

            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your account has been  registered successfully!')
            return redirect('registerUser')
    else:
        form = UserForm()
    context = {
        'form': form
    }
    return render(request,'accounts/registerUser.html', context)

def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already Logged In.')
        return redirect('myAccount')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)

        if form.is_valid() and v_form.is_valid:
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email,
                                            password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit = False)
            vendor.user = user
            user_profile = userProfile.objects.get(user = user)
            vendor.user_profile = user_profile
            vendor.save()

            #send Email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, 'Your account has been  created successfully ! Please wait for Approval')
            return redirect('registerVendor')
    else:
        form = UserForm()
        v_form = VendorForm()
        context = {
            'form' : form,
            'v_form' : v_form,
        }
    return render(request, 'accounts/registerVendor.html', context)

def activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user =  User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulation ! Your account is now Activated.')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('myAccount')


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already Logged In.')
        return redirect('myAccount')
    
    elif request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(email=email, password=password)

            if user is not None:
                auth.login(request, user)
                messages.success(request, 'You have Logged-In Successfully .')
                return redirect('myAccount')
            else:
                messages.error(request, 'Invalid Credential !')
                return redirect('login')
    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.success(request, 'You are now Logged Out.')
    return redirect('login')


@login_required(login_url = 'login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)


@login_required(login_url = 'login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render(request, 'accounts/custdashboard.html')


@login_required(login_url = 'login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendordashboard.html')


def forgot_password(request):
    if request.method=='POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists:
            user = User.objects.get(email__exact=email)

            #Send Reset Password Email
            mail_subject = 'Reset Your Password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, 'Password reset Link has been sent to your Email')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exixt')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')
             
def reset_password_validate(request, uid64, token):
    # Validate user by decoding token and user primary key
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user =  User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('myAccount')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')





