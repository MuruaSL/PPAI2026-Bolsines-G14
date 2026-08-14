"""Entidades del CU 28 — Registrar recepción de bolsín.

Calco del diagrama de clases de análisis de la Entrega 1.

Los nombres de métodos están en camelCase, no en snake_case, porque deben coincidir
exactamente con los del diagrama. Es deliberado: la cátedra corrige la consistencia
entre el modelado y el código. No renombrar.

Las referencias `msg N` en los docstrings apuntan al número de mensaje del diagrama
de secuencia, transcrito en docs/cu28-contrato-secuencia.md
"""

from django.db import models


# ---------------------------------------------------------------------------
# Ubicación y organización
# ---------------------------------------------------------------------------


class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.nombre


class Localidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200, blank=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre


class ComisionMedica(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT, null=True, blank=True)

    def getNombre(self):
        """msg 9, 19."""
        return self.nombre

    def __str__(self):
        return self.nombre


class Rol(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200, blank=True)

    def esGCM(self):
        return self.nombre == 'Gerente de Comision Medica'

    def __str__(self):
        return self.nombre


# ---------------------------------------------------------------------------
# Usuario, empleado y sesión
# ---------------------------------------------------------------------------


class Usuario(models.Model):
    email = models.EmailField()
    contrasenia = models.CharField(max_length=128)

    def __str__(self):
        return self.email


class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='empleados')
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True, blank=True)
    asignadoA = models.ForeignKey(ComisionMedica, on_delete=models.PROTECT, related_name='empleados')

    def esTuUsuario(self, usuario):
        """msg 6 — se pregunta a cada empleado si le corresponde el usuario en sesión."""
        return self.usuario_id == usuario.id

    def getCM(self):
        """msg 8 — devuelve la CM a la que está asignado el empleado.

        El diagrama muestra que este método dispara `getNombre()` sobre la CM (msg 9),
        por eso la invocación queda acá y no en el gestor.
        """
        self.asignadoA.getNombre()  # msg 9
        return self.asignadoA

    def __str__(self):
        return f'{self.apellido}, {self.nombre}'


class Sesion(models.Model):
    fechaHoraInicio = models.DateTimeField()
    fechaHoraFin = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='sesiones')

    def getUsuarioEnSesion(self):
        """msg 5."""
        return self.usuario

    def __str__(self):
        return f'Sesión {self.id} — {self.usuario}'


# ---------------------------------------------------------------------------
# Estados
# ---------------------------------------------------------------------------


class Estado(models.Model):
    """Estado con ámbito. El ámbito distingue a qué clase aplica el estado."""

    AMBITO_BOLSIN = 'Bolsin'
    AMBITO_REMITO = 'Remito'
    AMBITO_DOCUMENTACION = 'Documentacion'

    nombre = models.CharField(max_length=60)
    ambito = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, blank=True)

    # --- ámbito ---

    def sosAmbitoBolsin(self):
        """msg 44."""
        return self.ambito == self.AMBITO_BOLSIN

    def sosAmbitoRemito(self):
        """msg 46."""
        return self.ambito == self.AMBITO_REMITO

    def sosAmbitoDocumentacion(self):
        """msg 48."""
        return self.ambito == self.AMBITO_DOCUMENTACION

    def getAmbito(self):
        return self.ambito

    # --- nombre concreto ---

    def sosEnviado(self):
        """msg 16."""
        return self.nombre == 'Enviado'

    def sosRecibidoEnCMDestino(self):
        """msg 45."""
        return self.nombre == 'RecibidoEnCMDestino'

    def sosRecibidoYAceptado(self):
        """msg 47."""
        return self.nombre == 'RecibidoYAceptado'

    def sosRecibidaYAceptada(self):
        """msg 49."""
        return self.nombre == 'RecibidaYAceptada'

    def getNombre(self):
        return self.nombre

    def getDescripcion(self):
        return self.descripcion

    def __str__(self):
        return f'{self.ambito}/{self.nombre}'


# ---------------------------------------------------------------------------
# Documentación
# ---------------------------------------------------------------------------


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200, blank=True)

    def getNombre(self):
        """msg 33."""
        return self.nombre

    def getDescripcion(self):
        return self.descripcion

    def __str__(self):
        return self.nombre


