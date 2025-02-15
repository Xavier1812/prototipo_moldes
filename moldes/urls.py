from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from .views import (
    ProductCreateView,
    PurchaseDetailView,
    admin_login,
    category_products,
    client_create,
    client_delete,
    client_edit,
    client_list,
    create_category,
    create_purchase,
    home,
    purchase_list,
)

urlpatterns = [
#URL PARA LA PAGINA DE INICIO 'HOME'
    path('', home, name='home'),
    path('categoria/<int:pk>/', category_products, name='category_products'),  # Productos por categoría
# Login SOLO para administradores
    path('admin-login/', admin_login, name='admin_login'), 
#URLS PARA CLIENTES
    path('clients/', client_list, name='client_list'),  # Mostrar clientes
    path('client/create/', client_create, name='client_create'),
    path('client/edit/<int:pk>/', client_edit, name='client_edit'),  # Editar cliente
    path('client/delete/<int:pk>/', client_delete, name='client_delete'),  # Eliminar cliente
#URLS PARA COMPRAS
    path('purchases/', purchase_list, name='purchase_list'),  # Mostrar todas las compras
    path('purchases/<int:pk>/', PurchaseDetailView.as_view(), name='purchase_detail'), #Detalle de compras
    path('nueva-compra/', create_purchase, name='create_purchase'),
#URL PARA AGREGAR UNA NUEVA CATEGORIA
    path('categoria/nueva/', create_category, name='category_create'),
#URL PARA AGREGAR UN NUEVO PRODUCTO
    path('producto/nuevo/', ProductCreateView.as_view(), name='product_create'),
#URL PARA LOGOUT    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)