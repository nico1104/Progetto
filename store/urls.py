from django.urls import include, path
from django.contrib.auth import views as auth_views
from store import views

from . import views

app_name = 'store'

urlpatterns = [
    # Leave as empty string for base url
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('user/login', auth_views.LoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('signup/cliente/', views.CustomerSignUpView.as_view(), name='customer_signup'),
    path('signup/fornitore/', views.SellerSignUpView.as_view(), name='seller_signup'),

]


