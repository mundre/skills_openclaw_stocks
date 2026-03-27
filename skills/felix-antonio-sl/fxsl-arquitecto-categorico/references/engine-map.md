# Engine Map

Usa este mapa para decidir que playbook interno cargar. El bundle ya incluye el contenido operativo; no requiere archivos externos.

## 1. Static

Usar cuando el objetivo es schema, DDL o estructura declarativa.

- Playbook: `static-modeling.md`
- Preguntas de colapso utiles:
  - entidad o evento
  - esquema relacional o documento
  - limite o colimite
- Artefactos tipicos:
  - PostgreSQL DDL
  - JSON Schema
  - GraphQL SDL
  - Prisma
  - Mermaid

## 2. Dynamic

Usar cuando hay estado, transiciones, observaciones o comportamiento de API.

- Playbook: `dynamic-modeling.md`
- Decide entre:
  - lens: lectura/escritura bidireccional
  - coalgebra: comportamiento reactivo o sustituibilidad
  - monada: efectos, fallo, no determinismo, estado

## 3. Integration

Usar cuando hay multiples fuentes, tenants, zonas de lake o esquemas heterogeneos.

- Playbook: `integration-modeling.md`
- Patrones principales:
  - construccion de Grothendieck `int F`
  - wrappers functoriales por fuente
  - query as functor
- Preguntas de colapso utiles:
  - federacion o esquema global
  - integridad estricta o flexibilidad
  - salida relacional, documental, grafo o flat

## 4. Audit

Usar cuando el usuario trae artefactos existentes y pide diagnostico, consistencia o mejoras.

- Playbook: `evolution-audit.md`
- Modos de auditoria:
  - `STATIC`
  - `TEMPORAL`
  - `BEHAVIORAL`
  - `KB_GLOBAL`
  - `DAL_INTEGRATED`
- Salida esperada:
  - issues por severidad
  - patron de correccion
  - mejora priorizada

## 5. Clarification

Usar cuando la solicitud es ambigua o faltan decisiones que afectan la forma del artefacto.

- Reglas incluidas en `static-modeling.md`, `dynamic-modeling.md` e `integration-modeling.md`
- Taxonomia:
  - `A1` ser
  - `A2` devenir
  - `A3` conocer
  - `A4` expresar
- Regla:
  - formular una pregunta socratica breve
  - no avanzar a emision estructural sin colapso suficiente

## 6. Migration

Usar cuando el cambio principal es entre versiones de esquema o de representacion.

- Playbook: `evolution-audit.md`
- Operadores:
  - `Delta`: reestructurar preservando forma
  - `Sigma`: fusionar o generalizar
  - `Pi`: restringir o especializar
- Reportar siempre:
  - que preserva
  - que pierde
  - riesgo de informacion
