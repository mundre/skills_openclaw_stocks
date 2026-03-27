---
name: arquitecto-categorico
description: Formaliza dominios de datos y APIs con teoria de categorias. Usar para disenar DDL SQL, JSON Schema, OpenAPI, GraphQL, Prisma, integracion multi-esquema, estrategias de migracion, auditorias de schemas/APIs/KBs y consultas de modelado estructural cuando importa la trazabilidad formal.
_manifest: {"urn":"urn:fxsl:skill:arquitecto-categorico:1.0.0","type":"lazy_load_endofunctor"}
extensions: {"fxsl":{"skill":{"form":"extended","references":["references/engine-map.md","references/kb-map.md","references/static-modeling.md","references/dynamic-modeling.md","references/integration-modeling.md","references/evolution-audit.md","references/provenance.md"]}}}
---

# Arquitecto Categorico

Convierte requisitos ambiguos en artefactos formales de datos y APIs. El criterio rector es estructural: objetos, morfismos, composicion, invariantes, limites/colimites, comportamiento y migracion antes de cualquier detalle procedimental.

## Scope

Usa esta skill cuando el usuario pida:
- modelado estatico de dominio
- DDL PostgreSQL u otro schema formal
- JSON Schema, OpenAPI, GraphQL SDL o Prisma
- integracion de multiples esquemas o fuentes heterogeneas
- estrategia de migracion de esquema
- auditoria de schema, API, KB o DAL
- explicacion teorica de una decision de modelado

No la uses para:
- logica imperativa de aplicacion
- implementacion ad-hoc en Python o TypeScript fuera de schemas/APIs
- UI, infraestructura o automatizacion no estructural

## Procedimiento

1. Clasifica la solicitud en uno de cinco modos: `static`, `dynamic`, `integration`, `audit`, `consult`.
2. Si falta una decision estructural o el artefacto target cambia el resultado, pide una sola aclaracion focalizada. Ejemplos tipicos: entidad vs evento, estatico vs dinamico, SQL vs documento, fusion vs restriccion.
3. Formula primero el modelo formal minimo:
   - objetos y morfismos
   - identidades y composicion
   - path equations o restricciones
   - limite/colimite, lens, coalgebra o adjuncion de migracion si aplica
4. Emite el artefacto target solo despues de fijar esa estructura.
5. Si el formato target pierde estructura relevante, declara explicitamente `Functor Information Loss`.
6. Cierra con siguientes pasos pragmaticos: validacion, migracion, integracion o artefacto complementario.

## Dispatch

- `static`: leer `references/engine-map.md` y luego `references/static-modeling.md`.
- `dynamic`: leer `references/engine-map.md` y luego `references/dynamic-modeling.md`.
- `integration`: leer `references/engine-map.md` y luego `references/integration-modeling.md`.
- `audit`: leer `references/engine-map.md` y luego `references/evolution-audit.md`.
- `consult`: leer `references/kb-map.md` y cargar solo el bloque teorico que corresponda al problema.

## Reglas Duras

- Mantener la salida dentro del dominio de estructuras de datos, integracion y APIs.
- No exponer nombres internos `CM-*` al usuario salvo que pida internals del metodo.
- No inventar tooling ni fuentes que no existan en el bundle o en las rutas fuente referenciadas.
- Si el problema no puede resolverse sin una decision de diseno pendiente, detenerse y pedirla.

## Outputs Canonicos

Usa uno de estos formatos segun la solicitud:
- modelo categorico sintetico
- PostgreSQL DDL
- JSON Schema
- OpenAPI 3.x
- GraphQL SDL
- Prisma schema
- Mermaid o PlantUML
- estrategia de migracion `Delta/Sigma/Pi`
- informe de auditoria por severidad

## Carga Bajo Demanda

- Para el mapa operativo de motores, leer `references/engine-map.md`.
- Para el mapa del corpus teorico y de auditoria, leer `references/kb-map.md`.
- Para modelado estatico, leer `references/static-modeling.md`.
- Para comportamiento y DAL, leer `references/dynamic-modeling.md`.
- Para integracion heterogenea, leer `references/integration-modeling.md`.
- Para migracion, versionado y auditoria, leer `references/evolution-audit.md`.
- Para trazabilidad del bundle frente a sus fuentes, leer `references/provenance.md`.
