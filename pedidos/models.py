from django.core.validators import MinValueValidator
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Ingrediente(models.Model):
    UNIDADES = [
        ('g', 'Gramos (g)'),
        ('kg', 'Kilogramos (kg)'),
        ('ml', 'Mililitros (ml)'),
        ('l', 'Litros (l)'),
        ('u', 'Unidades (u)'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    unidad_medida = models.CharField(max_length=5, choices=UNIDADES, default='g')
    stock_actual = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text="Cantidad disponible en depósito/cocina"
    )
    stock_minimo_alerta = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Umbral para avisar si falta reponer"
    )

    class Meta:
        verbose_name = "Ingrediente / Materia Prima"
        verbose_name_plural = "Ingredientes y Materias Primas"

    def esta_bajo_stock(self):
        return self.stock_actual <= self.stock_minimo_alerta

    def __str__(self):
        return f"{self.nombre} ({self.stock_actual} {self.unidad_medida})"


class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    stock_disponible = models.PositiveIntegerField(default=0, help_text="Cantidad de unidades listas para venta")
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


class RecetaItem(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='ingredientes_receta')
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name='usado_en_recetas')
    cantidad_requerida = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        help_text="Cantidad requerida para elaborar 1 unidad de este producto"
    )

    class Meta:
        verbose_name = "Ingrediente de Receta"
        verbose_name_plural = "Ingredientes de Receta"
        unique_together = ('producto', 'ingrediente')

    def __str__(self):
        return f"{self.cantidad_requerida} {self.ingrediente.unidad_medida} de {self.ingrediente.nombre} para {self.producto.nombre}"


class ConfiguracionProduccion(models.Model):
    limite_pedidos_diarios = models.PositiveIntegerField(
        default=5, 
        help_text="Máximo de pedidos que la cocina puede elaborar por día"
    )

    class Meta:
        verbose_name = "Configuración de Capacidad Diaria"
        verbose_name_plural = "Configuraciones de Capacidad"

    def __str__(self):
        return f"Cupo Máximo Diario: {self.limite_pedidos_diarios} pedidos"


class Pedido(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de confirmación'),
        ('CONFIRMADO', 'En producción / Confirmado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    cliente_nombre = models.CharField(max_length=150)
    cliente_telefono = models.CharField(max_length=30)
    cliente_email = models.EmailField(
        verbose_name="Correo Electrónico",
        blank=True, 
        null=True, 
        help_text="Para recibir el comprobante de su encargo"
    )
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField()
    notas = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    comprobante_sena = models.FileField(upload_to='comprobantes/', blank=True, null=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_entrega']

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente_nombre} ({self.fecha_entrega.strftime('%d/%m/%Y %H:%M')})"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Detalle del Pedido"
        verbose_name_plural = "Detalles del Pedido"

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"