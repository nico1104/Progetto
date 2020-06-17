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
    path('add', views.product_insert, name='add-product'),
    path('user/login', auth_views.LoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('signup/cliente/', views.CustomerSignUpView.as_view(), name='customer_signup'),
    path('signup/fornitore/', views.SellerSignUpView.as_view(), name='seller_signup'),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('delete/<int:id>', views.product_delete, name='delete'),
    path('load_product', views.loaded_product_view, name='load-product'),
    path('profile', views.profile_view, name='profile'),

]


