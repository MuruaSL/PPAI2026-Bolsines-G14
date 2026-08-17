"""Vistas del CU 28 — Registrar recepción de bolsín.

La clase boundary del modelo es `PantallaRegRecepBolsin`. Estas vistas son la mitad
web de ese boundary: reciben el request, le pasan el mensaje a la pantalla y
renderizan lo que la pantalla acumuló.

Sobre el estado entre pasos: HTTP no tiene memoria, pero el caso de uso sí. En cada
request se reconstruye la pantalla y el gestor desde cero (`regRecepBolsin()`) y se
reaplica lo que el EB ya había elegido, que viaja en campos ocultos del formulario.
Así el recorrido de mensajes es siempre el del diagrama, sin estado escondido.
"""

from django.shortcuts import redirect, render

from .models import Bolsin, Sesion
from .pantalla import PantallaRegRecepBolsin


def _abrirPantalla():
    """Crea la pantalla y ejecuta la apertura del CU (msg 1 a 23)."""
    sesion = Sesion.objects.order_by('-fechaHoraInicio').first()
    if sesion is None:
        return None
    pantalla = PantallaRegRecepBolsin(sesion)
    pantalla.regRecepBolsin()  # msg 1
    return pantalla


def _contexto(pantalla, **extra):
    contexto = {
        'cmUsuario': pantalla.txtbCMUsuario,
        'bolsines': pantalla.lstBolsines,
        'seleccionHabilitada': pantalla.seleccionHabilitada,
        'datosRemitos': pantalla.datosRemitos,
        'opciones': pantalla.optsRecBolsin,
        'pideConfirmacion': pantalla.lblConfirmacion,
    }
    contexto.update(extra)
    return contexto


def registrarRecepcion(request):
    """Paso 1 — muestra la CM del usuario y los bolsines en estado Enviado."""
    pantalla = _abrirPantalla()
    if pantalla is None:
        return render(request, 'recepcion/sin_datos.html')

    if not pantalla.lstBolsines:
        # A1/A2: no hay bolsines enviados para la CM del usuario.
        return render(request, 'recepcion/pantalla.html',
                      _contexto(pantalla, sinBolsines=True))

    return render(request, 'recepcion/pantalla.html', _contexto(pantalla))


def seleccionarBolsin(request):
    """Paso 2 — msg 24: el EB selecciona un bolsín y se muestran sus remitos."""
    if request.method != 'POST':
        return redirect('registrarRecepcion')

    pantalla = _abrirPantalla()
    bolsin = Bolsin.objects.get(id=request.POST['bolsinId'])
    pantalla.tomarSeleccionBolsin(bolsin)  # msg 24

    return render(request, 'recepcion/pantalla.html',
                  _contexto(pantalla, bolsinSeleccionado=bolsin))


def seleccionarOpcion(request):
    """Paso 3 — msg 37: el EB elige la opción de recepción y se pide confirmación."""
    if request.method != 'POST':
        return redirect('registrarRecepcion')

    pantalla = _abrirPantalla()
    bolsin = Bolsin.objects.get(id=request.POST['bolsinId'])
    opcion = int(request.POST['opcion'])

    pantalla.tomarSeleccionBolsin(bolsin)  # msg 24
    pantalla.tomarSeleccionOptRecBolsin(opcion)  # msg 37

    etiquetaOpcion = dict(pantalla.optsRecBolsin).get(opcion, '')

    return render(request, 'recepcion/pantalla.html',
                  _contexto(pantalla, bolsinSeleccionado=bolsin,
                            opcionSeleccionada=opcion, etiquetaOpcion=etiquetaOpcion))


def confirmar(request):
    """Paso 4 — msg 41: el EB confirma y se registra la recepción."""
    if request.method != 'POST':
        return redirect('registrarRecepcion')

    pantalla = _abrirPantalla()
    bolsin = Bolsin.objects.get(id=request.POST['bolsinId'])
    opcion = int(request.POST['opcion'])
    confirmacion = request.POST.get('confirmacion') == 'si'

    pantalla.tomarSeleccionBolsin(bolsin)  # msg 24
    pantalla.tomarSeleccionOptRecBolsin(opcion)  # msg 37
    pantalla.tomarConfirmacionSeleccionParaRegCorresp(confirmacion)  # msg 41

    if not confirmacion:
        # A6: el EB no confirma. No se registra nada.
        return render(request, 'recepcion/resultado.html',
                      {'confirmado': False, 'bolsin': bolsin})

    bolsin.refresh_from_db()
    return render(request, 'recepcion/resultado.html', {
        'confirmado': True,
        'bolsin': bolsin,
        'estadoBolsin': bolsin.getEstadoActual(),
        'remitos': bolsin.remito.all(),
        'responsable': pantalla.gestor.empleadoLogueado,
        'informado': pantalla.responsableInformado,
    })


# ---------------------------------------------------------------------------
# Consulta auxiliar — FUERA DEL ALCANCE DEL CU 28
# ---------------------------------------------------------------------------
#
# Esta vista no forma parte del caso de uso asignado ni está modelada en los
# diagramas de la Entrega 1. Es una ayuda de consulta que hace visible la regla
# de negocio "Trazabilidad de la documentación y del Bolsín" del ERS: en qué
# estado quedó cada bolsín recibido, cuándo y qué empleado fue responsable.
#
# Deliberadamente NO tiene gestor ni clase boundary: inventarlos sería agregar
# modelado que la cátedra no validó. Consulta las entidades y muestra el
# resultado, nada más.


def historial(request):
    """Bolsines ya recibidos en la CM del usuario, con su trazabilidad."""
    sesion = Sesion.objects.order_by('-fechaHoraInicio').first()
    if sesion is None:
        return render(request, 'recepcion/sin_datos.html')

    empleado = sesion.getUsuarioEnSesion().empleados.first()
    comisionMedica = empleado.asignadoA if empleado else None

    recibidos = []
    for bolsin in Bolsin.objects.filter(destino=comisionMedica).order_by('-numeroBolsin'):
        estadoActual = bolsin.getEstadoActual()
        if estadoActual is None or estadoActual.nombre != 'RecibidoEnCMDestino':
            continue

        cambioEstado = bolsin.cambioEstado.filter(fechaHoraFin__isnull=True).first()

        remitos = []
        for remito in bolsin.remito.all():
            documentaciones = []
            for detalle in remito.detalleRemito.all():
                documentacion = detalle.getDocumentacion()
                documentaciones.append({
                    'asunto': documentacion.getAsunto(),
                    'tipo': documentacion.getTipoDocumentacion().getNombre(),
                    'estado': documentacion.getEstadoActual(),
                })
            remitos.append({
                'numero': remito.getNumero(),
                'estado': remito.estado,
                'documentaciones': documentaciones,
            })

        recibidos.append({
            'bolsin': bolsin,
            'estado': estadoActual,
            'fechaHora': cambioEstado.fechaHoraInicio if cambioEstado else None,
            'responsable': cambioEstado.responsableCE if cambioEstado else None,
            'remitos': remitos,
        })

    return render(request, 'recepcion/historial.html', {
        'cmUsuario': comisionMedica.getNombre() if comisionMedica else '',
        'recibidos': recibidos,
    })
