from django.urls import include, path
from store import views

from . import views

urlpatterns = [
    # Leave as empty string for base url
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup.html/', views.SignUpView.as_view(), name='signup.html'),
    path('accounts/signup.html/customer/', views.CustomerSignUpView.as_view(), name='customer_signup'),
    path('accounts/signup.html/seller/', views.SellerSignUpView.as_view(), name='seller_signup'),

]
