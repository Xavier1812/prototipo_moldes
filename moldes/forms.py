from django import forms
from django.forms import inlineformset_factory

from .models import Client, Product, ProductImage, Purchase, PurchaseItem

#CREA UN FORMULARIO BASADO EN EL MODELO 'Client'
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__' #Incluye todos los campos del modelo 'Client'
        
#PERMITE GESTIONAR LA CREACION Y EDICION DE COMPRAS 'Purchase'
class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['client', 'delivery_date', 'purchase_status']
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}), #Personaliza 'delivery_date' para que se muestre como un date pycker
        }

#DEFINE UN FORMULARIO  PARA EL MODELO 'PurchaseItem'
class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['product', 'amount', 'unitary_price']

PurchaseItemFormSet = inlineformset_factory(Purchase, PurchaseItem, form=PurchaseItemForm, extra=1, can_delete=True) #Permite manejar varios 'PurchaseItems' dentro de una 'Purchase'

#DEFINE EL FORMULARIO PARA CREARA NUEVOS PRODUCTOS
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'  # Incluye todos los campos de 'Product'

class ProductImageForm(forms.ModelForm): #Permite asociar varias imagenes a un 'Product'
    class Meta:
        model = ProductImage
        fields = ['image']
        
ProductImageFormSet = forms.inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=3, can_delete=True) ## FormSet para manejar múltiples imágenes, Muestra 3 formularios vacios para imagenes