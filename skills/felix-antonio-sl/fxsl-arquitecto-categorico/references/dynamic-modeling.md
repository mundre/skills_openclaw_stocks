# Dynamic Modeling

Playbook para comportamiento, APIs stateful y capas de acceso.

## Decision principal

Selecciona la estructura segun el tipo de dinamica:

- `lens`: lectura/escritura entre dos vistas
- `coalgebra`: comportamiento observable, reactivo o sustituible
- `monada`: efectos, fallo, no determinismo, estado o trazas

## Coalgebra

Modelo:
- estado oculto `U`
- interfaz `F`
- comportamiento `c: U -> F(U)`

Usar para:
- APIs con estado
- servicios reactivos
- comparacion de componentes por equivalencia externa

### Bisimulacion

Dos componentes son sustituibles si producen observaciones indistinguibles y preservan transiciones relevantes.

## Lenses

Modelo:
- `expose: S -> O`
- `update: S x I -> S`

Usar para:
- vistas derivadas
- CQRS
- document view sobre SQL

## Monadas

Usar cuando la dinamica central es un efecto:
- `Maybe`: fallo
- `List`: multiples resultados
- `Dist`: probabilidad
- `State`: estado mutable
- `Writer`: auditoria o log

## DAL categorico

### Storage

- limites -> SQL cuando importa integridad y joins
- colimites -> NoSQL cuando importa flexibilidad y fusion
- mixto -> lens asimetrico entre write model y read model

### API

- REST: recursos y morfismos CRUD
- GraphQL: tipos y pullbacks de consulta
- gRPC: servicios y RPCs como morfismos
- streams: comportamiento continuo

### Repository

Tratalo como coalgebra. Si dos repositorios son bisimilares, son intercambiables.

### ORM

Pensarlo como adjuncion entre dominio y schema. Drift aparece cuando el round-trip deja de aproximar identidad.

## Firma sugerida

```text
Subsistema: Lens | Coalgebra | Monada
Estados/Observaciones: ...
Persistencia: SQL | NoSQL | Mixto
API: REST | GraphQL | gRPC | Streams
Sustituibilidad: verificada | pendiente
```
