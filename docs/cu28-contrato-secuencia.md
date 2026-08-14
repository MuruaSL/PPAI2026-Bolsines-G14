# CU 28 — Registrar recepción de bolsín · Contrato de secuencia

Transcripción del diagrama de secuencia de la Entrega 1 (66 mensajes).

**Esto es un contrato, no documentación.** La implementación de la Entrega 2 debe ser un calco:
cada mensaje numerado tiene que existir en el código, con el mismo nombre de método, emitido por
la misma clase y recibido por la misma clase. La cátedra evalúa explícitamente la *consistencia con
el modelado* (clases gestor, pantalla/boundary, entidades).

Diagramas fuente en [`diagramas/`](diagramas/).

## Escenario modelado

Flujo principal únicamente: **opción 1 — el contenido del bolsín es igual al registrado**.

Las opciones 2, 3 y 4 (documentación faltante, documentación que no corresponde al destino,
documentación para redirigir) **no están modeladas todavía**. Ver [Pendientes](#pendientes).

## Participantes

| Lifeline | Estereotipo |
|---|---|
| `EB` | actor |
| `:PantallaRegRecepBolsin` | boundary |
| `:GestorRegRecepBolsin` | control |
| `actual:Sesion`, `:Empleado`, `logeado:Empleado` | entity |
| `:ComisionMedica`, `delEmpleado:ComisionMedica` | entity |
| `:Bolsin`, `seleccionado:Bolsin` | entity |
| `:Remito`, `:DetalleRemito` | entity |
| `:Documentacion`, `:TipoDocumento` | entity |
| `:Estado` | entity |
| `:CambioEstadoBolsin`, `actual:CambioEstadoBolsin`, `new:CambioEstadoBolsin` | entity |
| `:CambioEstadoDocumentacion`, `actual:cambio de estado`, `nuevo:CambioEstadoDocumentacion` | entity |
| `CU29. NotificarRecepcion de bolsin` | caso de uso incluido |

## Mensajes

### Apertura y CM del usuario logueado

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 1 | EB | `:PantallaRegRecepBolsin` | `regRecepBolsin()` «create» |
| 2 | Pantalla | Pantalla | `habilitarPantalla()` |
| 3 | Pantalla | `:GestorRegRecepBolsin` | `optRegRecepBolsin()` «create» |
| 4 | Gestor | Gestor | `buscarCmyMostrarlo()` |
| 5 | Gestor | `actual:Sesion` | `getUsuarioEnSesion()` |
| 6 | Gestor | `:Empleado` | `*esTuUsuario()` |
| 7 | Gestor | Gestor | `getCM()` |
| 8 | Gestor | `logeado:Empleado` | `getCM()` |
| 9 | `logeado:Empleado` | `delEmpleado:ComisionMedica` | `getNombre()` |
| 10 | Gestor | Pantalla | `mostrarCM()` |

### Búsqueda de bolsines en estado enviado

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 11 | Gestor | Gestor | `buscarBolsinesEnviados()` |

**loop bolsines** `[Mientras haya Bolsines]`

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 12 | Gestor | `:Bolsin` | `esTuCMDestino()` |
| 13 | Gestor | `:Bolsin` | `sosEnviado()` |

&nbsp;&nbsp;**loop cambio de estado** `[mientras haya cambios de estado]`

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 14 | `:Bolsin` | `:CambioEstadoBolsin` | `sosActual` |
| 15 | `:Bolsin` | `actual:CambioEstadoBolsin` | `sosEnviado()` |
| 16 | `actual:CambioEstadoBolsin` | `:Estado` | `sosEnviado` |

### Datos a mostrar de cada bolsín

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 17 | Gestor | Gestor | `obtenerCMOrigenYnroPrecinto()` |

**loop Bolsines** `[Mientras haya bolsines enviados]`

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 18 | Gestor | `:Bolsin` | `getCMOrigen()` |
| 19 | `:Bolsin` | `:ComisionMedica` | `getNombre` |
| 20 | Gestor | `:Bolsin` | `getNroPrecinto()` |

### Selección del bolsín

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 21 | Gestor | Gestor | `mostrarYPedirSeleccionBolsin()` |
| 22 | Gestor | Pantalla | `mostrarDatosBolsin()` |
| 23 | Gestor | Pantalla | `habilitarSeleccionBolsin()` |
| 24 | EB | Pantalla | `tomarSeleccionBolsin()` |
| 25 | Pantalla | Gestor | `tomarSeleccionBolsin()` |

> **Corrección acordada.** En los diagramas de la E1 la Pantalla expone `tomarSeleccionBolsin()` y
> el Gestor `tomarSeleccionbolsin()`, con `b` minúscula. Es un typo, no una distinción intencional.
> Se unifica a `tomarSeleccionBolsin()` en ambos lados.
>
> **Pendiente:** aplicar esta corrección en los diagramas fuente antes de la Entrega 2, para que el
> modelo y el código sigan coincidiendo. El diagrama manda; acá el código no diverge, se adelanta a
> una corrección que hay que hacer en el modelo.

### Remitos y documentación del bolsín seleccionado

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 26 | Gestor | Gestor | `mostrarDatosRemitoYDocAsociada()` |
| 27 | Gestor | `seleccionado:Bolsin` | `obtenerRemito()` |

**loop remitos** `[Mientras haya Remitos]`

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 28 | `seleccionado:Bolsin` | `:Remito` | `getNumero()` |
| 29 | `seleccionado:Bolsin` | `:Remito` | `buscarDocumentacion()` |

&nbsp;&nbsp;**loop detalles Remito** `[mientras haya detalles]`

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 30 | `:Remito` | `:DetalleRemito` | `getDocumentacion()` |
| 31 | `:DetalleRemito` | `:Documentacion` | `getAsunto()` |
| 32 | `:DetalleRemito` | `:Documentacion` | `getTipoDocumentacion()` |
| 33 | `:Documentacion` | `:TipoDocumento` | `getNombre()` |

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 34 | Gestor | Pantalla | `mostrarDatosRemitoYDocAsociada()` |

### Opción de recepción y confirmación

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 35 | Gestor | Gestor | `pedirSelecOptRecBolsin()` |
| 36 | Gestor | Pantalla | `mostrarOptsRecBolsin()` |
| 37 | EB | Pantalla | `tomarSeleccionOptRecBolsin()` |
| 38 | Pantalla | Gestor | `tomarSeleccionOptRecBolsin()` |
| 39 | Gestor | Gestor | `pedirConfirmacionSeleccionParaRegCorresp()` |
| 40 | Gestor | Pantalla | `pedirConfirmacionSeleccionParaRegCorresp()` |
| 41 | EB | Pantalla | `tomarConfirmacionSeleccionParaRegCorresp()` |
| 42 | Pantalla | Gestor | `tomarConfirmacionSeleccionParaRegCorresp()` |

### Búsqueda de los estados a asignar (tres ámbitos)

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 43 | Gestor | Gestor | `buscarEstados()` |

**loop estados** `[Mientras haya estados]` — ámbito Bolsín

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 44 | Gestor | `:Estado` | `sosAmbitoBolsin()` |
| 45 | Gestor | `:Estado` | `sosRecibidoEnCMDestino()` |

**loop estados** `[mientras haya estados]` — ámbito Remito

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 46 | Gestor | `:Estado` | `sosAmbitoRemito()` |
| 47 | Gestor | `:Estado` | `sosRecibidoYAceptado()` |

**loop estados** `[mientras haya estados]` — ámbito Documentación

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 48 | Gestor | `:Estado` | `sosAmbitoDocumentacion()` |
| 49 | Gestor | `:Estado` | `sosRecibidaYAceptada()` |

### Registración en cascada

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 50 | Gestor | Gestor | `getFechaHoraActual()` |
| 51 | Gestor | Gestor | `regRecepcionBolsin()` |
| 52 | Gestor | `seleccionado:Bolsin` | `recibir()` |
| 53 | `seleccionado:Bolsin` | `:CambioEstadoBolsin` | `sosActual*()` |
| 54 | `seleccionado:Bolsin` | `actual:CambioEstadoBolsin` | `setFechaHoraFin()` |
| 55 | `seleccionado:Bolsin` | `new:CambioEstadoBolsin` | `new()` «create» |

**loop recibir y aceptar** `[Para todos los remitos del bolsin]`

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 56 | `seleccionado:Bolsin` | `:Remito` | `aceptar()` |

&nbsp;&nbsp;**loop detRemito** `[mientrasHayaDetalles]`

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 57 | `:Remito` | `:DetalleRemito` | `aceptar()` |
| 58 | `:DetalleRemito` | `:Documentacion` | `aceptar()` |
| 59 | `:Documentacion` | `:CambioEstadoDocumentacion` | `sosActual*()` |
| 60 | `:Documentacion` | `actual:cambio de estado` | `setFechaHoraFin()` |
| 61 | `:Documentacion` | `:Documentacion` | `crearNuevoCE()` |
| 62 | `:Documentacion` | `nuevo:CambioEstadoDocumentacion` | `new()` «create» |

### Notificación y cierre

| # | Emisor | Receptor | Mensaje |
|---|---|---|---|
| 63 | Gestor | Gestor | `notificarCM()` |
| 64 | Gestor | `CU29. NotificarRecepcion de bolsin` | «include» |
| 65 | Gestor | Pantalla | `informarResponsable()` |
| 66 | Gestor | Gestor | `finCU()` |

## Verificación contra el diagrama de clases

Los 66 mensajes fueron cruzados contra el diagrama de clases de análisis: **todos los métodos
invocados existen en la clase receptora, con el mismo nombre**. No hay mensajes huérfanos ni
métodos que aparezcan solo en la secuencia.

## Pendientes

1. **Flujos alternativos sin modelar.** La secuencia cubre solo la opción 1. La Entrega 2 exige que
   al menos dos flujos alternativos funcionen en la defensa. Hoy `Bolsin.recibir()` resuelve un
   único caso y debe resolver cuatro:

   | Opción | Documentación | Remito | Bolsín |
   |---|---|---|---|
   | 1 · Contenido igual | Recibida y Aceptada | Recibido y Aceptado | Recibido en CM destino |
   | 2 · Falta documentación | No Recibida → Registrada o De Baja | Recibido y Aceptado Parcial | Recibido en CM destino |
   | 3 · No corresponde al destino | Recibida y Rechazada | — | Recibido en CM destino |
   | 4 · Redirigir a otra área | Para Redirigir | — | Recibido en CM destino |

2. **Patrón de diseño de la Entrega 2.** Ese `recibir()` que debe resolver cuatro variantes es el
   punto natural donde entra el patrón GoF. A acordar con el docente tutor antes de implementar.

3. **Sin devolución docente.** A la fecha no hubo corrección de la Entrega 1, así que el modelado
   podría cambiar. Cualquier cambio que la cátedra pida debe reflejarse acá antes que en el código.
