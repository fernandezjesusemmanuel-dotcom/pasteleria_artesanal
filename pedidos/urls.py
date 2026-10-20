from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('pedido/<int:producto_id>/', views.realizar_pedido, name='realizar_pedido'),
    path('pedido/confirmacion/<int:pedido_id>/', views.confirmacion_pedido, name='confirmacion_pedido'),
    path('panel-cocina/', views.dashboard_pastelera, name='dashboard_pastelera'),
    path('panel-cocina/hoja-imprimible/', views.orden_produccion_pdf, name='orden_produccion_pdf'),
]