# for registering new user
# import user model for registering new user 
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
import uuid

class SignUpForm(UserCreationForm):
    """Signup form without manual username; captures phone.

    Username is auto-generated from email (local-part) with a short suffix if needed.
    """
    first_name = forms.CharField(label="First Name", max_length=30, required=False)
    last_name = forms.CharField(label="Last Name", max_length=30, required=False)
    email = forms.EmailField(label="Email")
    phone = forms.CharField(label="Phone", max_length=15, required=False)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', 'phone')

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email already registered")
        return email

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        email = self.cleaned_data.get('email')
        user.email = email
        # Generate username from email local part
        base_username = email.split('@')[0][:20]
        candidate = base_username
        idx = 1
        while User.objects.filter(username=candidate).exists():
            candidate = f"{base_username}-{idx}"[:30]
            idx += 1
        user.username = candidate
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        # Attach phone to form instance for external creation of Customer
        self.phone = self.cleaned_data.get('phone', '')
        return user


class CustomerProfileForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    phone = forms.CharField(max_length=15, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.customer = kwargs.pop('customer', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
        if self.customer:
            self.fields['phone'].initial = self.customer.phone

    def save(self):
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name','')
            self.user.last_name = self.cleaned_data.get('last_name','')
            self.user.save(update_fields=['first_name','last_name'])
        if self.customer:
            self.customer.phone = self.cleaned_data.get('phone','')
            self.customer.first_name = self.user.first_name or self.customer.first_name
            self.customer.last_name = self.user.last_name or self.customer.last_name
            self.customer.save(update_fields=['first_name','last_name','phone'])
        return self.user, self.customer
