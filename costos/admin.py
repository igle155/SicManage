from django.contrib import admin
from .models import Recurso, Producto, CostoProduccion
from django.db.models import Sum
from decimal import Decimal

class CostoProduccionInline(admin.TabularInline):
    model = CostoProduccion
    extra = 1
    readonly_fields = ('subtotal',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    inlines = [CostoProduccionInline]
    list_display = ('nombre', 'cantidad_producida', 'mostrar_costo_total', 'mostrar_costo_unitario')

    def mostrar_costo_total(self, obj):
        total = obj.costoproduccion_set.aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
        return f"${total:,.2f}"
    mostrar_costo_total.short_description = "Costo total"

    def mostrar_costo_unitario(self, obj):
        total = obj.costoproduccion_set.aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
        cantidad = obj.cantidad_producida if obj.cantidad_producida > 0 else 1
        unitario = total / Decimal(cantidad)
        return f"${unitario:,.2f}"
    mostrar_costo_unitario.short_description = "Costo unitario"

@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'costo_unitario', 'cuenta_contable')
    search_fields = ('nombre',)

@admin.register(CostoProduccion)
class CostoProduccionAdmin(admin.ModelAdmin):
    list_display = ('producto', 'recurso', 'cantidad', 'subtotal')
