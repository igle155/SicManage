from django.db import models
from django.utils import timezone
from decimal import Decimal
from contabilidad.models import CuentaContable, AsientoContable, DetalleAsiento
from costos.models import Producto


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    nit = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Factura(models.Model):
    numero = models.CharField(max_length=15, unique=True)
    fecha = models.DateField(default=timezone.now)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calcular_totales(self):
        detalles = self.detallefactura_set.all()
        subtotal = sum([detalle.subtotal for detalle in detalles])
        iva = subtotal * Decimal('0.13')
        total = subtotal + iva
        self.subtotal = subtotal
        self.iva = iva
        self.total = total
        self.save()

    def generar_asiento_contable(self):
        """
        Crea automáticamente un asiento contable cuando se registra la factura.
        """
        # Evita duplicar asientos para la misma factura
        if AsientoContable.objects.filter(descripcion__icontains=self.numero).exists():
            return

        # Crea el asiento principal
        asiento = AsientoContable.objects.create(
            fecha=self.fecha,
            descripcion=f"Registro de venta - Factura {self.numero}",
            total_debe=self.total,
            total_haber=self.total
        )

        # Recupera las cuentas contables base
        cuenta_ventas = CuentaContable.objects.filter(nombre__icontains='Ventas').first()
        cuenta_iva = CuentaContable.objects.filter(nombre__icontains='IVA por pagar').first()
        cuenta_clientes = CuentaContable.objects.filter(nombre__icontains='Cuentas por cobrar').first()

        # Si alguna cuenta falta, no genera asiento
        if not (cuenta_ventas and cuenta_iva and cuenta_clientes):
            return

        # Detalle 1: Cuentas por cobrar (Debe)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta=cuenta_clientes,
            descripcion=f"Cuenta por cobrar de factura {self.numero}",
            debe=self.total,
            haber=0
        )

        # Detalle 2: Ventas (Haber)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta=cuenta_ventas,
            descripcion="Ingreso por ventas",
            debe=0,
            haber=self.subtotal
        )

        # Detalle 3: IVA por pagar (Haber)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta=cuenta_iva,
            descripcion="IVA generado por venta",
            debe=0,
            haber=self.iva
        )

    def __str__(self):
        return f"Factura #{self.numero} - {self.cliente.nombre}"

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-fecha']


class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    def save(self, *args, **kwargs):
        # Calcula el subtotal
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

        # Actualiza los totales de la factura
        self.factura.calcular_totales()

        # Genera el asiento contable automáticamente
        self.factura.generar_asiento_contable()

    def __str__(self):
        return f"{self.producto.nombre} ({self.cantidad} x ${self.precio_unitario})"

    class Meta:
        verbose_name = "Detalle de factura"
        verbose_name_plural = "Detalles de factura"
