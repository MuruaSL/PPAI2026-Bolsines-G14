# Pendientes

Backlog de lo que falta para la Entrega 2 y para la defensa oral. No es trabajo hecho ni
comprometido: es lo detectado que hay que decidir.

## 1. Lógica de carga de los datos previos a la recepción

**El problema.** Hoy el escenario de prueba (`manage.py cargardatos`) inserta los bolsines
directamente en estado `Enviado`, con sus remitos en `EnBolsinEnviado` y su documentación
también. Es una semilla: el sistema nunca los llevó a ese estado, aparecen ahí ya puestos.

El CU 28 arranca con un bolsín que ya fue armado, cerrado con precinto y retirado por el correo.
Toda esa cadena previa está simulada, no implementada.

**Qué casos de uso producen ese estado inicial:**

| CU | Nombre | Deja a la documentación en | Deja al remito en | Deja al bolsín en |
|---|---|---|---|---|
| 7 | Registrar Documentación | Registrada | — | — |
| 15 | Generar Remito | EnRemito | Creado | — |
| 19 | Generar Bolsín | EnBolsinSaliente | EnBolsinSaliente | Creado |
| 39 | Cerrar Bolsín | — | — | Cerrado |
| 27 | Registrar el retiro de bolsines | EnBolsinEnviado | EnBolsinEnviado | Enviado |

Además, la parametrización de soporte: CU 23 (Registrar Comisión Médica), CU 11 (Registrar Tipo
de Documento) y CU 1 (Registrar usuario), que hoy también vienen por semilla.

**Cómo lo leo.** La consigna de la Entrega 2 pide implementar *el caso de uso modelado* —el 28—
con su flujo principal y al menos dos alternativos. No pide la cadena entera, así que la semilla
es una decisión legítima y defendible: aísla el CU asignado, que es lo que se corrige.

El riesgo es la defensa oral. Si el tutor pregunta *"¿y cómo llegó ese bolsín a estado Enviado?"*,
la respuesta honesta hoy es "lo cargamos nosotros". Eso puede estar perfectamente bien, o puede
abrir una repregunta incómoda.

**Opciones, de menor a mayor esfuerzo:**

1. **Dejarlo como está** y tener preparada la explicación: el alcance de la entrega es el CU 28,
   los estados previos son precondición del caso de uso. Cuesta cero y es argumentable.
2. **Cargar los datos por el admin de Django** en vez de por semilla, para poder mostrar en vivo
   de dónde salen. Cuesta poco, no requiere modelar nada nuevo.
3. **Implementar CU 19, 39 y 27** (generar, cerrar y retirar bolsín), que son los tres que tocan
   directamente al bolsín. Permite demostrar la cadena completa en vivo. Requiere los diagramas
   de esos CU, que hoy no tenemos.

**Bloqueante para la opción 3:** no tenemos los diagramas de secuencia ni de clases de esos casos
de uso. Sin ellos no se puede aplicar la regla del calco, y escribirlos por nuestra cuenta sería
inventar modelado que la cátedra no validó.

## 2. Flujos alternativos A3, A4 y A5

Sin implementar. Ver la tabla de estados por opción en
[`cu28-contrato-secuencia.md`](cu28-contrato-secuencia.md).

Van junto con el patrón de diseño de la Entrega 2, todavía sin asignar por el docente tutor.

## 3. Autenticación real

No hay login. La vista toma la última `Sesion` cargada como la sesión activa
(`views.py`, `_abrirPantalla`). El CU 5 Iniciar sesión no está implementado.

Para el CU 28 alcanza, porque el caso de uso arranca con un usuario ya logueado. Pero si se quiere
mostrar que la CM que aparece depende de quién entró, hace falta un login mínimo.

## 4. Corrección a aplicar en los diagramas

En los diagramas de la E1, la Pantalla expone `tomarSeleccionBolsin()` y el Gestor
`tomarSeleccionbolsin()`, con `b` minúscula. Es un typo. El código ya usa `tomarSeleccionBolsin()`
en ambos lados; falta corregirlo en los diagramas fuente antes de la Entrega 2.

## 5. SECRET_KEY en el repositorio

`config/settings.py` tiene el `SECRET_KEY` que genera Django por defecto, commiteado, y el repo es
público. Como el proyecto no se despliega, el riesgo real es nulo. Moverlo a variable de entorno es
una mejora opcional.
