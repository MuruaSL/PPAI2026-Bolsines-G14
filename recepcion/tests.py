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
