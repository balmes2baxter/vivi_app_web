from django.contrib import admin
from .models import Plan, Cliente, Membresia, Pago


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "duracion_dias")
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "telefono", "fecha_registro", "activo")
    search_fields = ("nombre", "email")
    list_filter = ("activo",)


@admin.register(Membresia)
class MembresiaAdmin(admin.ModelAdmin):
    list_display = ("cliente", "plan", "fecha_inicio", "fecha_fin", "activa")
    list_filter = ("plan", "activa")
    search_fields = ("cliente__nombre", "cliente__email")


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "cliente",
        "monto",
        "metodo_pago",
        "estado",
        "fecha_pago",
    )
    list_filter = ("metodo_pago", "estado")
    search_fields = ("transaction_id", "cliente__email")
