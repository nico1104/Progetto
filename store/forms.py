import self as self
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from store.models import Product, User, Customer, Seller


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
        fields = ['username', 'email', 'password1', 'password2']

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_customer = True
        user.save()
        customer = Customer.objects.create(user=user)
        return user

    def clean_email(self):
        """
             Controllo che l'email non sia presa da alcun utente
        """
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("La mail selezionata è già esistente, scegline una differente")
        return data


class SellerSignUpForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_seller = True
        user.save()
        seller = Seller.objects.create(user=user)
        return user

    def clean_email(self):
        """
             Controllo che l'email non sia presa da alcun utente
        """
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("La mail selezionata è già esistente, scegline una differente")
        return data


class ProdottoAddForm (forms.ModelForm):

    class Meta:

        model = Product
        fields = ('name', 'category', 'available_size', 'description', 'price', 'image')
        labels = {
            'name': _('Nome'),
            'category': _('Categoria del prodotto'),
            'available_size': _('Taglie disponibili'),
            'description': _('Descrizione del prodotto'),
            'price': _('Prezzo'),
            'image': _('Immagine del prodotto'),
        }


    def save(self, commit=True):
        product = super().save(commit=False)
        product.image = self.cleaned_data.get('image')
        product.save()
        return product


class ProductSearchForm(forms.Form):

    nome_prod = forms.CharField(max_length=40, label='', required=False, initial="", widget= forms.TextInput
                           (attrs={'placeholder':'Ricerca prodotto'}))

