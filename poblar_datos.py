import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from pedidos.models import Categoria, Producto, Ingrediente, ConfiguracionProduccion

def poblar():
    # 1. Configuración de capacidad diaria
    config, _ = ConfiguracionProduccion.objects.get_or_create(id=1)
    config.limite_pedidos_diarios = 6
    config.save()

    # 2. Categorías
    cat_tortas, _ = Categoria.objects.get_or_create(
        nombre='Tortas Artesanales',
        defaults={'descripcion': 'Tortas temáticas y para eventos especiales.'}
    )
    cat_tartas, _ = Categoria.objects.get_or_create(
        nombre='Tartas Dulces',
        defaults={'descripcion': 'Tartas clásicas con frutas y cremas.'}
    )
    cat_postres, _ = Categoria.objects.get_or_create(
        nombre='Postres Individuales',
        defaults={'descripcion': 'Porciones y bocados dulces.'}
    )

    # 3. Productos del Catálogo
    productos_demo = [
        {
            'categoria': cat_tortas,
            'nombre': 'Torta Selva Negra',
            'descripcion': 'Bizcochuelo húmedo de chocolate, crema chantilly, cerezas y virutas de chocolate semiamargo.',
            'precio': Decimal('18500.00'),
            'stock_disponible': 4,
            'activo': True,
        },
        {
            'categoria': cat_tortas,
            'nombre': 'Red Velvet Clásica',
            'descripcion': 'Suave bizcocho aterciopelado con relleno y cobertura de frosting de queso crema.',
            'precio': Decimal('19500.00'),
            'stock_disponible': 3,
            'activo': True,
        },
        {
            'categoria': cat_tartas,
            'nombre': 'Lemon Pie Tradicional',
            'descripcion': 'Base crocante de masa sablée, curd artesanal de limón y merengue italiano flameado.',
            'precio': Decimal('13500.00'),
            'stock_disponible': 5,
            'activo': True,
        },
        {
            'categoria': cat_tartas,
            'nombre': 'Tarta de Frutillas con Crema',
            'descripcion': 'Base de masa fina, crema pastelera suave y abundantes frutillas frescas de estación.',
            'precio': Decimal('14800.00'),
            'stock_disponible': 4,
            'activo': True,
        },
        {
            'categoria': cat_postres,
            'nombre': 'Cheesecake Frutos Rojos',
            'descripcion': 'Tarta horneada de queso Philadelphia con coulis de frutos del bosque.',
            'precio': Decimal('16000.00'),
            'stock_disponible': 2,
            'activo': True,
        },
    ]

    for p_data in productos_demo:
        Producto.objects.get_or_create(
            nombre=p_data['nombre'],
            defaults=p_data
        )

    # 4. Insumos básicos para control de stock
    ingredientes_demo = [
        {'nombre': 'Harina 0000', 'unidad_medida': 'kg', 'stock_actual': Decimal('15.0'), 'stock_minimo_alerta': Decimal('5.0')},
        {'nombre': 'Azúcar común', 'unidad_medida': 'kg', 'stock_actual': Decimal('8.5'), 'stock_minimo_alerta': Decimal('4.0')},
        {'nombre': 'Crema de Leche', 'unidad_medida': 'l', 'stock_actual': Decimal('3.0'), 'stock_minimo_alerta': Decimal('2.0')},
        {'nombre': 'Frutillas', 'unidad_medida': 'kg', 'stock_actual': Decimal('1.2'), 'stock_minimo_alerta': Decimal('2.5')}, # Crítico
    ]

    for ing in ingredientes_demo:
        Ingrediente.objects.get_or_create(
            nombre=ing['nombre'],
            defaults=ing
        )

    print(">>> Datos de demostración (categorías, productos e insumos) cargados exitosamente.")

if __name__ == '__main__':
    poblar()