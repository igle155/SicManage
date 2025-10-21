from django.db import models
from django.utils import timezone

class CuentaContable(models.Model):
    TIPO_CUENTA = [
        ('activo', 'Activo'),
        ('pasivo', 'Pasivo'),
        ('patrimonio', 'Patrimonio'),
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
        ('costo', 'Costo'),
    ]

    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CUENTA)
    nivel = models.PositiveIntegerField(default=1)
    padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        verbose_name = "Cuenta contable"
        verbose_name_plural = "Cuentas contables"
        ordering = ['codigo']


class AsientoContable(models.Model):
    fecha = models.DateField(default=timezone.now)
    descripcion = models.TextField()
    total_debe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_haber = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Asiento #{self.id} - {self.fecha}"

    class Meta:
        verbose_name = "Asiento contable"
        verbose_name_plural = "Asientos contables"
        ordering = ['-fecha']


class DetalleAsiento(models.Model):
    asiento = models.ForeignKey(AsientoContable, on_delete=models.CASCADE, related_name='detalles')
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.PROTECT)
    descripcion = models.CharField(max_length=150)
    debe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    haber = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.cuenta.nombre} - Debe: {self.debe} / Haber: {self.haber}"

    class Meta:
        verbose_name = "Detalle de asiento"
        verbose_name_plural = "Detalles de asientos"
