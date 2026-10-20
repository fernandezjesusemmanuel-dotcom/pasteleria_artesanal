from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import ConfiguracionProduccion, Pedido


class PedidoForm(forms.ModelForm):
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.HiddenInput()  # Se gestiona dinámicamente con los botones + y -
    )

    class Meta:
        model = Pedido
        fields = [
            'cliente_nombre',
            'cliente_telefono',
            'cliente_email',
            'fecha_entrega',
            'notas',
            'comprobante_sena',
        ]
        widgets = {
            'cliente_nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-amber-500 bg-stone-50 text-sm',
                'placeholder': 'Ej. Mariana Rodríguez'
            }),
            'cliente_telefono': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-amber-500 bg-stone-50 text-sm',
                'placeholder': 'Ej. 261 555-1234'
            }),
            'cliente_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-amber-500 bg-stone-50 text-sm',
                'placeholder': 'mariana@ejemplo.com'
            }),
            'fecha_entrega': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-amber-500 bg-stone-50 text-sm'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 rounded-xl border border-stone-200 focus:outline-none focus:ring-2 focus:ring-amber-500 bg-stone-50 text-sm',
                'rows': 2,
                'placeholder': '¿Algún mensaje en chocolate o aclaración especial?'
            }),
            'comprobante_sena': forms.FileInput(attrs={
                'class': 'w-full text-xs text-stone-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-amber-100 file:text-amber-800 hover:file:bg-amber-200 cursor-pointer'
            })
        }

    def clean_fecha_entrega(self):
        fecha_entrega = self.cleaned_data.get('fecha_entrega')
        if not fecha_entrega:
            return fecha_entrega

        # 1. No permitir fechas pasadas
        if fecha_entrega < timezone.now():
            raise ValidationError("La fecha de entrega debe ser posterior al momento actual.")

        # 2. Control de cupo diario de producción
        config = ConfiguracionProduccion.objects.first()
        limite_diario = config.limite_pedidos_diarios if config else 5

        dia_inicio = fecha_entrega.replace(hour=0, minute=0, second=0, microsecond=0)
        dia_fin = fecha_entrega.replace(hour=23, minute=59, second=59, microsecond=999999)

        pedidos_del_dia = Pedido.objects.filter(
            fecha_entrega__range=(dia_inicio, dia_fin)
        ).exclude(estado='CANCELADO').count()

        if pedidos_del_dia >= limite_diario:
            raise ValidationError(
                f"La cocina alcanzó su capacidad máxima ({limite_diario} pedidos) para el {fecha_entrega.strftime('%d/%m/%Y')}. Por favor selecciona otra fecha."
            )

        return fecha_entrega