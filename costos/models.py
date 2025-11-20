from django.db import models
from contabilidad.models import CuentaContable

class Recurso(models.Model):
    TIPO_RECURSO = [
        ('material', 'Material Directo'),
        ('mano_obra', 'Mano de Obra Directa'),
        ('indirecto', 'Costo Indirecto de Fabricación'),
    ]
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_RECURSO)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cuenta_contable = models.ForeignKey(CuentaContable, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    cantidad_producida = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nombre


class CostoProduccion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    def save(self, *args, **kwargs):
        # Calcula el subtotal cada vez que se guarda el objeto
        if self.recurso and self.cantidad:
            self.subtotal = self.cantidad * self.recurso.costo_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} - {self.recurso.nombre} (${self.subtotal})"

    class Meta:
        verbose_name = "Costo de Producción"
        verbose_name_plural = "Costos de Producción"
