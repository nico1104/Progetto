from django.contrib.auth import login
from pyexpat.errors import messages

from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView

from .forms import ProductForm, CustomerSignUpForm, SellerSignUpForm
from .models import *


def store(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}

    context = {'items': items, 'order': order}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}

    context = {'items': items, 'order': order}
    return render(request, 'store/checkout.html', context)


def add_to_cart(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            cart_add = form.save(commit=False)
            size = form.cleaned_data.get('size')
            cart_add.save()
            messages.success(request, 'Aggiunto al carrello')
            return redirect('store/store.html')
        else:
            messages.error(request, 'Impossibile aggiungere il prodotto al carrello')
    else:
        form = ProductForm()

    context = {'form': form}

    return render(request, 'store/store.html', context)


############ USER ##################


class SignUpView(TemplateView):
    template_name = 'signup.html'


def home(request):
    if request.user.is_authenticated:
        if request.user.is_seller:
            return redirect('#')
        else:
            return redirect('#')
    return render(request, '#')


class CustomerSignUpView(CreateView):
    model = User
    form_class = CustomerSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'customer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('store/store.html')


class SellerSignUpView(CreateView):
    model = User
    form_class = SellerSignUpForm
    template_name = 'registration/register.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'seller'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('store/store.html')
