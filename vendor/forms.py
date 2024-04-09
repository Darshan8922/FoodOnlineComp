from django import forms
from .models import Vendor, OpeningHour
from accounts.validators import allow_only_images_validator




class VendorForm(forms.ModelForm):
    vendor_license = forms.ImageField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator])
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']

class OpeningHourForm(forms.ModelForm):
    def __init__(self, *args, request=None, **kwargs):
        self.request = request  # Store the request object as an instance attribute
        super().__init__(*args, **kwargs)

    class Meta:
        model = OpeningHour
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']
    




