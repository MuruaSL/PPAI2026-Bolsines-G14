# Sistema Bolsines — PPAI 2026

Proyecto Práctico de Aplicación Integrador · **Diseño de Sistemas de Información**
UTN — Facultad Regional Córdoba · Curso **3K3** · **Grupo 14**

## Caso asignado

Grupo par:

- **CU 28 — Registrar recepción de bolsín**
- **Máquina de estados de `Documentación`**

## El dominio

Un organismo controlador nacional (sede central en CABA, una CMC y más de 80 comisiones médicas
jurisdiccionales) intercambia documentación física entre comisiones médicas dentro de *bolsines*:
bolsas cerradas con un precinto numerado, transportadas por correo. El sistema registra, envía y
sigue esa documentación, y debe poder informar en todo momento en qué estado está cada bolsín y qué
empleado es responsable de cada actualización.

### Cadenas de estados

```
Documentación   Registrada → EnRemito → EnBolsínSaliente → EnBolsínEnviado
                → RecibidaYAceptada | NoRecibida | RecibidaYRechazada | ParaRedirigir | DeBaja

Remito          Creado → EnBolsínSaliente → EnBolsínEnviado
                → Recibido y Aceptado | Recibido y Aceptado Parcial

Bolsín          Creado → Cerrado (precinto) → Enviado → Recibido en CM destino | DeBaja
```

## Estado de las entregas

| Entrega | Contenido | Estado |
|---|---|---|
| E1 · Análisis | Clases de análisis, secuencia, máquina de estados de Documentación | Entregada (25/05/2026), **sin devolución docente** |
| E2 · Diseño | Patrón GoF + implementación funcionando + defensa oral | En curso |
| UX | MoodBoard, Mapa de Empatía, User Journey sobre una Persona del EB | En paralelo |

### Qué está implementado

- **Flujo principal completo** del CU 28, mensajes 1 a 66: opción 1, el contenido del bolsín
  es igual al registrado.
- **Flujo alternativo A6**: el EB no confirma la registración.
- 16 pruebas automatizadas.

**Falta**: los flujos alternativos A3, A4 y A5 (documentación faltante, documentación que no
corresponde al destino, documentación para redirigir). Se implementan junto con el patrón de
diseño de la Entrega 2, todavía sin asignar por el docente tutor.

El backlog completo, con lo detectado que hay que decidir, está en
[`docs/pendientes.md`](docs/pendientes.md).

## Regla que gobierna la implementación

**El código debe ser un calco del modelado.** Tienen que existir las clases del diagrama, el gestor,
las pantallas/boundary y las entidades, y los pases de mensajes deben usar exactamente los métodos
listados en el diagrama de secuencia. La cátedra evalúa la consistencia con el modelado como
criterio de corrección explícito.

El contrato está transcrito mensaje por mensaje en
[`docs/cu28-contrato-secuencia.md`](docs/cu28-contrato-secuencia.md). Ante cualquier duda sobre cómo
implementar algo, manda el diagrama, no la conveniencia del código.

## Requisitos de la Entrega 2

1. Patrón de diseño de Gamma identificado y justificado (a acordar con el docente tutor), con vista
   estática (tipos de datos, retornos, parámetros, visibilidad) y vista dinámica.
2. Implementación que **corra el día de la defensa**: flujo principal + al menos **dos flujos
   alternativos**.
3. Persistencia a base de datos.
4. Tecnología web. Python o Java (lenguajes con soporte de la cátedra).

## Cómo correrlo

Hace falta Python 3.10 o superior. El entorno virtual y la base de datos no están en el
repositorio, así que cada uno los crea en su máquina.

**1. Clonar y entrar a la carpeta**

```bash
git clone https://github.com/MuruaSL/PPAI2026-Bolsines-G14.git
cd PPAI2026-Bolsines-G14
```

**2. Crear el entorno virtual e instalar Django**

En macOS o Linux:

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

En Windows:

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

**3. Crear la base de datos y cargar el escenario de prueba**

```bash
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py cargardatos
```

En Windows, reemplazar `./.venv/bin/python` por `.venv\Scripts\python` en este paso y en los
siguientes.

**4. Levantar el servidor**

```bash
./.venv/bin/python manage.py runserver
```

Abrir http://localhost:8000

**Correr las pruebas**

```bash
./.venv/bin/python manage.py test recepcion
```

### El escenario de prueba

`cargardatos` deja cargado un Encargado de Bolsines de la Comisión Médica Córdoba y cuatro
bolsines, elegidos para que se vea que el filtrado funciona:

| Bolsín | Precinto | ¿Debe listarse? | Por qué |
|---|---|---|---|
| 1001 | PRE-88231 | Sí | Enviado a Córdoba, con 2 remitos y 3 documentaciones |
| 1002 | PRE-88245 | Sí | Enviado a Córdoba, con 1 remito |
| 1003 | PRE-90001 | No | Su destino es Rosario, no la CM del usuario |
| 1004 | PRE-90002 | No | Su destino es Córdoba pero está Cerrado, no Enviado |

Una vez que se registra la recepción de un bolsín, deja de aparecer en el listado: ya no está
en estado Enviado. Para volver al punto de partida, correr `cargardatos` de nuevo.

## Estructura

```
config/                         configuración del proyecto Django
recepcion/
  models.py                     las entidades del diagrama de clases
  gestor.py                     GestorRegRecepBolsin, la clase control
  pantalla.py                   PantallaRegRecepBolsin, el boundary
  views.py, urls.py             la mitad web del boundary
  templates/recepcion/          las pantallas
  tests.py                      pruebas del CU 28
  management/commands/
    cargardatos.py              escenario de prueba
docs/
  cu28-contrato-secuencia.md    contrato de los 66 mensajes
  pendientes.md                 backlog de lo que falta decidir
  diagramas/                    modelo de dominio y diagramas de la E1
```

## Documentación de la cátedra

Descripción del Caso · ERS v1.2 · Modelo de Dominio v1.1 · Consignas · Consignas UX
