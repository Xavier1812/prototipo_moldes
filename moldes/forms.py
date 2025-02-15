from django import forms
from .models import Client
from django.forms import inlineformset_factory
from .models import Purchase, PurchaseItem

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'  # O puedes especificar los campos que quieres incluir

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['client', 'delivery_date', 'purchase_status']
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['product', 'amount', 'unitary_price']

PurchaseItemFormSet = inlineformset_factory(Purchase, PurchaseItem, form=PurchaseItemForm, extra=1, can_delete=True)
