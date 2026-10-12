# Corrección de la Entrega 1

Nota: **10**. Lo marcado es de nombres y prolijidad, no de lógica. Fotos leídas el 12/10/2026;
algunas anotaciones manuscritas quedan marcadas como dudosas.

## Máquina de estados de Documentación (pág. 7)

| Marca del profesor | Qué significa | Acción |
|---|---|---|
| "Están invertidas las direcciones" | En Registrada ⇄ EnRemito las puntas de flecha están al revés | CU 15 va de Registrada a EnRemito |
| `new()` sobre Registrada | La transición inicial crea el objeto | `Registrar()` pasa a `new()` |
| `CU 17 Cancelar()` encerrado + `16. quitarDeRemito()` | EnRemito → Registrada también es CU 16 Modificar Remito | Agregar CU 16 `quitarDeRemito()`. **Mantener** CU 17: el ERS dice que cancelar devuelve la documentación a Registrada |
| `NotificarCM()` subrayado + `devolver()` | Mal nombre | NoRecibida → Registrada: `devolver()` |
| `CU 31` en NoRecibida → DeBaja | Esa baja es el CU 31 (Registrar revisión), no el 9 | Cambiar etiqueta de CU 9 a CU 31 |
| "Ojo con los nombres de los métodos" | `AgregarRemitoAlBolsin()`, `retirarBolsinCM()`, `NotificarCM()` son métodos de Documentación pero hablan de Bolsín o Remito | Renombrar desde el punto de vista de Documentación (ej. `incluirEnBolsin()`) |
| "Ojo! Poco cohesivo pero bien!" | Aprobó el `recibir()` único pero lo marcó | Ver siguiente |
| "A `recibir()` lo separaría en métodos más cohesivos. Les va a ser más fácil para la implementación" | `recibir()` hace cuatro cosas según una condición | Un método por resultado |

El modelo de dominio ya nombra una transición: `Documentacion.remitar()` (vs. `IncluirEnRemito()`).

## Diagrama de clases (pág. 4)

Nota: "Revisar los atributos de las clases. Tiene el diagrama de clases del Modelo de Dominio".

Comparación hecha clase por clase contra el modelo de la cátedra:

- Coinciden: Empleado, TipoDocumento, Documentacion, ComisionMedica, DetalleRemito, Remito,
  Bolsin, CambioEstadoBolsin, CambioEstadoDocumentacion.
- **Estado tiene un atributo de más: `esEnviado`**. El dominio solo tiene `ambito`, `descripcion`
  y `nombre`; `sosEnviado()` ya cumple esa función. Hay tachaduras sobre sus atributos.
- Sesion y Usuario no están en el dominio pero las tildó.
- Marcó con `?` los 8 atributos de la Pantalla (`rdbtnOpt1..4`, `lblrdBtn1..4`): parecen repetitivos.
- El código Django ya no tiene `esEnviado`.

## Diagrama de secuencia (págs. 5 y 6)

Los 66 mensajes quedaron tildados.

| Marca | Significa |
|---|---|
| "¡Objetos estereotipados! UML 2.0" | Las líneas de vida llevan estereotipo: actor, boundary, control, entity (dibujó cada ícono) |
| "Pueden ir en un mismo loop" | Los loops 12–16 y 18–20 se pueden unir. Dice "pueden": opcional |
| "Ahí empieza" | El marco del loop de remitos arranca en el mensaje 28, no antes del 27 |
| **"Inconsistencia con ME! `recibir()`"** | La secuencia llama `aceptar()` en Documentación (msg 58); la máquina de estados dice `recibir()`. Deben coincidir |
| CU 29 encerrado | Posiblemente no va como columna inicial. Ver abajo |

## Lecturas dudosas (resueltas con el alumno)

- **"desc" en Documentacion**: el dominio no tiene `descripcion` ahí; el asunto *es* la descripción
  según la descripción del caso. No agregar; consultar.
- **"¿Kilos?" en ComisionMedica**: no está en dominio ni ERS. El único peso es `Bolsin.peso`, en
  gramos. No agregar; consultar.
- **CU 29**: lectura más probable: la caja baja a la altura del mensaje 64 con el `«include»`
  llegándole por la izquierda. Alternativa: marco `ref CU29`. Consultar.
- **Anotación junto a CU 20**: ilegible ("documentación en remito"?). Ya existe CU 20/21 hacia EnRemito.
- Un garabato azul arriba a la derecha del loop de `recibir y aceptar`: es un tachón, se descarta.

## Impacto en el código

Nada urgente. El código sigue la secuencia (usa `aceptar()`), y la inconsistencia se arregla del
lado de la máquina de estados. Solo uniría los loops si el diagrama corregido lo hace.

## Archivos de los diagramas

- Máquina de estados: draw.io (editable).
- Secuencia y clases: posiblemente Enterprise Architect (sin licencia). La E2 pide diagramas
  nuevos de la parte rediseñada, así que quizá no haya que reabrirlos. Consultar si hay que
  reentregar los de E1 corregidos.
