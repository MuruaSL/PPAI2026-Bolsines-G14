"""Carga datos de prueba para poder ejecutar el CU 28.

    python manage.py cargardatos

Deja el escenario del flujo principal listo: un EB logueado en la CM Córdoba y
bolsines en estado Enviado dirigidos a esa CM, con remitos y documentación.
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from recepcion.models import (
    Bolsin,
    CambioEstadoBolsin,
    CambioEstadoDocumentacion,
    ComisionMedica,
    DetalleRemito,
    Documentacion,
    Empleado,
    Estado,
    Localidad,
    Provincia,
    Remito,
    Rol,
    Sesion,
    TipoDocumento,
    Usuario,
)

ESTADOS = [
    (Estado.AMBITO_BOLSIN, ['Creado', 'Cerrado', 'Enviado', 'RecibidoEnCMDestino', 'DeBaja']),
    (Estado.AMBITO_REMITO, ['Creado', 'EnBolsinSaliente', 'EnBolsinEnviado',
                            'RecibidoYAceptado', 'RecibidoYAceptadoParcial']),
    (Estado.AMBITO_DOCUMENTACION, ['Registrada', 'EnRemito', 'EnBolsinSaliente',
                                   'EnBolsinEnviado', 'RecibidaYAceptada', 'NoRecibida',
                                   'RecibidaYRechazada', 'ParaRedirigir', 'DeBaja']),
]


class Command(BaseCommand):
    help = 'Carga datos de prueba para el CU 28 Registrar recepción de bolsín'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Limpiando datos previos...')
        for modelo in (CambioEstadoDocumentacion, CambioEstadoBolsin, DetalleRemito, Remito,
                       Bolsin, Documentacion, TipoDocumento, Sesion, Empleado, Usuario, Rol,
                       ComisionMedica, Localidad, Provincia, Estado):
            modelo.objects.all().delete()

        estados = {}
        for ambito, nombres in ESTADOS:
            for nombre in nombres:
                estados[(ambito, nombre)] = Estado.objects.create(ambito=ambito, nombre=nombre)

        cordoba = Provincia.objects.create(nombre='Córdoba')
        santaFe = Provincia.objects.create(nombre='Santa Fe')
        locCordoba = Localidad.objects.create(nombre='Córdoba', provincia=cordoba)
        locRosario = Localidad.objects.create(nombre='Rosario', provincia=santaFe)

        cmCordoba = ComisionMedica.objects.create(
            codigo='CM-CBA', nombre='Comisión Médica Córdoba',
            email='cba@organismo.gob.ar', localidad=locCordoba,
        )
        cmRosario = ComisionMedica.objects.create(
            codigo='CM-ROS', nombre='Comisión Médica Rosario',
            email='ros@organismo.gob.ar', localidad=locRosario,
        )

        rolEB = Rol.objects.create(nombre='Encargado de Bolsines')
        usuario = Usuario.objects.create(email='eb.cordoba@organismo.gob.ar',
                                         contrasenia='sin-hashear-demo')
        empleado = Empleado.objects.create(
            nombre='Sergio', apellido='Murua', email='eb.cordoba@organismo.gob.ar',
            usuario=usuario, rol=rolEB, asignadoA=cmCordoba,
        )
        sesion = Sesion.objects.create(fechaHoraInicio=timezone.now(), usuario=usuario)

        tipoExpediente = TipoDocumento.objects.create(nombre='Expediente')
        tipoDictamen = TipoDocumento.objects.create(nombre='Dictamen')
        tipoEstudio = TipoDocumento.objects.create(nombre='Estudio médico')

        ahora = timezone.now()
        numeroDoc = 1

        def crearDocumentacion(asunto, tipo):
            nonlocal numeroDoc
            documentacion = Documentacion.objects.create(
                numero=numeroDoc, asunto=asunto, fechaPase=date.today(),
                tipoDocumento=tipo, cmOrigen=cmRosario,
            )
            CambioEstadoDocumentacion.objects.create(
                documentacion=documentacion,
                estado=estados[(Estado.AMBITO_DOCUMENTACION, 'EnBolsinEnviado')],
                fechaHoraInicio=ahora, responsableCE=empleado,
            )
            numeroDoc += 1
            return documentacion

        # Bolsín 1001: dos remitos, tres documentaciones. Enviado a Córdoba.
        bolsin = Bolsin.objects.create(
            numeroBolsin=1001, numeroPrecinto='PRE-88231', fecha=date.today(),
            peso=1450, origen=cmRosario, destino=cmCordoba,
        )
        CambioEstadoBolsin.objects.create(
            bolsin=bolsin, estado=estados[(Estado.AMBITO_BOLSIN, 'Enviado')],
            fechaHoraInicio=ahora, responsableCE=empleado,
        )

        remitoUno = Remito.objects.create(
            numero=501, fecha=date.today(),
            estado=estados[(Estado.AMBITO_REMITO, 'EnBolsinEnviado')],
            origen=cmRosario, destino=cmCordoba, bolsin=bolsin,
        )
        DetalleRemito.objects.create(
            remito=remitoUno, documentacion=crearDocumentacion('Expediente laboral 4471', tipoExpediente))
        DetalleRemito.objects.create(
            remito=remitoUno, documentacion=crearDocumentacion('Dictamen médico 220', tipoDictamen))

        remitoDos = Remito.objects.create(
            numero=502, fecha=date.today(),
            estado=estados[(Estado.AMBITO_REMITO, 'EnBolsinEnviado')],
            origen=cmRosario, destino=cmCordoba, bolsin=bolsin,
        )
        DetalleRemito.objects.create(
            remito=remitoDos, documentacion=crearDocumentacion('Radiografías caso 89', tipoEstudio))

        # Bolsín 1002: un remito. También enviado a Córdoba, para que haya más de uno.
        bolsinDos = Bolsin.objects.create(
            numeroBolsin=1002, numeroPrecinto='PRE-88245', fecha=date.today(),
            peso=820, origen=cmRosario, destino=cmCordoba,
        )
        CambioEstadoBolsin.objects.create(
            bolsin=bolsinDos, estado=estados[(Estado.AMBITO_BOLSIN, 'Enviado')],
            fechaHoraInicio=ahora, responsableCE=empleado,
        )
        remitoTres = Remito.objects.create(
            numero=503, fecha=date.today(),
            estado=estados[(Estado.AMBITO_REMITO, 'EnBolsinEnviado')],
            origen=cmRosario, destino=cmCordoba, bolsin=bolsinDos,
        )
        DetalleRemito.objects.create(
            remito=remitoTres, documentacion=crearDocumentacion('Carta documento 12', tipoExpediente))

        # Bolsín 1003: NO debe aparecer. Destino Rosario, no es la CM del usuario.
        bolsinAjeno = Bolsin.objects.create(
            numeroBolsin=1003, numeroPrecinto='PRE-90001', fecha=date.today(),
            peso=500, origen=cmCordoba, destino=cmRosario,
        )
        CambioEstadoBolsin.objects.create(
            bolsin=bolsinAjeno, estado=estados[(Estado.AMBITO_BOLSIN, 'Enviado')],
            fechaHoraInicio=ahora, responsableCE=empleado,
        )

        # Bolsín 1004: NO debe aparecer. Destino Córdoba pero está Cerrado, no Enviado.
        bolsinCerrado = Bolsin.objects.create(
            numeroBolsin=1004, numeroPrecinto='PRE-90002', fecha=date.today(),
            peso=600, origen=cmRosario, destino=cmCordoba,
        )
        CambioEstadoBolsin.objects.create(
            bolsin=bolsinCerrado, estado=estados[(Estado.AMBITO_BOLSIN, 'Cerrado')],
            fechaHoraInicio=ahora, responsableCE=empleado,
        )

        self.stdout.write(self.style.SUCCESS(
            f'Datos cargados. Sesión id={sesion.id}, EB={empleado}, CM={cmCordoba.nombre}\n'
            f'Bolsines que debe listar el CU: 1001 y 1002.\n'
            f'Bolsines que NO debe listar: 1003 (otro destino), 1004 (no está enviado).'
        ))
