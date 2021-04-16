from django.urls import path
from .import views

urlpatterns = [
    path("", views.home, name = "home"),
    path("category/", views.category, name="category"),
    path("product/", views.product, name="product"),
    path("customer/", views.customer, name="customer"),
    path("returns/", views.returns, name="returns"),
    path("graph/", views.graph, name="graph"),
]