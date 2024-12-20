from django.urls import path
from . import views

urlpatterns = [
    path('/products//', views.list_products, name='list_products'),
    path('/products//', views.create_product, name='create_product'),
    path('/products/<int:id>//', views.get_product, name='get_product'),
    path('/products/<int:id>//', views.update_product, name='update_product'),
    path('/products/<int:id>//', views.delete_product, name='delete_product'),
]
