# Cheatsheet para la reunión con el tutor

## Preguntas, en orden de prioridad

1. **¿Puedo aplicar State sobre la máquina de estados de Documentación?** (si no, Strategy)
2. ¿Hay que reentregar corregidos los diagramas de E1, o alcanzan los nuevos de E2?
3. CU 29 en la secuencia: ¿caja abajo con el `«include»` desde la izquierda, o `ref CU29`?
4. EnRemito → Registrada: ¿agrego CU 16 `quitarDeRemito()` y mantengo CU 17 `Cancelar()`?
5. ¿"desc" en Documentacion es un atributo `descripcion`? (el dominio no lo tiene)
6. ¿"¿Kilos?" en ComisionMedica? (¿era sobre `Bolsin.peso`, que es en gramos?)

## Los dos patrones a proponer

| | **State** (recomendado) | **Strategy** |
|---|---|---|
| Qué resuelve | Cada estado de Documentación pasa a ser una clase con sus transiciones | Cada opción de recepción (igual / falta / no corresponde / redirigir) es un algoritmo intercambiable |
| Por qué encaja | La máquina de estados asignada ya *es* el patrón. Elimina el "¿sos ámbito bolsín? ¿sos recibido?" de los msgs 44–49. Parte `recibir()` como pidió el profesor | Calza exacto con las 4 opciones del CU. Da los 2 alternativos que exige la E2 |
| Riesgo | `Estado` hoy es entidad persistida: hay que mapearla a las clases del patrón | Es más simple, pero no usa la máquina de estados asignada |

Frase clave: el profesor pidió separar `recibir()` en métodos cohesivos → eso es el punto de entrada
natural de cualquiera de los dos patrones.

## Si te preguntan por el diseño actual

- **Por qué el gestor recorre todos los bolsines en vez de filtrar:** así lo modela la secuencia
  (msgs 12 y 13 preguntan a cada bolsín), aplicando Experto.
- **Por qué la cascada está repartida (Bolsin → Remito → DetalleRemito → Documentacion):** cada
  clase resuelve lo suyo, msgs 52 a 62. El gestor no toca estados.
- **Por qué no hay estado en la sesión web:** cada request reconstruye pantalla y gestor con
  `regRecepBolsin()`, así el recorrido de mensajes es siempre el del diagrama.
- **De dónde sale que el bolsín esté Enviado:** de una semilla (`cargardatos`). Los CU previos
  (7, 15, 19, 39, 27) no están implementados y no tenemos sus diagramas. Ver `pendientes.md`.

## Nombres a corregir en la máquina de estados

`Registrar()` → `new()` · `IncluirEnRemito()` → `remitar()` (nombre del dominio) ·
`NotificarCM()` → `devolver()` · `AgregarRemitoAlBolsin()` → `incluirEnBolsin()` ·
`retirarBolsinCM()` → algo de Documentación · `recibir()` → un método por resultado.
