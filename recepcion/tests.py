"""Pruebas del CU 28 — Registrar recepción de bolsín.

Verifican el flujo descripto (opción 1: el contenido del bolsín es igual al
registrado) recorriendo la pantalla y el gestor tal como los modela la secuencia.
"""

from django.core.management import call_command
from django.test import TestCase

from .models import Bolsin, Documentacion, Remito, Sesion
from .pantalla import PantallaRegRecepBolsin


class CU28RegistrarRecepcionBolsinTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('cargardatos', verbosity=0)

    def setUp(self):
        self.sesion = Sesion.objects.first()
        self.pantalla = PantallaRegRecepBolsin(self.sesion)

    # -- msg 1 a 23 --------------------------------------------------------

    def test_muestra_la_cm_del_usuario_logueado(self):
        self.pantalla.regRecepBolsin()
        self.assertEqual(self.pantalla.txtbCMUsuario, 'Comisión Médica Córdoba')

    def test_lista_solo_los_bolsines_enviados_a_la_cm_del_usuario(self):
        self.pantalla.regRecepBolsin()

        numeros = sorted(bolsin['numeroBolsin'] for bolsin in self.pantalla.lstBolsines)
        self.assertEqual(numeros, [1001, 1002])
        self.assertTrue(self.pantalla.seleccionHabilitada)

    def test_muestra_cm_origen_y_precinto_de_cada_bolsin(self):
        self.pantalla.regRecepBolsin()

        bolsin = next(b for b in self.pantalla.lstBolsines if b['numeroBolsin'] == 1001)
        self.assertEqual(bolsin['cmOrigen'], 'Comisión Médica Rosario')
        self.assertEqual(bolsin['nroPrecinto'], 'PRE-88231')

    # -- msg 24 a 36 -------------------------------------------------------

    def test_al_seleccionar_bolsin_muestra_remitos_y_documentacion(self):
        self.pantalla.regRecepBolsin()
        bolsin = Bolsin.objects.get(numeroBolsin=1001)

        self.pantalla.tomarSeleccionBolsin(bolsin)

        self.assertEqual(sorted(self.pantalla.lblNroRemito), [501, 502])
        self.assertIn('Expediente laboral 4471', self.pantalla.lblAsuntosDoc)
        self.assertIn('Dictamen médico 220', self.pantalla.lblAsuntosDoc)
        self.assertIn('Radiografías caso 89', self.pantalla.lblAsuntosDoc)
        self.assertIn('Expediente', self.pantalla.lblTiposDoc)

    def test_muestra_las_cuatro_opciones_de_recepcion(self):
        self.pantalla.regRecepBolsin()
        self.pantalla.tomarSeleccionBolsin(Bolsin.objects.get(numeroBolsin=1001))

        self.assertEqual(len(self.pantalla.optsRecBolsin), 4)

    # -- msg 37 a 66: flujo principal --------------------------------------

    def test_flujo_principal_actualiza_bolsin_remitos_y_documentacion(self):
        self.pantalla.regRecepBolsin()
        bolsin = Bolsin.objects.get(numeroBolsin=1001)
        self.pantalla.tomarSeleccionBolsin(bolsin)
        self.pantalla.tomarSeleccionOptRecBolsin(1)

        self.assertTrue(self.pantalla.lblConfirmacion)

        self.pantalla.tomarConfirmacionSeleccionParaRegCorresp(True)

        bolsin.refresh_from_db()
        self.assertEqual(bolsin.getEstadoActual().nombre, 'RecibidoEnCMDestino')

        for numero in (501, 502):
            remito = Remito.objects.get(numero=numero)
            self.assertEqual(remito.estado.nombre, 'RecibidoYAceptado')

        for numero in (1, 2, 3):
            documentacion = Documentacion.objects.get(numero=numero)
            self.assertEqual(documentacion.getEstadoActual().nombre, 'RecibidaYAceptada')

    def test_registra_al_empleado_responsable(self):
        self.pantalla.regRecepBolsin()
        bolsin = Bolsin.objects.get(numeroBolsin=1001)
        self.pantalla.tomarSeleccionBolsin(bolsin)
        self.pantalla.tomarSeleccionOptRecBolsin(1)
        self.pantalla.tomarConfirmacionSeleccionParaRegCorresp(True)

        cambioEstado = bolsin.cambioEstado.get(fechaHoraFin__isnull=True)
        self.assertEqual(cambioEstado.responsableCE.apellido, 'Murua')

        documentacion = Documentacion.objects.get(numero=1)
        cambioDoc = documentacion.cambioEstado.get(fechaHoraFin__isnull=True)
        self.assertEqual(cambioDoc.responsableCE.apellido, 'Murua')

    def test_cierra_el_cambio_de_estado_anterior(self):
        self.pantalla.regRecepBolsin()
        bolsin = Bolsin.objects.get(numeroBolsin=1001)
        self.pantalla.tomarSeleccionBolsin(bolsin)
        self.pantalla.tomarSeleccionOptRecBolsin(1)
        self.pantalla.tomarConfirmacionSeleccionParaRegCorresp(True)

        anterior = bolsin.cambioEstado.get(estado__nombre='Enviado')
        self.assertIsNotNone(anterior.fechaHoraFin)
        self.assertEqual(bolsin.cambioEstado.count(), 2)

    def test_no_afecta_a_los_demas_bolsines(self):
        self.pantalla.regRecepBolsin()
        self.pantalla.tomarSeleccionBolsin(Bolsin.objects.get(numeroBolsin=1001))
        self.pantalla.tomarSeleccionOptRecBolsin(1)
        self.pantalla.tomarConfirmacionSeleccionParaRegCorresp(True)

        otro = Bolsin.objects.get(numeroBolsin=1002)
        self.assertEqual(otro.getEstadoActual().nombre, 'Enviado')

    # -- A6: el EB no confirma ---------------------------------------------

    def test_si_no_confirma_no_registra_nada(self):
        self.pantalla.regRecepBolsin()
        bolsin = Bolsin.objects.get(numeroBolsin=1001)
        self.pantalla.tomarSeleccionBolsin(bolsin)
        self.pantalla.tomarSeleccionOptRecBolsin(1)

        self.pantalla.tomarConfirmacionSeleccionParaRegCorresp(False)

        bolsin.refresh_from_db()
        self.assertEqual(bolsin.getEstadoActual().nombre, 'Enviado')
        self.assertEqual(bolsin.cambioEstado.count(), 1)
        self.assertFalse(self.pantalla.responsableInformado)


