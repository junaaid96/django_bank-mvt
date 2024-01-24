# here we use UserCreationForm to create a form for user registration. if we use ModelForm then we have to write 3 ModelForm for 3 models which is in models.py file. so we make a relationship to built in user model along with extra data(extending the built-in user model, which is a common approach in Django for adding custom fields to the user model.) so that only usercreationform is enough to create a form for user registration.

from django.contrib.auth.forms import UserCreationForm
from django import forms
from .constants import ACCOUNT_TYPE, GENDER_TYPE
from django.contrib.auth.models import User
from .models import UserBankAccount, UserAddress


class UserRegistrationForm(UserCreationForm):
    # Here the first 3 fields are in built in user model. so we don't need to write them again. but for required=True we have to write them again.
    first_name = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={'required': True}))
    last_name = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={'required': True}))
    email = forms.EmailField(
        max_length=100, widget=forms.TextInput(attrs={'required': True}))

    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'account_type',
                  'gender', 'birth_date', 'street_address', 'city', 'postal_code', 'country']

    def save(self, commit=True):
        customer = super().save(commit=False)
        if commit == True:
            customer.save()  # we save data to user model

            account_type = self.cleaned_data.get('account_type')
            gender = self.cleaned_data.get('gender')
            birth_date = self.cleaned_data.get('birth_date')
            street_address = self.cleaned_data.get('street_address')
            city = self.cleaned_data.get('city')
            postal_code = self.cleaned_data.get('postal_code')
            country = self.cleaned_data.get('country')

            UserAddress.objects.create(
                user=customer,
                street_address=street_address,
                city=city,
                postal_code=postal_code,
                country=country
            )

            UserBankAccount.objects.create(
                user=customer,
                account_no=2024000 + customer.id,
                account_type=account_type,
                gender=gender,
                birth_date=birth_date
            )

            return customer
