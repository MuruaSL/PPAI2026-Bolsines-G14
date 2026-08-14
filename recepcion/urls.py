from django.urls import path

from . import views

urlpatterns = [
    path('', views.registrarRecepcion, name='registrarRecepcion'),
    path('seleccionar-bolsin/', views.seleccionarBolsin, name='seleccionarBolsin'),
    path('seleccionar-opcion/', views.seleccionarOpcion, name='seleccionarOpcion'),
    path('confirmar/', views.confirmar, name='confirmar'),
]
