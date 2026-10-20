import urllib.parse
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import PedidoForm
from .models import Categoria, DetallePedido, Ingrediente, Pedido, Producto

PASTELERA_WHATSAPP = "5492615962434"


def catalogo(request):
    categoria_id = request.GET.get('categoria')
    productos = Producto.objects.filter(activo=True, stock_disponible__gt=0)
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
        
    categorias = Categoria.objects.all()
    return render(request, 'pedidos/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id
    })


def realizar_pedido(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True, stock_disponible__gt=0)
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES)
        
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except (ValueError, TypeError):
            cantidad = 1
        
        if form.is_valid():
            if cantidad > producto.stock_disponible:
                messages.error(request, f"Solo quedan {producto.stock_disponible} unidades disponibles.")
            else:
                with transaction.atomic():
                    # 1. Crear y guardar el pedido
                    pedido = form.save(commit=False)
                    pedido.total = producto.precio * cantidad
                    pedido.save()
                    
                    # 2. Registrar el detalle del pedido
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio
                    )
                    
                    # 3. Actualizar stock del producto terminado
                    producto.stock_disponible -= cantidad
                    if producto.stock_disponible == 0:
                        producto.activo = False
                    producto.save()

                    # 4. Descontar materia prima según la receta
                    for item_receta in producto.ingredientes_receta.all():
                        ingrediente = item_receta.ingrediente
                        total_a_descontar = item_receta.cantidad_requerida * cantidad
                        if ingrediente.stock_actual >= total_a_descontar:
                            ingrediente.stock_actual -= total_a_descontar
                        else:
                            ingrediente.stock_actual = 0
                        ingrediente.save()

                # 5. Enviar notificación por correo
                asunto = f"Confirmación de Pedido #{pedido.id} - Pastelería Artesanal"
                detalles = f"{cantidad}x {producto.nombre}"
                mensaje_correo = (
                    f"¡Hola {pedido.cliente_nombre}!\n\n"
                    f"Recibimos tu encargo correctamente.\n"
                    f"Detalle: {detalles}\n"
                    f"Total: ${pedido.total}\n"
                    f"Fecha de entrega: {pedido.fecha_entrega.strftime('%d/%m/%Y %H:%M')} hs\n\n"
                    f"Nos comunicaremos a la brevedad para coordinar la entrega.\n"
                    f"¡Muchas gracias por elegirnos!"
                )

                destinatarios = []
                if pedido.cliente_email:
                    destinatarios.append(pedido.cliente_email)
                
                email_pastelera = getattr(settings, 'PASTELERA_EMAIL', None)
                if email_pastelera:
                    destinatarios.append(email_pastelera)

                if destinatarios:
                    try:
                        send_mail(
                            subject=asunto,
                            message=mensaje_correo,
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=destinatarios,
                            fail_silently=True,
                        )
                    except Exception:
                        pass

                return redirect('confirmacion_pedido', pedido_id=pedido.id)
    else:
        form = PedidoForm()
        
    return render(request, 'pedidos/formulario_pedido.html', {
        'form': form,
        'producto': producto
    })


def confirmacion_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    detalles = pedido.detalles.all()
    items_texto = ", ".join([f"{d.cantidad}x {d.producto.nombre}" for d in detalles])
    sena_adjunta = "Sí (adjuntado en la web)" if pedido.comprobante_sena else "Pendiente de envío"

    mensaje = (
        f"¡Hola! Acabo de registrar el pedido #{pedido.id} en la web:\n\n"
        f"🍰 Detalle: {items_texto}\n"
        f"💰 Total: ${pedido.total}\n"
        f"📅 Entrega: {pedido.fecha_entrega.strftime('%d/%m/%Y %H:%M')} hs\n"
        f"👤 Cliente: {pedido.cliente_nombre}\n"
        f"🧾 Comprobante: {sena_adjunta}"
    )
    whatsapp_url = f"https://wa.me/{PASTELERA_WHATSAPP}?text={urllib.parse.quote(mensaje)}"

    return render(request, 'pedidos/confirmacion.html', {
        'pedido': pedido,
        'whatsapp_url': whatsapp_url
    })


@staff_member_required
def dashboard_pastelera(request):
    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)

    pedidos_hoy = Pedido.objects.filter(
        fecha_entrega__date=hoy
    ).exclude(estado='CANCELADO').order_by('fecha_entrega')

    pedidos_pendientes_count = Pedido.objects.filter(estado='PENDIENTE').count()

    facturacion_mes = Pedido.objects.filter(
        fecha_entrega__date__gte=inicio_mes
    ).exclude(estado='CANCELADO').aggregate(total=Sum('total'))['total'] or 0

    insumos_criticos = [
        item for item in Ingrediente.objects.all() if item.esta_bajo_stock()
    ]

    context = {
        'pedidos_hoy': pedidos_hoy,
        'pedidos_hoy_count': pedidos_hoy.count(),
        'pedidos_pendientes_count': pedidos_pendientes_count,
        'facturacion_mes': facturacion_mes,
        'insumos_criticos': insumos_criticos,
    }
    return render(request, 'pedidos/admin_dashboard.html', context)


@staff_member_required
def orden_produccion_pdf(request):
    hoy = timezone.now().date()
    
    pedidos_hoy = Pedido.objects.filter(
        fecha_entrega__date=hoy
    ).exclude(estado='CANCELADO').order_by('fecha_entrega')

    resumen_productos = DetallePedido.objects.filter(
        pedido__fecha_entrega__date=hoy
    ).exclude(pedido__estado='CANCELADO').values('producto__nombre').annotate(
        total_cantidad=Sum('cantidad')
    ).order_by('-total_cantidad')

    context = {
        'fecha': hoy,
        'pedidos': pedidos_hoy,
        'resumen_productos': resumen_productos,
    }
    return render(request, 'pedidos/orden_produccion_print.html', context)