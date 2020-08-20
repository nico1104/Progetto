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
from django.utils.translation import ugettext_lazy as _
from scipy import spatial

from .decorators import customer_required, seller_required
from .forms import ProductForm, CustomerSignUpForm, SellerSignUpForm, ProdottoAddForm, ProductSearchForm
from .models import *


def store(request):
    """
            Funzione che si occupa della visualizzazione dei prodotti sullo store e dispone lo store a seconda
            che l'utente sia un cliente o un fornitore.

    """
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

@login_required()
@customer_required()
def cart(request):
    """
            Funzione che si occupa della visualizzazione dei prodotti all'interno del carrello
            ed è dedicata ad utenti che hanno effettuato il login come cliente.
    """
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

@login_required()
@customer_required()
def checkout(request):
    """
            Funzione che si occupa del riepilogo dei dati dell'ordine.
    """

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
    """
            Funzione che si occupa del processo che porta a termine l'ordine e completa l'ordine solo se
            il prezzo totale corrispond econ il totale dell'ordine, per proteggersi da eventuali manomissini del prezzo.

    """
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
    """
            Funzione che si occupa della registrazione del cliente.

    """

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
    """
                Funzione che si occupa della registrazione del fornitore.

    """

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
    """
                Funzione che si occupa del logout e reindirizza al login.

    """

    user = getattr(request, 'user', None)
    user = None
    user_logged_out.send(sender=User.__class__, request=request, user=User)
    request.session.flush()
    if hasattr(request, 'user'):
        request.user = AnonymousUser()
    return redirect('store:login')


def updateItem(request):
    """
                Funzione che si occupa dell'aggiornamento dei prodotti nel carrello in seguito
                ad operazione di aggiunta o rimozione.

    """

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

@login_required()
@seller_required()
def product_insert(request):
    """
        Funzione che si occupa dell'aggiunta del prodotto nello store da parte di in fornitore loggato.

        :return:
        Ritorna la stessa pagina per aggiungere un nuovo articolo.

    """

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


@login_required()
@seller_required()
def product_delete(request, id):
    """
        Elimina il prodotto corrispondente alla riga in cui viene premuto il tasto delete nella pagina che mostra
        gli articoli caricati dall'utente attualmente loggato.

        :param:
            id: id del prodotto.

        :return:
             Ritorna la stessa pagina aggiornata.
    """
    product = Product.objects.get(id=id)
    product.delete()
    return redirect('store:load-product')

@login_required()
def profile_view(request):
    """
        Funzione che si occupa della visualizzazione del profilo utente e gestione degli termini della balcklist e
        cancellazione degli articoli.


        :return:
             Ritorna la pagina del profilo.

    """

    logged_user_username = request.user.username
    context = {'logged_user_username': logged_user_username, 'email': request.user.email}
    return render(request, 'store/user_profile.html', context)

@login_required()
def loaded_product_view(request):
    """
        Funzione che si occupa della visualizzazione dei testi caricati dall'utente.

        :return:
             tutti i prodotti caricati dall'utente loggato se l'utente è fornitore, oppure tutti gli ordini effettuati
             se l'utente è un cliente.
    """
    if request.user.is_seller:
        logged_user_username = request.user.username
        loaded_products = Product.objects.filter(user=request.user.id)
        table = ProfileTextTable(loaded_products)
        RequestConfig(request).configure(table)

        context = {'logged_user_username': logged_user_username, 'table': table}
        return render(request, 'store/load_product.html', context)

    else:
        logged_user_username = request.user.username
        loaded_products = Product.objects.filter(user=request.user.id)
        table = ProfileTextTable2(loaded_products)
        RequestConfig(request).configure(table)
        context = {'logged_user_username': logged_user_username, 'table': table}
        return render(request, 'store/load_product.html', context)


class ProfileTextTable(tables.Table):
    """
        Definisce una tabella personalizzata per visualizzare gli articoli inseriti dall'utente attualmente loggato.

        :param: tabella da renderizzare.
    """
    name = tables.Column(verbose_name='Nome')
    category = tables.Column(verbose_name='Categoria')
    available_size = tables.Column(verbose_name='Taglie disponibili')
    user = tables.Column(verbose_name='Utente')
    price = tables.Column(verbose_name='Prezzo')
    description = tables.Column(verbose_name='Descrizione')

    class Meta:
        model = Product
        template_name = "django_tables2/bootstrap4.html"
        fields = ("name", "category", "available_size", "user", "price", "description")
        attrs = {"class": "table table-striped table-bordered sortable",
                 "data-toggle": "table"
                 }

    delete = TemplateColumn(exclude_from_export=False, template_name='store/delete.html', orderable=False,
                            verbose_name='')


class ProfileTextTable2(tables.Table):
    """
        Definisce una tabella personalizzata per visualizzare gli articoli ordinati dall'utente attualmente loggato.

        :param: tabella da renderizzare.
    """

    customer = tables.Column(verbose_name='Cliente')
    date_ordered = tables.Column(verbose_name='Data di ordine')
    complete = tables.Column(verbose_name='Completo')
    transaction_id = tables.Column(verbose_name='Transazione')

    class Meta:
        model = Order
        template_name = "django_tables2/bootstrap4.html"
        fields = ("customer", "date_ordered", "complete", "transaction_id")
        attrs = {"class": "table table-striped table-bordered sortable",
                 "data-toggle": "table"
                 }

