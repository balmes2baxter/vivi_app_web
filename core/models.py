from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class Cliente(models.Model):
    """Representa a un cliente del gimnasio"""

    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)

    # Relación opcional con User de Django (para login futuro)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cliente",
    )

    class Meta:
        db_table = "clientes"
        ordering = ["-fecha_registro"]
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.nombre


class Plan(models.Model):
    """Define los planes de membresía que ofrece el gimnasio"""

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_dias = models.PositiveIntegerField(help_text="Duración en días")

    class Meta:
        db_table = "planes"
        ordering = ["precio"]
        verbose_name = "Plan"
        verbose_name_plural = "Planes"

    def __str__(self):
        return f"{self.nombre} - {self.precio}"


class Membresia(models.Model):
    """Une a un cliente con un plan en un periodo de tiempo"""

    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="membresias"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="membresias")
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(blank=True, null=True)  # se calcula si no está
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = "membresias"
        ordering = ["-fecha_inicio"]
        verbose_name = "Membresía"
        verbose_name_plural = "Membresías"
        indexes = [
            models.Index(fields=["cliente", "plan"], name="idx_cliente_plan"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(fecha_fin__gte=models.F("fecha_inicio")),
                name="fecha_fin_mayor_inicio",
            ),
            models.UniqueConstraint(
                fields=["cliente", "plan", "fecha_inicio"],
                name="unique_membresia_cliente_plan_fecha_inicio",
            ),
        ]

    def save(self, *args, **kwargs):
        # Si no hay fecha_fin, se calcula automáticamente
        if not self.fecha_fin and self.plan:
            self.fecha_fin = self.fecha_inicio + timedelta(days=self.plan.duracion_dias)
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.cliente.nombre} - {self.plan.nombre} "
            f"({self.fecha_inicio} a {self.fecha_fin})"
        )


class Pago(models.Model):
    """Registro de un pago realizado por un cliente"""

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="pagos")
    membresia = models.ForeignKey(
        Membresia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pagos",
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(default=timezone.now)
    metodo_pago = models.CharField(
        max_length=50, choices=[("efectivo", "Efectivo"), ("tarjeta", "Tarjeta")]
    )
    estado = models.CharField(
        max_length=20,
        choices=[("pendiente", "Pendiente"), ("pagado", "Pagado")],
        default="pendiente",
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text="ID único de la transacción (ej: generado por el banco o sistema)",
    )

    class Meta:
        db_table = "pagos"
        ordering = ["-fecha_pago"]
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        indexes = [
            models.Index(fields=["cliente"], name="idx_pago_cliente"),
            models.Index(fields=["transaction_id"], name="idx_pago_tx"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(monto__gte=0), name="monto_non_negative"
            )
        ]

    def __str__(self):
        return f"Pago {self.monto} - {self.cliente.nombre} ({self.estado})"
