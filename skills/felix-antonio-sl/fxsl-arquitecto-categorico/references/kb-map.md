# KB Map

Mapa de lectura del conocimiento ya condensado dentro del bundle. Carga solo el bloque relevante al problema.

## 1. Fundamentos de estructuras

Usar para modelado estatico, restricciones y representacion de schemas.

- `static-modeling.md`
  - schema como categoria
  - instancia como funtor a `Set`
  - restricciones como path equations
  - accion como primary key cuando la identidad es transicional

## 2. Comportamiento y sistemas

Usar para APIs stateful, eventos, observacion y sustituibilidad.

- `dynamic-modeling.md`
  - coalgebras
  - bisimulacion
  - equivalencia comportamental
  - lenses, monadas y DAL

## 3. Integracion multimodelo

Usar para fusion de fuentes, data lakes, traduccion entre modelos y query functorial.

- `integration-modeling.md`
  - CQL
  - migracion functorial
  - proveniencia
  - Grothendieck
  - multimodel wrappers

## 4. Evolucion y auditoria

Usar para diagnostico, versionado, debt estructural y drift.

- `evolution-audit.md`
  - categoria de versiones
  - Delta/Sigma/Pi
  - auditoria temporal
  - patrones de falla
  - formato de reporte

## 5. Meta-arquitectura

Usar para explicar por que los artefactos se tratan como estructuras composicionales.

- `static-modeling.md`
  - categorias, objetos, morfismos, limites y colimites
- `integration-modeling.md`
  - schema global, wrappers y query as functor
- `evolution-audit.md`
  - invariantes, cadena temporal y debt

## 6. Regla de Lectura

- Si el pedido es operativo, empieza por `engine-map.md` y luego baja al playbook minimo.
- Si el pedido es teorico, empieza por este mapa y carga solo 1 a 2 playbooks.
- Si el pedido es auditoria o migracion, prioriza `evolution-audit.md`.
