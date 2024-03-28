from django.shortcuts import render
from .forms import VendorForm
# Create your views here.

def vprofile(request):
    profile_form = UserProfileForm()
    vendor_form = VendorForm()
    return render(request, 'vendor/vprofile.html')