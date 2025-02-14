from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Client, Purchase, PurchaseItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import ClientForm
from django.views.generic import DetailView
from django.forms import inlineformset_factory

def home(request):
    categories = Category.objects.filter(shows_in_home=True)
    
    return render(request, 'home.html', {'categories': categories})

def category_products(request, pk):
    category = Category.objects.get(pk=pk)  # Obtén la categoría
    products = category.products.filter(shows_in_catalog=True) 
    
    return render(request, 'category_products.html', {'category': category, 'products': products})


#LOGIN OCULTO, SOLO PARA ADMINISTRADORES
class AdminLoginView(LoginView):
    template_name = 'admin_login.html'

def admin_login(request):
    return AdminLoginView.as_view()(request)

#AQUI COMIENZAN LAS VISTAS PARA CRUD CLIENTES
# Vista para mostrar todos los clientes en una tabla
def client_list(request):
    clients = Client.objects.all()  # Obtén todos los clientes
    return render(request, 'client_list.html', {'clients': clients})

def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el nuevo cliente
            return redirect('client_list')  # Redirige a la lista de clientes
    else:
        form = ClientForm()  # Formulario vacío

    return render(request, 'client_create.html', {'form': form})

# Vista para editar un cliente
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)  # Obtén el cliente por su ID
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)  # Rellena el formulario con los datos actuales del cliente
        if form.is_valid():
            form.save()  # Guarda los cambios
            return redirect('client_list')  # Redirige a la lista de clientes
    else:
        form = ClientForm(instance=client)  # Carga el formulario vacío con los datos del cliente

    return render(request, 'client_edit.html', {'form': form, 'client': client})

# Vista para eliminar un cliente
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)  # Obtén el cliente por su ID
    if request.method == 'POST':
        client.delete()  # Elimina el cliente
        return redirect('client_list')  # Redirige a la lista de clientes
    return render(request, 'client_confirm_delete.html', {'client': client})

#AQUI COMIENZAN LAS VISTAS PARA COMPRAS y CRUD COMPRAS
#Muestra todas las compras
def purchase_list(request):
    purchases = Purchase.objects.all()  # Obtén todas las compras
    return render(request, 'purchase_list.html', {'purchases': purchases})

#Esta clase muestra los detalles de una compra
class PurchaseDetailView(DetailView):
    model = Purchase
    template_name = 'purchase_detail.html'
    context_object_name = 'purchase'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()  # Obtiene los PurchaseItem relacionados con la compra
        return context
