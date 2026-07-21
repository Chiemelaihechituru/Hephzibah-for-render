from django.urls import path

from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.all_products, name='all_products'),
    path('search/', views.search, name='search'),
    path('wholesale/', views.wholesale, name='wholesale'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]