class CU28InterfazWebTest(TestCase):
    """Recorre el CU 28 por HTTP, como lo haría el EB en el navegador."""

    @classmethod
    def setUpTestData(cls):
        call_command('cargardatos', verbosity=0)

    def test_pantalla_inicial_muestra_cm_y_bolsines(self):
        respuesta = self.client.get('/')

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Comisión Médica Córdoba')
        self.assertContains(respuesta, '1001')
        self.assertContains(respuesta, 'PRE-88231')
        self.assertContains(respuesta, '1002')
        # 1003 es de otro destino y 1004 no está enviado: no deben listarse.
        self.assertNotContains(respuesta, 'PRE-90001')
        self.assertNotContains(respuesta, 'PRE-90002')

    def test_seleccionar_bolsin_muestra_remitos_y_opciones(self):
        bolsin = Bolsin.objects.get(numeroBolsin=1001)

        respuesta = self.client.post('/seleccionar-bolsin/', {'bolsinId': bolsin.id})

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Remito N° 501')
        self.assertContains(respuesta, 'Remito N° 502')
        self.assertContains(respuesta, 'Expediente laboral 4471')
        self.assertContains(respuesta, 'Radiografías caso 89')
        self.assertContains(respuesta, 'El contenido del bolsín es igual al registrado')

    def test_seleccionar_opcion_pide_confirmacion(self):
        bolsin = Bolsin.objects.get(numeroBolsin=1001)

        respuesta = self.client.post('/seleccionar-opcion/',
                                     {'bolsinId': bolsin.id, 'opcion': 1})

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Confirmar registración')
        self.assertContains(respuesta, 'El contenido del bolsín es igual al registrado')

    def test_confirmar_registra_y_muestra_los_estados(self):
        bolsin = Bolsin.objects.get(numeroBolsin=1001)

        respuesta = self.client.post('/confirmar/', {
            'bolsinId': bolsin.id, 'opcion': 1, 'confirmacion': 'si',
        })

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Recepción registrada')
        self.assertContains(respuesta, 'RecibidoEnCMDestino')
        self.assertContains(respuesta, 'RecibidoYAceptado')
        self.assertContains(respuesta, 'RecibidaYAceptada')
        self.assertContains(respuesta, 'Murua')

        bolsin.refresh_from_db()
        self.assertEqual(bolsin.getEstadoActual().nombre, 'RecibidoEnCMDestino')

    def test_no_confirmar_no_registra(self):
        bolsin = Bolsin.objects.get(numeroBolsin=1001)

        respuesta = self.client.post('/confirmar/', {
            'bolsinId': bolsin.id, 'opcion': 1, 'confirmacion': 'no',
        })

        self.assertContains(respuesta, 'No se confirmó la registración')
        bolsin.refresh_from_db()
        self.assertEqual(bolsin.getEstadoActual().nombre, 'Enviado')

    def test_recorrido_completo_paso_a_paso(self):
        """El recorrido entero, como en la defensa."""
        bolsin = Bolsin.objects.get(numeroBolsin=1002)

        self.assertContains(self.client.get('/'), '1002')
        self.assertContains(
            self.client.post('/seleccionar-bolsin/', {'bolsinId': bolsin.id}),
            'Remito N° 503')
        self.assertContains(
            self.client.post('/seleccionar-opcion/', {'bolsinId': bolsin.id, 'opcion': 1}),
            'Confirmar registración')
        self.assertContains(
            self.client.post('/confirmar/',
                             {'bolsinId': bolsin.id, 'opcion': 1, 'confirmacion': 'si'}),
            'Recepción registrada')

        bolsin.refresh_from_db()
        self.assertEqual(bolsin.getEstadoActual().nombre, 'RecibidoEnCMDestino')
        self.assertEqual(Remito.objects.get(numero=503).estado.nombre, 'RecibidoYAceptado')


