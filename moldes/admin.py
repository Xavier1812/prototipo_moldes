from django.contrib import admin
from .models import Category, Product, ProductImage ,Client, Purchase, PurchaseItem

# Registra los modelos en el administrador de Django
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Client)
admin.site.register(PurchaseItem)
admin.site.register(ProductImage)

# Personaliza la administración de Purchase para hacer total_price de solo lectura\class PurchaseAdmin(admin.ModelAdmin):
class PurchaseAdmin(admin.ModelAdmin):
    readonly_fields = ('total_price',)
    fields = ('client', 'delivery_date', 'purchase_status', 'total_price')  # Excluimos total_price de fields

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields

admin.site.register(Purchase, PurchaseAdmin)