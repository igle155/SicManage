from django.contrib import admin
from .models import CuentaContable, AsientoContable, DetalleAsiento

class DetalleAsientoInline(admin.TabularInline):
    model = DetalleAsiento
    extra = 1

@admin.register(AsientoContable)
class AsientoContableAdmin(admin.ModelAdmin):
    inlines = [DetalleAsientoInline]
    list_display = ('id', 'fecha', 'descripcion', 'total_debe', 'total_haber')
    search_fields = ('descripcion',)

@admin.register(CuentaContable)
class CuentaContableAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'nivel', 'padre')
    search_fields = ('codigo', 'nombre')

admin.site.register(DetalleAsiento)
