from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from store.models import Product, User, Customer


class ProductForm(forms.ModelForm):
    """
        form per carrello
    """

    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]

    size = forms.ChoiceField(required=True, choices=SIZE_CHOICES)

    class Meta:
        model = Product
        fields = ('name', 'category', 'price', 'image', 'size')


########## USER ############

class CustomerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_customer = True
        user.save()
        customer = Customer.objects.create(user=user)

        return user


class SellerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_seller = True
        if commit:
            user.save()
        return user