@login_required()
def search_helmet(request):
    """
        Funzione che si occupa di visualizzare sullo store solo prodotti di categoria casco.

        :return:
                La pagina che prevede la visualizzazione solo di articoli di categoria casco.
    """
    products = Product.objects.filter(category='Casco').order_by('price')
    context = {'products': products}
    return render(request, 'store/helmet.html', context)


@login_required()
def search_gloves(request):
    """
            Funzione che si occupa di visualizzare sullo store solo prodotti di categoria guanti.

            :return:
                    La pagina che prevede la visualizzazione solo di articoli di categoria guanti.
    """
    products = Product.objects.filter(category='Guanti').order_by('price')
    context = {'products': products}
    return render(request, 'store/gloves.html', context)


@login_required()
def search_jacket(request):
    """
            Funzione che si occupa di visualizzare sullo store solo prodotti di categoria giacca.

            :return:
                    La pagina che prevede la visualizzazione solo di articoli di categoria giacca.
    """
    products = Product.objects.filter(category='Giacca').order_by('price')
    context = {'products': products}
    return render(request, 'store/jacket.html', context)


@login_required()
def search_trousers(request):
    """
            Funzione che si occupa di visualizzare sullo store solo prodotti di categoria pantaloni.

            :return:
                    La pagina che prevede la visualizzazione solo di articoli di categoria pantaloni.
    """
    products = Product.objects.filter(category='Pantaloni').order_by('price')
    context = {'products': products}
    return render(request, 'store/trousers.html', context)


@login_required()
def search_suit(request):
    """
            Funzione che si occupa di visualizzare sullo store solo prodotti di categoria tuta.

            :return:
                    La pagina che prevede la visualizzazione solo di articoli di categoria tuta.
    """
    products = Product.objects.filter(category='Tuta').order_by('price')
    context = {'products': products}
    return render(request, 'store/suit.html', context)


@login_required()
def search_boots(request):
    """
            Funzione che si occupa di visualizzare sullo store solo prodotti di categoria stivali.

            :return:
                    La pagina che prevede la visualizzazione solo di articoli di categoria stivali.
    """
    products = Product.objects.filter(category='Stivali').order_by('price')
    context = {'products': products}
    return render(request, 'store/boots.html', context)


@login_required()
def search_stuff(request):
    """
            Funzione che si occupa di visualizzare sullo store solo prodotti di categoria manutenzione moto.
            :return:
                    La pagina che prevede la visualizzazione solo di articoli di categoria manutenzione moto.
    """
    products = Product.objects.filter(category='Manutenzione moto').order_by('price')
    context = {'products': products}
    return render(request, 'store/bikestuff.html', context)


@login_required()
def product_description(request, id):
    """
            Funzione che si occupa della descrizione del prodotto a cui l'utente è interessato.
            Prevede anche la funzione di recommendation sugli articoli consigliati.

            :param:
                id: id del prodotto.

            :return:
                 Ritorna la pagina che si occupa della visualizzazione dei dettagli del singolo prodotto.
    """
    product = Product.objects.get(id=id)
    logged_user = request.user

    tri = three_recommended_items(request, id)
    if tri == 0:
        tri = []

    context = {'product': product, 'logged_user': logged_user, 'tri': tri}

    return render(request, 'store/detail.html', context)


def three_recommended_items(request, id):
    """
                Fuznione che si occupa dei prodotti consigliati per l'utente, controllando di consigliare il
                prodotto stesso. Sfrutta il pacchetto textdistance e la similarità di levenshtein.
    :param:
                id: id del prodotto
    :return:
                Ritorna la lista dei prodotti consigliati
    """
    all_products = Product.objects.all()
    name_products = Product.objects.get(id=id)
    nome = name_products.name
    user_products = Product.objects.filter(user__email=request.user.email)
    all_products = all_products.difference(user_products)

    all_products_names = []
    for p in all_products:
        all_products_names.append(p.name)

    lista_nomi_prodotti = all_products_names
    lista_nomi_prodotti.remove(nome)

    user_products_names = []
    for p in all_products:
        user_products_names.append(p.name)

    if len(all_products_names) < 3:
        return 0

    import textdistance

    list = [[user_products_names[0], all_products_names[0],
             round(textdistance.levenshtein(user_products_names[0], all_products_names[0]), 4)],
            [user_products_names[0], all_products_names[1],
             round(textdistance.levenshtein(user_products_names[0], all_products_names[0]), 4)],
            [user_products_names[0], all_products_names[2],
             round(textdistance.levenshtein(user_products_names[0], all_products_names[0]), 4)]]

    # Jaro–Winkler distance is a measure of edit distance which gives more similar measures to words in which
    # the beginning characters match.

    from django.db.models import Q
    list = Product.objects.filter(Q(name=list[0][1]) | Q(name=list[1][1]) | Q(name=list[2][1]))
    return list
