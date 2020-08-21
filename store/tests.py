from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from .models import *
from django.urls import reverse

User = get_user_model()


class TestViews(TestCase):

    def setUp(self):
        self.customer_test = User.objects.create_user(
            username="Customer",
            password="Registration9",
            is_customer=True
        )

        self.seller_test = User.objects.create_user(
            username="Seller",
            password="Registration9",
            is_seller=True
        )

    def customerLogin(self):
        self.client.login(username="Customer", password="Registration9")

    def sellerLogin(self):
        self.client.login(username="Seller", password="Registration9")

    def test_profilo_no_logged_user(self):
        response = self.client.get(reverse('store:profile'))
        self.assertEquals(response.status_code, 302, "Utente non loggato va reindirizzato")
        self.assertRedirects(response, '/accounts/login/?next=/profile', status_code=302, target_status_code=200)

    def test_profilo_logged_cliente(self):
        self.customerLogin()
        response = self.client.get(reverse('store:profile'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/user_profile.html')

    def test_profilo_logged_pt(self):
        self.customerLogin()
        response = self.client.get(reverse('store:profile'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/user_profile.html')


class TestOrderItem(TestCase):

    def test_orderitem(self):
        product = Product()
        product.price = 200
        product.save()

        order = Order()
        order.save()

        item = OrderItem()
        item.product = product
        item.order = order
        item.quantity = 2
        item.size = "XS"
        item.date_added = "2019/04/04"
        item.save()
        self.assertEquals(400, item.get_total)

        item.quantity = 4
        item.save()

        self.assertEquals(800, item.get_total)
