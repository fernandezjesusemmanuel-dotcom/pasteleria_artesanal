from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Categoria,
    ConfiguracionProduccion,
    DetallePedido,
    Ingrediente,
    Pedido,
    Producto,
    RecetaItem,
)


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'stock_actual_formato', 'stock_minimo_alerta', 'unidad_medida', 'estado_stock')
    list_editable = ('stock_minimo_alerta',)
    search_fields = ('nombre',)

    def stock_actual_formato(self, obj):
        return f"{obj.stock_actual} {obj.unidad_medida}"
    stock_actual_formato.short_description = "Stock en Cocina"

    def estado_stock(self, obj):
        if obj.esta_bajo_stock():
            return format_html(
                '<span style="background-color: {}; color: {}; padding: 4px 8px; border-radius: 9999px; font-weight: 700; font-size: 11px;">{}</span>',
                '#fee2e2', '#991b1b', '⚠️ Reponer Urgente'
            )
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 8px; border-radius: 9999px; font-weight: 700; font-size: 11px;">{}</span>',
            '#d1fae5', '#065f46', '✔ Óptimo'
        )
    estado_stock.short_description = "Nivel de Stock"


class RecetaItemInline(admin.TabularInline):
    model = RecetaItem
    extra = 1


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('miniatura', 'nombre', 'categoria', 'precio_formato', 'stock_disponible', 'activo')
    list_editable = ('stock_disponible', 'activo')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre', 'descripcion')
    inlines = [RecetaItemInline]

    def miniatura(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="width: 42px; height: 42px; object-fit: cover; border-radius: 8px; border: 1px solid #e5e7eb;" />',
                obj.imagen.url
            )
        return format_html('<span>{}</span>', '🎂')
    miniatura.short_description = "Foto"

    def precio_formato(self, obj):
        return f"${obj.precio}"
    precio_formato.short_description = "Precio"


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario')
    can_delete = False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nombre', 'cliente_telefono', 'fecha_entrega', 'total_formato', 'estado_badge', 'ver_comprobante')
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('cliente_nombre', 'cliente_telefono', 'id')
    date_hierarchy = 'fecha_entrega'
    inlines = [DetallePedidoInline]

    def total_formato(self, obj):
        return format_html('<strong>${}</strong>', obj.total)
    total_formato.short_description = "Total"

    def estado_badge(self, obj):
        colores = {
            'PENDIENTE': ('#fef3c7', '#92400e'),
            'CONFIRMADO': ('#d1fae5', '#065f46'),
            'ENTREGADO': ('#e0e7ff', '#3730a3'),
            'CANCELADO': ('#fee2e2', '#991b1b'),
        }
        bg, text = colores.get(obj.estado, ('#f3f4f6', '#374151'))
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 10px; border-radius: 9999px; font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">{}</span>',
            bg, text, obj.get_estado_display()
        )
    estado_badge.short_description = "Estado"

    def ver_comprobante(self, obj):
        if obj.comprobante_sena:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #C86D51; color: white; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 11px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">'
                '📎 Ver Archivo'
                '</a>',
                obj.comprobante_sena.url
            )
        return format_html('<span style="color: #9ca3af; font-size: 11px;">{}</span>', 'Sin adjunto')
    ver_comprobante.short_description = "Seña"


@admin.register(ConfiguracionProduccion)
class ConfiguracionProduccionAdmin(admin.ModelAdmin):
    list_display = ('limite_pedidos_diarios',)

    def has_add_permission(self, request):
        if ConfiguracionProduccion.objects.exists():
            return False
        return True


# Configuración del encabezado y títulos del Dashboard
admin.site.site_header = "Panel de Gestión - Pastelería Artesanal"
admin.site.site_title = "Pastelería Artesanal"
admin.site.index_title = "Agenda de Entregas, Stock y Producción"