class Documentacion(models.Model):
    numero = models.IntegerField(unique=True)
    asunto = models.CharField(max_length=250)
    fechaPase = models.DateField()
    tipoDocumento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT)
    cmOrigen = models.ForeignKey(ComisionMedica, on_delete=models.PROTECT, related_name='documentaciones')

    def getAsunto(self):
        """msg 31."""
        return self.asunto

    def getTipoDocumentacion(self):
        """msg 32."""
        return self.tipoDocumento

    def aceptar(self, estado, fechaHora, responsable):
        """msg 58 — cierra el cambio de estado actual y crea el nuevo."""
        actual = None
        for cambioEstado in self.cambioEstado.all():
            if cambioEstado.sosActual():  # msg 59
                actual = cambioEstado
        if actual is not None:
            actual.setFechaHoraFin(fechaHora)  # msg 60
        return self.crearNuevoCE(estado, fechaHora, responsable)  # msg 61

    def crearNuevoCE(self, estado, fechaHora, responsable):
        """msg 61 — crea el nuevo CambioEstadoDocumentacion (msg 62)."""
        return CambioEstadoDocumentacion.objects.create(  # msg 62 «create»
            documentacion=self,
            estado=estado,
            fechaHoraInicio=fechaHora,
            responsableCE=responsable,
        )

    def getEstadoActual(self):
        for cambioEstado in self.cambioEstado.all():
            if cambioEstado.sosActual():
                return cambioEstado.estado
        return None

    def __str__(self):
        return f'Doc {self.numero} — {self.asunto}'


class Archivo(models.Model):
    nombreArchivo = models.CharField(max_length=200)
    tituloDocumento = models.CharField(max_length=200, blank=True)
    documentacion = models.ForeignKey(
        Documentacion, on_delete=models.CASCADE, related_name='archivoAdjunto'
    )

    def __str__(self):
        return self.nombreArchivo


