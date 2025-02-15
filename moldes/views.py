# Importaciones de Django estándar
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.generic import DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Importaciones de modelos
from .models import Category, Product, Client, Purchase, PurchaseItem, ProductImage

# Importaciones de formularios
from .forms import ClientForm, ProductForm, PurchaseForm, PurchaseItemFormSet, ProductImageFormSet

#VISTA HOME 
def home(request):
    categories = Category.objects.filter(shows_in_home=True)  # Obtener categorías visibles en home
    return render(request, 'home.html', {'categories': categories})

#VISTA DE PRODUCTOS DETALLADOS POR CATEGORIA
def category_products(request, pk):
    category = Category.objects.get(pk=pk)  # Obtén la categoría
    products = category.products.filter(shows_in_catalog=True) 
    return render(request, 'category_products.html', {'category': category, 'products': products})

#Esta clase es como un @login_requiered pero para vistas basadas en clases__________________________________
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
    
#LOGIN OCULTO, SOLO PARA ADMINISTRADORES
class AdminLoginView(LoginView):
    template_name = 'admin_login.html'

def admin_login(request):
    return AdminLoginView.as_view()(request)

#AQUI COMIENZAN LAS VISTAS PARA CRUD CLIENTES_____________________________________________________________________

# Vista para mostrar todos los clientes en una tabla
@login_required
def client_list(request):
    clients = Client.objects.all() 
    return render(request, 'client_list.html', {'clients': clients})

#Vista para crear un nuevo cliente
@login_required
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
@login_required
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
@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)  # Obtiene el cliente por su ID
    if request.method == 'POST':
        client.delete()  # Elimina el cliente
        return redirect('client_list')  # Redirige a la lista de clientes
    return render(request, 'client_confirm_delete.html', {'client': client})

#AQUI COMIENZAN LAS VISTAS PARA COMPRAS y CRUD COMPRAS_____________________________________________________________________

#Muestra todas las compras
@login_required
def purchase_list(request):
    purchases = Purchase.objects.all()
    return render(request, 'purchase_list.html', {'purchases': purchases})

#Esta clase muestra los detalles de una compra

class PurchaseDetailView(AdminRequiredMixin, DetailView):
    model = Purchase
    template_name = 'purchase_detail.html'
    context_object_name = 'purchase'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()  # Obtiene los PurchaseItem relacionados con la compra
        return context

#Crea una compra
@login_required
def create_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        formset = PurchaseItemFormSet(request.POST)

        print("Datos del formulario principal:", request.POST)
        print("Datos del formset:", request.POST.getlist('form-0-product'))  # Verifica que haya múltiples productos

        if form.is_valid() and formset.is_valid():
            purchase = form.save()
            formset.instance = purchase  # Asigna la compra al formset antes de guardar
            formset.save()
            purchase.recalculate_total()
            return redirect('purchase_list')
        else:
            print("Errores en el form:", form.errors)
            print("Errores en el formset:", formset.errors)
    else:
        form = PurchaseForm()
        formset = PurchaseItemFormSet()

    return render(request, 'purchase_form.html', {'form': form, 'formset': formset})

#AQUI COMIENZAN LAS VISTAS PARA 'CATEGORY'_____________________________________________________________________

#Vista para agregar categorias nuevas
@login_required
def create_category(request):
    if request.method == 'POST': #verifica si la solicitud es de tipo POST, es decir que se envio datos desde un formulario
        category_name = request.POST.get('category_name')
        shows_in_home = request.POST.get('shows_in_home') == 'on'

        # Valida que el nombre de la categoria no se repita
        if Category.objects.filter(category_name=category_name).exists():
            messages.error(request, 'Ya existe una categoría con este nombre.')
            return render(request, 'category_form.html')

        # Crear la categoría
        Category.objects.create(category_name=category_name, shows_in_home=shows_in_home)
        messages.success(request, 'Categoría creada exitosamente.')
        return redirect('home')

    return render(request, 'category_form.html')

# Vista basada en clases para crear un producto y subir imagenes___________________________________________________________
class ProductCreateView(AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = ProductImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['image_formset'] = ProductImageFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        if form.is_valid() and image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))