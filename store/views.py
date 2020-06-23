import json
import datetime

from django.contrib.auth import login, user_logged_out
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.http import JsonResponse
from django.template.defaulttags import comment
from django.views.decorators.csrf import csrf_exempt
from pyexpat.errors import messages
import django_tables2 as tables
from django_tables2 import SingleTableView, TemplateColumn, RequestConfig
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView

from .decorators import customer_required
from .forms import ProductForm, CustomerSignUpForm, SellerSignUpForm, ProdottoAddForm, ProductSearchForm
from .models import *


def store(request):
    products = Product.objects.all()

    if request.method == 'POST':
        form = ProductSearchForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['nome_prod'] == '':  # Campo ricerca vuoto
                products = Product.objects.all()
            else:
                products = Product.objects.filter(Q(name__icontains=form.cleaned_data['nome_prod']))
    else:
        form = ProductSearchForm()

    if request.user.is_authenticated:
        if request.user.is_seller:
            seller = request.user.seller
            context = {'products': products, 'form': form}
            return render(request, 'store/store.html', context)
        else:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items

    else:
        # Create empty cart for now for non-logged in user
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    logged_user = request.user
    context = {'logged_user': logged_user, 'products': products, 'cartItems': cartItems, 'form': form}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # Create empty cart for now for non-logged in user
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # Create empty cart for now for non-logged in user
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = (data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

    else:
        print("Utente non loggato")

    return JsonResponse('Payment submitted..', safe=False)


class SignUpView(TemplateView):
    template_name = 'registration/register.html'


class CustomerSignUpView(CreateView):
    model = User
    form_class = CustomerSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'cliente'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('store:store')


class SellerSignUpView(CreateView):
    model = User
    form_class = SellerSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'fornitore'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('store:store')


@login_required
def logout(request):
    user = getattr(request, 'user', None)
    user = None
    user_logged_out.send(sender=User.__class__, request=request, user=User)
    request.session.flush()
    if hasattr(request, 'user'):
        request.user = AnonymousUser()
    return redirect('store:login')


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def product_insert(request):
    if request.method == 'POST':
        form = ProdottoAddForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
    else:
        form = ProdottoAddForm

    logged_user_username = request.user.username
    context = {'form': form, 'logged_user_username': logged_user_username}
    return render(request, 'store/add_product.html', context)


def product_delete(request, id):
    """
        Elimina il prodotto corrispondente alla riga in cui viene premuto il tasto delete nella pagina che mostra
        gli articoli caricati dall'utente attualmente loggato.

        Args:
            id: id del prodotto

        Returns:
             Ritorna la stessa pagina aggiornata
    """
    product = Product.objects.get(id=id)
    product.delete()
    return redirect('store:load-product')


def profile_view(request):
    """
        Funzione che si occupa della visualizzazione del profilo utente e gestione degli termini della balcklist e
        cancellazione degli articoli

    """

    logged_user_username = request.user.username
    context = {'logged_user_username': logged_user_username, 'email': request.user.email}
    return render(request, 'store/user_profile.html', context)


def loaded_product_view(request):
    """
        Funzione che si occupa della visualizzazione dei testi caricati dall'utente

        Returns:
             tutti i testi caricati dall'utente loggato
    """

    logged_user_username = request.user.username
    loaded_products = Product.objects.filter(user=request.user.id)
    table = ProfileTextTable(loaded_products)
    RequestConfig(request).configure(table)

    context = {'logged_user_username': logged_user_username, 'table': table}
    return render(request, 'store/load_product.html', context)


class ProfileTextTable(tables.Table):
    """
        Definisce una tabella personalizzata per visualizzare gli articoli inseriti dall'utente attualmente loggato
    """

    class Meta:
        model = Product
        template_name = "django_tables2/bootstrap4.html"
        fields = ("name", "category", "available_size", "user", "price")
        attrs = {"class": "table table-striped table-bordered sortable",
                 "data-toggle": "table"
                 }

    detail = TemplateColumn(exclude_from_export=False, template_name='store/detail.html', orderable=False,
                            verbose_name='')
    delete = TemplateColumn(exclude_from_export=False, template_name='store/delete.html', orderable=False,
                            verbose_name='')


def search_helmet(request):
    products = Product.objects.filter(category='Casco')
    context = {'products': products}
    return render(request, 'store/helmet.html', context)


def search_gloves(request):
    products = Product.objects.filter(category='Guanti')
    context = {'products': products}
    return render(request, 'store/gloves.html', context)


def search_jacket(request):
    products = Product.objects.filter(category='Giacca')
    context = {'products': products}
    return render(request, 'store/jacket.html', context)


def search_trousers(request):
    products = Product.objects.filter(category='Pantaloni')
    context = {'products': products}
    return render(request, 'store/trousers.html', context)


def search_suit(request):
    products = Product.objects.filter(category='Tuta')
    context = {'products': products}
    return render(request, 'store/suit.html', context)


def search_boots(request):
    products = Product.objects.filter(category='Stivali')
    context = {'products': products}
    return render(request, 'store/boots.html', context)


def search_stuff(request):
    products = Product.objects.filter(category='Manutenzione moto')
    context = {'products': products}
    return render(request, 'store/bikestuff.html', context)


def product_description(request, id):
    product = Product.objects.get(id=id)
    logged_user = request.user
    context = {'product': product, 'logged_user': logged_user}
    return render(request, 'store/detail.html', context)