class CambioEstadoDocumentacion(models.Model):
    fechaHoraInicio = models.DateTimeField()
    fechaHoraFin = models.DateTimeField(null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    documentacion = models.ForeignKey(
        Documentacion, on_delete=models.CASCADE, related_name='cambioEstado'
    )
    responsableCE = models.ForeignKey(
        Empleado, on_delete=models.PROTECT, null=True, blank=True
    )

    def sosActual(self):
        """msg 59 — es el cambio de estado vigente si no tiene fecha de fin."""
        return self.fechaHoraFin is None

    def setFechaHoraFin(self, fechaHora):
        """msg 60."""
        self.fechaHoraFin = fechaHora
        self.save()

    def __str__(self):
        return f'{self.documentacion} → {self.estado}'


# ---------------------------------------------------------------------------
# Remito
# ---------------------------------------------------------------------------


class Remito(models.Model):
    numero = models.IntegerField(unique=True)
    fecha = models.DateField()
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    origen = models.ForeignKey(
        ComisionMedica, on_delete=models.PROTECT, related_name='remitosOrigen'
    )
    destino = models.ForeignKey(
        ComisionMedica, on_delete=models.PROTECT, related_name='remitosDestino'
    )
    bolsin = models.ForeignKey(
        'Bolsin', on_delete=models.SET_NULL, null=True, blank=True, related_name='remito'
    )

    def getNumero(self):
        """msg 28."""
        return self.numero

    def buscarDocumentacion(self):
        """msg 29 — recorre los detalles y arma los datos de la documentación."""
        datos = []
        for detalleRemito in self.detalleRemito.all():
            documentacion = detalleRemito.getDocumentacion()  # msg 30
            datos.append(
                {
                    'asunto': documentacion.getAsunto(),  # msg 31
                    'tipo': documentacion.getTipoDocumentacion().getNombre(),  # msg 32, 33
                }
            )
        return datos

    def aceptar(self, estadoRemito, estadoDocumentacion, fechaHora, responsable):
        """msg 56 — el remito toma su estado y propaga a sus detalles."""
        self.estado = estadoRemito
        self.save()
        for detalleRemito in self.detalleRemito.all():
            detalleRemito.aceptar(estadoDocumentacion, fechaHora, responsable)  # msg 57

    def __str__(self):
        return f'Remito {self.numero}'


class DetalleRemito(models.Model):
    areaCMCDestino = models.CharField(max_length=150, blank=True)
    remito = models.ForeignKey(Remito, on_delete=models.CASCADE, related_name='detalleRemito')
    documentacion = models.ForeignKey(Documentacion, on_delete=models.PROTECT)

    def getDocumentacion(self):
        """msg 30."""
        return self.documentacion

    def aceptar(self, estado, fechaHora, responsable):
        """msg 57."""
        return self.documentacion.aceptar(estado, fechaHora, responsable)  # msg 58

    def __str__(self):
        return f'Detalle de {self.remito} — {self.documentacion}'


# ---------------------------------------------------------------------------
# Bolsín
# ---------------------------------------------------------------------------


class Bolsin(models.Model):
    numeroBolsin = models.IntegerField(unique=True)
    numeroPrecinto = models.CharField(max_length=50, blank=True)
    fecha = models.DateField()
    peso = models.IntegerField(help_text='Peso en gramos')
    origen = models.ForeignKey(
        ComisionMedica, on_delete=models.PROTECT, related_name='bolsinesOrigen'
    )
    destino = models.ForeignKey(
        ComisionMedica, on_delete=models.PROTECT, related_name='bolsinesDestino'
    )

    def esTuCMDestino(self, comisionMedica):
        """msg 12."""
        return self.destino_id == comisionMedica.id

    def sosEnviado(self):
        """msg 13 — pregunta a sus cambios de estado cuál es el actual y si es Enviado."""
        for cambioEstado in self.cambioEstado.all():
            if cambioEstado.sosActual():  # msg 14
                return cambioEstado.sosEnviado()  # msg 15
        return False

    def getCMOrigen(self):
        """msg 18."""
        self.origen.getNombre()  # msg 19
        return self.origen

    def getNroPrecinto(self):
        """msg 20."""
        return self.numeroPrecinto

    def obtenerRemito(self):
        """msg 27 — devuelve los datos de sus remitos con la documentación asociada."""
        datos = []
        for remito in self.remito.all():
            datos.append(
                {
                    'numero': remito.getNumero(),  # msg 28
                    'documentacion': remito.buscarDocumentacion(),  # msg 29
                }
            )
        return datos

    def recibir(self, estadoBolsin, estadoRemito, estadoDocumentacion, fechaHora, responsable):
        """msg 52 — registra la recepción y propaga a remitos y documentación.

        Corresponde a la opción 1 del CU 28: el contenido del bolsín es igual al
        registrado. Las otras tres opciones todavía no están modeladas.
        """
        actual = None
        for cambioEstado in self.cambioEstado.all():
            if cambioEstado.sosActual():  # msg 53
                actual = cambioEstado
        if actual is not None:
            actual.setFechaHoraFin(fechaHora)  # msg 54

        CambioEstadoBolsin.objects.create(  # msg 55 «create»
            bolsin=self,
            estado=estadoBolsin,
            fechaHoraInicio=fechaHora,
            responsableCE=responsable,
        )

        for remito in self.remito.all():
            remito.aceptar(estadoRemito, estadoDocumentacion, fechaHora, responsable)  # msg 56

    def getEstadoActual(self):
        for cambioEstado in self.cambioEstado.all():
            if cambioEstado.sosActual():
                return cambioEstado.estado
        return None

    def __str__(self):
        return f'Bolsín {self.numeroBolsin}'


class CambioEstadoBolsin(models.Model):
    fechaHoraInicio = models.DateTimeField()
    fechaHoraFin = models.DateTimeField(null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    bolsin = models.ForeignKey(Bolsin, on_delete=models.CASCADE, related_name='cambioEstado')
    responsableCE = models.ForeignKey(
        Empleado, on_delete=models.PROTECT, null=True, blank=True
    )

    def sosActual(self):
        """msg 14, 53."""
        return self.fechaHoraFin is None

    def sosEnviado(self):
        """msg 15 — delega en su estado."""
        return self.estado.sosEnviado()  # msg 16

    def setFechaHoraFin(self, fechaHora):
        """msg 54."""
        self.fechaHoraFin = fechaHora
        self.save()

    def __str__(self):
        return f'{self.bolsin} → {self.estado}'
