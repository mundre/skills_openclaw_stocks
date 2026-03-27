# Evolution Audit

Playbook para migraciones, versionado y auditoria de artefactos.

## Migracion como adjuncion

Modela el cambio entre esquemas con uno de estos operadores:

- `Delta`: reestructurar sin cambiar esencia
- `Sigma`: fusionar, generalizar o agregar
- `Pi`: restringir o especializar

Para cada migracion reporta:
- morfismo estructural
- operador elegido
- propiedades preservadas
- propiedades perdidas

## Categoria de versiones

Piensa las versiones como objetos y las migraciones como morfismos.

Auditar una cadena implica verificar:
- composicion valida
- preservacion de restricciones criticas
- deuda acumulada por perdida de estructura

## Modos de auditoria

### STATIC

Verifica:
- identidades
- composicion
- path equations
- referencias y foreign keys

### TEMPORAL

Verifica:
- cadena de migraciones
- constraint preservation
- debt estructural

### BEHAVIORAL

Verifica:
- conformancia de interfaz
- bisimulacion
- trazabilidad de acciones

### KB_GLOBAL

Verifica:
- referencias no colgantes
- URNs unicas
- grafo de dependencias sano

### DAL_INTEGRATED

Verifica:
- alineacion storage-model
- preservacion API-functor
- drift ORM
- conmutatividad de pipelines

## Severidades

- `CRITICAL`: invalida el artefacto
- `HIGH`: rompe integridad antes de produccion
- `MEDIUM`: suboptimo pero recuperable
- `LOW`: mejora incremental

## Patrones de correccion

- `BROKEN-DIAGRAM`
- `ORPHAN-OBJECT`
- `DANGLING-REF`
- `VERSION-MISMATCH`
- `NON-FUNCTORIAL`
- `REDUNDANT-BISIMILAR`

## Firma sugerida

```text
Modo: STATIC | TEMPORAL | BEHAVIORAL | KB_GLOBAL | DAL_INTEGRATED
Issues: ...
Patrones: ...
Migracion: Delta | Sigma | Pi | composicion
Riesgos: ...
```
