from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP

def upload_to_category(instance, filename):
    return f'Categoria/{instance.category_name}/{filename}'

#Define la categoria en la que los productos se clasificaran.
class Category(models.Model): 
    category_name = models.CharField(max_length=255, unique=True)
    shows_in_home = models.BooleanField(default=False, verbose_name='¿Mostrar categoria en home?') #Determina si la categoria se exhibira o no en el home para el publico general.
    category_image = models.ImageField(upload_to=upload_to_category, null=True, blank=True, verbose_name="Imagen de la Categoría")
    def __str__(self):
        return self.category_name
    
    def delete(self, *args, **kwargs): #Esta funcion solo elimina categorias cuando no tiene productos asociados
        if self.products.exists():
            raise ValidationError("No se puede eliminar esta categoría, por que tiene productos asociados.") 

class Product(models.Model):
    name = models.CharField(max_length=40, unique=True, verbose_name="Nombre")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True, related_name="products")
    description = models.TextField(blank=True) 
# En los siguientes atributos podemos encontrar todas las medidas generales que un molde podria tener
    length = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="Largo", null=True, blank=True, validators=[MinValueValidator(0.0)])
    wide = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="Ancho", null=True, blank=True, validators=[MinValueValidator(0.0)])
    height = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="Altura", null=True, blank=True, validators=[MinValueValidator(0.0)])
    diameter = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="Diametro", null=True, blank=True, validators=[MinValueValidator(0.0)])
    superior_diameter = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="Diametro superior", null=True, blank=True, validators=[MinValueValidator(0.0)])
    inferior_diameter = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="Diametro inferior", null=True, blank=True, validators=[MinValueValidator(0.0)])
#define el material con el que pueden ser elaborados los moldes
    MATERIAL_CHOICES = [ 
        ('INOX_04', 'Acero Inoxidable 0.4mm de espesor'),
        ('INOX_05', 'Acero Inoxidable 0.5mm de espesor'),
        ('INOX_06', 'Acero Inoxidable 0.6mm de espesor'),
        ('ALUM_04', 'Aluminio 0.4mm de espesor'),
        ('ALUM_07', 'Aluminio 0.7mm de espesor'),
        ('TOL_04', 'Tol Galvanizado 0.4mm de espesor'),
    ]
    material = models.CharField(max_length=15, choices=MATERIAL_CHOICES, default='INOX_04', verbose_name="Material")
    shows_in_catalog = models.BooleanField(default=False, verbose_name='¿Mostrar en catalogo publico?') #Determina si el producto se exhibira o no en el catalogo para el publico general.   
         
    def __str__(self):
        return self.name

#Esta funcion independiente, genera la ruta de almacenamiento dinamica de las imagenes en 'MEDIA/Categoria/<Nombre_Categoria>/<Nombre_Producto>/' 
def product_image_upload_path(instance, filename):
    category_name = instance.product.category.category_name if instance.product.category else "Sin_Categoria"
    return f"Categoria/{category_name}/{instance.product.name}/{filename}" #Este path esta asociado a MEDIA_ROOT en settings.py

#Este modelo nos permite subir una o varias imagenes de un mismo producto.
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=product_image_upload_path, verbose_name="Imagen del producto")

    def __str__(self):
        return f"Imagen de {self.product.name}"

class Client(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="Nombre Completo")
    email = models.EmailField(unique=True, blank=True, verbose_name="Correo Electrónico")
    cellphone = models.CharField(max_length=10, null=True, blank=True, verbose_name="Teléfono",
        validators=[RegexValidator(regex=r'^\d{10}$', message="El número de teléfono debe contener exactamente 10 dígitos.")])
    address = models.TextField(null=True, blank=True, verbose_name="Dirección")
    bussiness = models.CharField(max_length=100, null=True, blank=True, verbose_name="Negocio") #En este campo describo el nombre del negocio de mi cliente, en caso de tener uno.

    def __str__(self):
        return self.full_name
    
#Define una Compra
class Purchase(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name='Cliente')  
    delivery_date = models.DateField(verbose_name='Fecha de entrega') #Por practicidad del negocio usamos la fecha en la que el producto debera ser entregado, y no la fecha en la que se realiza el pedido  
    PURCHASE_STATUS_CHOICES = [
        ('FABRICAR', 'Por Fabricar'),
        ('STOCK', 'En Stock'),  
        ('ENTREGADO', 'Entregado Por Cobrar'),
        ('SOLO_COBRADO', 'Solo Cobrado, No entregado'), 
        ('COBRADO_ENTREGADO', 'Entregado y Cobrado'), 
    ]
    purchase_status = models.CharField(max_length=18, choices=PURCHASE_STATUS_CHOICES, default='FABRICAR', verbose_name="Estado de la Venta")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total de la compra") #Si bien los productos individuales pueden tener varios decimales, al momento de sumar el total usaremos dos decimales

    class Meta:
        ordering = ['-delivery_date'] #Permite ordenar por fecha descendente

    def recalculate_total(self): #Recalcula el total sumando los subtotales de todos los productos en la compra.
        total = sum(item.subtotal() for item in self.items.all())
        self.total_price = total
        self._internal_update = True  # Marcamos que es una actualización interna, para que me permita editar compras
        self.save(update_fields=['total_price'])

    def delete(self, *args, **kwargs): #Evita la eliminación de compras si el estado no es 'FABRICAR' o 'STOCK'.
        if self.purchase_status not in ['FABRICAR', 'STOCK']:
            raise ValidationError(f"No se pueden eliminar las compras de tipo {self.get_purchase_status_display()}")
        super().delete(*args, **kwargs)
    
    def save(self, *args, **kwargs): #Evita modificaciones manuales en el campo total_price, excepto si es una actualización interna.
        if hasattr(self, '_internal_update') and self._internal_update:
            self._internal_update = False # Si es una actualización interna, omitimos la validación
        elif self.pk:
            original = Purchase.objects.get(pk=self.pk)
            if self.total_price != original.total_price:
                raise ValidationError("El campo 'PRECIO TOTAL' es informativo y no puede ser editado manualmente.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Compra {self.id} - {self.client.full_name} - {self.delivery_date}"

#Define los productos individuales que se agregaran a las compras, pueden ser variso productos en una sola compra
class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="items")  
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Producto')  
    amount = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])  
    unitary_price = models.DecimalField(max_digits=11, decimal_places=8) #Algunos productos individuales tienen hasta 8 decimales de precision  

    def subtotal(self): #Calcula el subtotal de este producto en la compra
        subtotal_value = self.amount * self.unitary_price
        return subtotal_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)  # Redondea a 2 decimales

    def save(self, *args, **kwargs): #Guarda el item y actualiza el total de la compra.
        super().save(*args, **kwargs)
        self.purchase.recalculate_total()

    def delete(self, *args, **kwargs): #Elimina el item y actualiza el total de la compra.
        super().delete(*args, **kwargs)
        self.purchase.recalculate_total()

    def __str__(self):
        return f"{self.amount} x {self.product.name} en Compra {self.purchase.id}"