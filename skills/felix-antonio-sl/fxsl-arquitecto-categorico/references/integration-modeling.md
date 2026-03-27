# Integration Modeling

Playbook para integracion de fuentes heterogeneas.

## Objetivo

Unificar esquemas distintos sin perder trazabilidad estructural.

## Patrones principales

### Grothendieck `int F`

Usar cuando hay:
- federacion
- multi-tenant
- versiones temporales
- zonas de data lake

Construccion:
- indice `I`: fuentes, tenants, versiones o zonas
- `F(i)`: schema de cada indice
- `F(f)`: traduccion entre esquemas
- `int F`: espacio global de objetos y morfismos

### Multimodel

Usar cuando conviven:
- SQL
- documentos
- grafos
- key-value

Normaliza cada fuente a un lenguaje comun:
- objetos: tablas, colecciones, nodos, keyspaces
- morfismos: foreign keys, refs, edges, paths

## Query as functor

Trata la consulta como un funtor desde el schema global al tipo de salida:
- relacional
- documental
- grafo
- flat

## Proveniencia

Preservar siempre:
- fuente de origen
- transformacion aplicada
- equivalencia semantica usada

## Preguntas de colapso utiles

- federacion o esquema global consolidado
- salida target relacional, documental, grafo o flat
- integridad estricta o compatibilidad flexible

## Firma sugerida

```text
Fuentes: [...]
Metodo: Grothendieck | Multimodel | Ambos
Global Schema: ...
Wrappers: ...
Query target: ...
Proveniencia: completa | parcial
```
