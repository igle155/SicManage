from django.contrib import admin
from .models import Cliente, Factura, DetalleFactura

class DetalleFacturaInline(admin.TabularInline):
    model = DetalleFactura
    extra = 1
    readonly_fields = ('subtotal',)

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    inlines = [DetalleFacturaInline]
    list_display = ('numero', 'cliente', 'fecha', 'subtotal', 'iva', 'total')
    search_fields = ('numero', 'cliente__nombre')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nit', 'telefono')
    search_fields = ('nombre', 'nit')