class HistorialTest(TestCase):
    """Pantalla auxiliar de historial. No es parte del CU 28."""

    @classmethod
    def setUpTestData(cls):
        call_command('cargardatos', verbosity=0)

    def test_sin_recepciones_avisa_que_esta_vacio(self):
        respuesta = self.client.get('/historial/')

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Todavía no se registró la recepción')

    def test_muestra_el_bolsin_recibido_con_su_trazabilidad(self):
        bolsin = Bolsin.objects.get(numeroBolsin=1001)
        self.client.post('/confirmar/',
                         {'bolsinId': bolsin.id, 'opcion': 1, 'confirmacion': 'si'})

        respuesta = self.client.get('/historial/')

        self.assertContains(respuesta, '1001')
        self.assertContains(respuesta, 'PRE-88231')
        self.assertContains(respuesta, 'RecibidoEnCMDestino')
        self.assertContains(respuesta, 'Remito N° 501')
        self.assertContains(respuesta, 'RecibidoYAceptado')
        self.assertContains(respuesta, 'Expediente laboral 4471')
        self.assertContains(respuesta, 'RecibidaYAceptada')
        self.assertContains(respuesta, 'Murua')

    def test_no_muestra_bolsines_que_siguen_enviados(self):
        bolsin = Bolsin.objects.get(numeroBolsin=1001)
        self.client.post('/confirmar/',
                         {'bolsinId': bolsin.id, 'opcion': 1, 'confirmacion': 'si'})

        respuesta = self.client.get('/historial/')

        # 1002 sigue en Enviado, no debe aparecer en el historial.
        self.assertNotContains(respuesta, 'PRE-88245')

    def test_no_muestra_bolsines_de_otra_cm(self):
        respuesta = self.client.get('/historial/')

        self.assertNotContains(respuesta, 'PRE-90001')
