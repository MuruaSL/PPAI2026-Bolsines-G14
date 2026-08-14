"""GestorRegRecepBolsin — clase control del CU 28.

Calco del diagrama de clases y del diagrama de secuencia de la Entrega 1.
Los `msg N` de los docstrings refieren a docs/cu28-contrato-secuencia.md

Es una clase Python plana, no un modelo Django: el gestor no se persiste, coordina.
"""

from django.utils import timezone

from .models import Bolsin, Empleado, Estado


class GestorRegRecepBolsin:
    """Control del caso de uso. Un gestor por ejecución del CU."""

    # Opciones de recepción que se le ofrecen al EB (msg 36).
    OPT_CONTENIDO_IGUAL = 1
    OPT_FALTA_DOCUMENTACION = 2
    OPT_NO_CORRESPONDE_DESTINO = 3
    OPT_REDIRIGIR_A_OTRA_AREA = 4

    OPCIONES_RECEPCION = [
        (OPT_CONTENIDO_IGUAL, 'El contenido del bolsín es igual al registrado'),
        (OPT_FALTA_DOCUMENTACION,
         'No se recibe toda la documentación asociada a los remitos que contiene el bolsín'),
        (OPT_NO_CORRESPONDE_DESTINO, 'Existe documentación que no corresponde al destino'),
        (OPT_REDIRIGIR_A_OTRA_AREA, 'La documentación se debe redirigir a otra área'),
    ]

    def __init__(self, pantalla, sesion):
        self.pantalla = pantalla
        self.sesion = sesion

        self.empleadoLogueado = None
        self.cmUsuario = None
        self.lstBolsinesEnviados = []
        self.lstCMOrigen = []
        self.lstNrosPrecintos = []
        self.seleccionBolsin = None
        self.lstDocumentacion = []
        self.nrosRemitos = []
        self.asuntosDocumentacion = []
        self.tiposDocumentacion = []
        self.optsRecBolsin = []
        self.selecOptRegRecBolsin = None
        self.confirmacion = None
        self.estadoRecibidoEnCMDestino = None
        self.estadoRecibidoYAceptado = None
        self.estadoRecibidaYAceptada = None
        self.fechaHoraActual = None

    # -- msg 3 -------------------------------------------------------------

    def optRegRecepBolsin(self):
        """msg 3 — arranque del caso de uso."""
        self.buscarCmyMostrarlo()  # msg 4

    # -- msg 4 a 10 --------------------------------------------------------

    def buscarCmyMostrarlo(self):
        """msg 4 — identifica al empleado logueado y muestra su CM."""
        usuario = self.sesion.getUsuarioEnSesion()  # msg 5

        for empleado in Empleado.objects.all():
            if empleado.esTuUsuario(usuario):  # msg 6
                self.empleadoLogueado = empleado

        self.getCM()  # msg 7
        self.pantalla.mostrarCM(self.cmUsuario.getNombre())  # msg 10

        self.buscarBolsinesEnviados()  # msg 11

    def getCM(self):
        """msg 7."""
        self.cmUsuario = self.empleadoLogueado.getCM()  # msg 8 (dispara msg 9)
        return self.cmUsuario

    # -- msg 11 a 16 -------------------------------------------------------

    def buscarBolsinesEnviados(self):
        """msg 11 — se le pregunta a cada bolsín si le corresponde al usuario.

        Se recorren todos los bolsines preguntándoles, en vez de filtrar por consulta:
        así lo modela el diagrama, aplicando Experto.
        """
        self.lstBolsinesEnviados = []

        for bolsin in Bolsin.objects.all():
            if bolsin.esTuCMDestino(self.cmUsuario):  # msg 12
                if bolsin.sosEnviado():  # msg 13 (dispara msg 14, 15, 16)
                    self.lstBolsinesEnviados.append(bolsin)

        self.obtenerCMOrigenYnroPrecinto()  # msg 17

    # -- msg 17 a 20 -------------------------------------------------------

    def obtenerCMOrigenYnroPrecinto(self):
        """msg 17 — arma los datos con los que se listan los bolsines."""
        self.lstCMOrigen = []
        self.lstNrosPrecintos = []

        for bolsin in self.lstBolsinesEnviados:
            cmOrigen = bolsin.getCMOrigen()  # msg 18 (dispara msg 19)
            self.lstCMOrigen.append(cmOrigen.getNombre())
            self.lstNrosPrecintos.append(bolsin.getNroPrecinto())  # msg 20

        self.mostrarYPedirSeleccionBolsin()  # msg 21

    # -- msg 21 a 23 -------------------------------------------------------

    def mostrarYPedirSeleccionBolsin(self):
        """msg 21."""
        datosBolsines = []
        for indice, bolsin in enumerate(self.lstBolsinesEnviados):
            datosBolsines.append(
                {
                    'id': bolsin.id,
                    'numeroBolsin': bolsin.numeroBolsin,
                    'cmOrigen': self.lstCMOrigen[indice],
                    'nroPrecinto': self.lstNrosPrecintos[indice],
                }
            )

        self.pantalla.mostrarDatosBolsin(datosBolsines)  # msg 22
        self.pantalla.habilitarSeleccionBolsin()  # msg 23

    # -- msg 25 ------------------------------------------------------------

    def tomarSeleccionBolsin(self, bolsin):
        """msg 25 — recibe el bolsín que eligió el EB."""
        self.seleccionBolsin = bolsin
        self.mostrarDatosRemitoYDocAsociada()  # msg 26

    # -- msg 26 a 34 -------------------------------------------------------

    def mostrarDatosRemitoYDocAsociada(self):
        """msg 26."""
        self.lstDocumentacion = self.seleccionBolsin.obtenerRemito()  # msg 27

        self.nrosRemitos = []
        self.asuntosDocumentacion = []
        self.tiposDocumentacion = []
        for remito in self.lstDocumentacion:
            self.nrosRemitos.append(remito['numero'])
            for documentacion in remito['documentacion']:
                self.asuntosDocumentacion.append(documentacion['asunto'])
                self.tiposDocumentacion.append(documentacion['tipo'])

        self.pantalla.mostrarDatosRemitoYDocAsociada(self.lstDocumentacion)  # msg 34
        self.pedirSelecOptRecBolsin()  # msg 35

    # -- msg 35 a 36 -------------------------------------------------------

    def pedirSelecOptRecBolsin(self):
        """msg 35."""
        self.optsRecBolsin = self.OPCIONES_RECEPCION
        self.pantalla.mostrarOptsRecBolsin(self.optsRecBolsin)  # msg 36

    # -- msg 38 a 40 -------------------------------------------------------

    def tomarSeleccionOptRecBolsin(self, opcion):
        """msg 38 — recibe la opción de recepción elegida."""
        self.selecOptRegRecBolsin = opcion
        self.pedirConfirmacionSeleccionParaRegCorresp()  # msg 39

    def pedirConfirmacionSeleccionParaRegCorresp(self):
        """msg 39."""
        self.pantalla.pedirConfirmacionSeleccionParaRegCorresp()  # msg 40

    # -- msg 42 ------------------------------------------------------------

    def tomarConfirmacionSeleccionParaRegCorresp(self, confirmacion):
        """msg 42 — el EB confirma o no.

        A6: si no confirma, el CU no registra nada.
        """
        self.confirmacion = confirmacion

        if not self.confirmacion:
            return self.finCU()  # msg 66

        self.buscarEstados()  # msg 43
        self.getFechaHoraActual()  # msg 50
        self.regRecepcionBolsin()  # msg 51
        self.notificarCM()  # msg 63
        self.pantalla.informarResponsable()  # msg 65
        return self.finCU()  # msg 66

    # -- msg 43 a 49 -------------------------------------------------------

    def buscarEstados(self):
        """msg 43 — busca los tres estados a asignar, uno por ámbito."""
        for estado in Estado.objects.all():
            if estado.sosAmbitoBolsin():  # msg 44
                if estado.sosRecibidoEnCMDestino():  # msg 45
                    self.estadoRecibidoEnCMDestino = estado

        for estado in Estado.objects.all():
            if estado.sosAmbitoRemito():  # msg 46
                if estado.sosRecibidoYAceptado():  # msg 47
                    self.estadoRecibidoYAceptado = estado

        for estado in Estado.objects.all():
            if estado.sosAmbitoDocumentacion():  # msg 48
                if estado.sosRecibidaYAceptada():  # msg 49
                    self.estadoRecibidaYAceptada = estado

    # -- msg 50 a 51 -------------------------------------------------------

    def getFechaHoraActual(self):
        """msg 50."""
        self.fechaHoraActual = timezone.now()
        return self.fechaHoraActual

    def regRecepcionBolsin(self):
        """msg 51 — dispara la registración en cascada."""
        self.seleccionBolsin.recibir(  # msg 52
            self.estadoRecibidoEnCMDestino,
            self.estadoRecibidoYAceptado,
            self.estadoRecibidaYAceptada,
            self.fechaHoraActual,
            self.empleadoLogueado,
        )

    # -- msg 63 a 66 -------------------------------------------------------

    def notificarCM(self):
        """msg 63 — incluye al CU 29 Notificar recepción de bolsín (msg 64).

        El envío real de mail corresponde al CU 29, fuera del alcance del CU 28.
        """
        pass  # msg 64 «include» CU 29

    def finCU(self):
        """msg 66."""
        return True
