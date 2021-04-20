from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name = 'index'),
    path('logout',views.logout, name = 'logout'),
    # path('login',views.login, name = 'login'),
    path('dashboard',views.dashboard, name = 'dashboard'),
    path('signup',views.register, name = 'register'),
    path('decision',views.decision,name = 'decisions'),
    path('customQuery',views.customQuery, name = 'customQuery'),
    path('explore',views.explore, name = 'explore'),
    path('graph',views.graph, name = 'graph'),

    path("home", views.home, name = "home"),
    path("category/", views.category, name="category"),
    path("product/", views.product, name="product"),
    path("customer/", views.customer, name="customer"),
    path("returns/", views.returns, name="returns"),
    # path("graph/", views.graph, name="graph"),
]
