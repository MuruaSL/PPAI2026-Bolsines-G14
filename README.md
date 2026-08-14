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

## Estructura

```
docs/
  cu28-contrato-secuencia.md    contrato de los 66 mensajes
  diagramas/                    modelo de dominio y diagramas de la E1
```

## Documentación de la cátedra

Descripción del Caso · ERS v1.2 · Modelo de Dominio v1.1 · Consignas · Consignas UX
