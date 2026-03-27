# Static Modeling

Playbook para modelado estructural.

## Objetivo

Formalizar dominios como categorias y emitir artefactos declarativos sin contaminar el modelo con logica procedimental.

## Modelo minimo

Para cada dominio, define:
- objetos: entidades o tipos
- morfismos: relaciones tipadas
- identidades: `id_A`
- composicion: cadenas `g o f`
- path equations: restricciones de coherencia

## Construcciones utiles

### Limites

Usar cuando importa integridad, composicion fuerte y joins.

- producto: combinacion estructural
- pullback: join sobre clave compartida
- equalizer: restriccion donde dos caminos deben coincidir

### Colimites

Usar cuando importa fusion, union o flexibilidad.

- coproducto: union tipada
- pushout: merge por parte comun
- coequalizer: identificacion de equivalencias

## Tensiones frecuentes

- entidad vs evento
- token vs tipo
- todo vs partes
- formal vs informal

Si una tension cambia el schema resultante, pide una sola aclaracion antes de emitir.

## Mapeo a artefactos

| Categorico | SQL | GraphQL | OpenAPI | JSON Schema | Prisma |
|---|---|---|---|---|---|
| objeto | tabla | type | schema component | object | model |
| morfismo | foreign key | field tipado | `$ref` | `$ref` | `@relation` |
| identidad | primary key | `id: ID!` | propiedad requerida | propiedad requerida | `@id` |
| limite | join/check | nested type | `allOf` | `allOf` | unique compuesto |
| colimite | union | union | `oneOf` | `oneOf` | patron explicito |

## Regla de emision

Primero presenta el modelo sintetico si el dominio es ambiguo. Emite DDL/schema final cuando la estructura ya esta fijada.

## Firma sugerida

```text
Categoria: C_dom
Obj: {...}
Morph: {...}
Path Equations: [...]
Construcciones: [...]
Artefacto target: ...
```
