from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path

from .views import home, category_products, admin_login, client_list, client_create, client_edit, client_delete, purchase_list, PurchaseDetailView

urlpatterns = [
    path('', home, name='home'),  # Página de inicio con categorías
    path('categoria/<int:pk>/', category_products, name='category_products'),  # Productos por categoría
    path('admin-login/', admin_login, name='admin_login'), # Login oculto para administradores
    #URLS PARA CLIENTES
    path('clients/', client_list, name='client_list'),  # Mostrar clientes
    path('client/create/', client_create, name='client_create'),
    path('client/edit/<int:pk>/', client_edit, name='client_edit'),  # Editar cliente
    path('client/delete/<int:pk>/', client_delete, name='client_delete'),  # Eliminar cliente
    #URLS PARA COMPRAS
    path('purchases/', purchase_list, name='purchase_list'),  # Mostrar todas las compras
    path('purchases/<int:pk>/', PurchaseDetailView.as_view(), name='purchase_detail'), #Detalle de compras
]