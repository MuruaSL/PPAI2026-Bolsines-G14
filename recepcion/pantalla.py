"""PantallaRegRecepBolsin — clase boundary del CU 28.

Calco del diagrama de clases y del diagrama de secuencia de la Entrega 1.

En una aplicación web el boundary queda partido en dos mitades: esta clase, que es
la del modelo, y las vistas + templates que la renderizan (views.py). La pantalla
acumula lo que el gestor le pide mostrar; la vista lo lleva al navegador.

Así el calco se sostiene: los mensajes 10, 22, 23, 34, 36, 40 y 65 llegan a esta
clase con el nombre exacto del diagrama, y la tecnología web queda por detrás.
"""

from .gestor import GestorRegRecepBolsin


class PantallaRegRecepBolsin:

    def __init__(self, sesion):
        self.sesion = sesion
        self.gestor = None

        self.lblCMUsuario = None
        self.txtbCMUsuario = None
        self.lstBolsines = []
        self.lstPrecintos = []
        self.seleccionHabilitada = False
        self.lblNroRemito = []
        self.lblAsuntosDoc = []
        self.lblTiposDoc = []
        self.datosRemitos = []
        self.optsRecBolsin = []
        self.lblConfirmacion = False
        self.responsableInformado = False

    # -- msg 1 a 3 ---------------------------------------------------------

    def regRecepBolsin(self):
        """msg 1 — el EB selecciona la opción de registrar la recepción de un bolsín."""
        self.habilitarPantalla()  # msg 2

    def habilitarPantalla(self):
        """msg 2."""
        self.gestor = GestorRegRecepBolsin(self, self.sesion)  # msg 3 «create»
        self.gestor.optRegRecepBolsin()  # msg 3

    # -- msg 10 ------------------------------------------------------------

    def mostrarCM(self, nombreCM):
        """msg 10."""
        self.txtbCMUsuario = nombreCM

    # -- msg 22 a 25 -------------------------------------------------------

    def mostrarDatosBolsin(self, datosBolsines):
        """msg 22."""
        self.lstBolsines = datosBolsines
        self.lstPrecintos = [bolsin['nroPrecinto'] for bolsin in datosBolsines]

    def habilitarSeleccionBolsin(self):
        """msg 23."""
        self.seleccionHabilitada = True

    def tomarSeleccionBolsin(self, bolsin):
        """msg 24 — el EB selecciona un bolsín del listado."""
        self.gestor.tomarSeleccionBolsin(bolsin)  # msg 25

    # -- msg 34 ------------------------------------------------------------

    def mostrarDatosRemitoYDocAsociada(self, datosRemitos):
        """msg 34."""
        self.datosRemitos = datosRemitos
        self.lblNroRemito = [remito['numero'] for remito in datosRemitos]
        self.lblAsuntosDoc = []
        self.lblTiposDoc = []
        for remito in datosRemitos:
            for documentacion in remito['documentacion']:
                self.lblAsuntosDoc.append(documentacion['asunto'])
                self.lblTiposDoc.append(documentacion['tipo'])

    # -- msg 36 a 38 -------------------------------------------------------

    def mostrarOptsRecBolsin(self, opciones):
        """msg 36."""
        self.optsRecBolsin = opciones

    def tomarSeleccionOptRecBolsin(self, opcion):
        """msg 37 — el EB selecciona la opción de recepción."""
        self.gestor.tomarSeleccionOptRecBolsin(opcion)  # msg 38

    # -- msg 40 a 42 -------------------------------------------------------

    def pedirConfirmacionSeleccionParaRegCorresp(self):
        """msg 40."""
        self.lblConfirmacion = True

    def tomarConfirmacionSeleccionParaRegCorresp(self, confirmacion):
        """msg 41 — el EB confirma la selección."""
        return self.gestor.tomarConfirmacionSeleccionParaRegCorresp(confirmacion)  # msg 42

    # -- msg 65 ------------------------------------------------------------

    def informarResponsable(self):
        """msg 65 — informa la ejecución exitosa del caso de uso."""
        self.responsableInformado = True
