---
name: auto-dream
description: "Memory consolidation skill that replicates Anthropic's Auto Dream feature. Runs a 4-phase reflective pass over memory files: Orient → Gather → Merge → Prune. Use when: (1) Context window feels cluttered with stale info, (2) After long coding sessions, (3) Manually triggered with /dream, (4) Automatically after daily-reflection. Keeps memories tight, removes contradictions, converts relative dates to absolute."
metadata:
  openclaw:
    emoji: 🌙
    requires: {}
---

# Auto Dream — Memory Consolidation

Repliziert Anthropics Auto Dream Feature für OpenClaw. Führt einen 4-Phasen-Pass über alle Memory-Dateien durch und konsolidiert sie effizient.

## Wann ausführen

- Nach langen Sessions (Kontext fühlt sich voll an)
- Manuell: "führe einen dream durch" / "konsolidiere memory"  
- Automatisch: Wird vom daily-reflection Skill aufgerufen
- Nach Claude Code Sessions die viele Memory-Dateien erzeugt haben

## Die 4 Phasen

### Phase 1 — Orient
```
ls memory/
cat memory/morning-briefing.md (Index)
Skim alle topic files → verstehen was existiert
```
Ziel: Verstehen was da ist, Duplikate erkennen bevor sie entstehen.

### Phase 2 — Gather Signal
Quellen in Prioritäts-Reihenfolge:
1. Heutige Tages-Datei: `memory/YYYY-MM-DD.md` (append-only Stream)
2. Nacht-Summary: `memory/nacht-summary.md`
3. Session-Ende: `memory/session-ende-DATUM.md`
4. Alte Memories die mit aktuellem Codebase-Stand widersprechen
5. Bei Bedarf: `git log --oneline -20` für aktuelle Commits

**Nicht:** Session-Transcripts exhaustiv lesen. Nur gezielt grep wenn nötig.

### Phase 3 — Merge
Für jedes neue Signal das es wert ist gespeichert zu werden:
- In bestehende Topic-Dateien mergen, NICHT neue Duplikate anlegen
- Relative Daten ("gestern", "letzte Woche") → absolute Daten (2026-04-02)
- Widersprüche auflösen: wenn neue Info alte widerlegt → alte korrigieren/löschen
- Fakten-Updates: gelöste Tasks als ✅ markieren, offene aktualisieren

**In MEMORY.md schreiben:**
- Neue Projekte, Entscheidungen, Tech-Learnings
- Erledigte Tasks → in ~~durchgestrichen~~ oder raus
- Maximal ~200 Zeilen — es ist ein Index, kein Dump
- Jeder Eintrag: eine Zeile unter 150 Zeichen

### Phase 4 — Prune
MEMORY.md auf Stand bringen:
- Einträge über gelöste Bugs/Tasks entfernen oder als ✅ markieren
- Veraltete Infos (>30 Tage, nicht mehr relevant) raus
- Widersprüchliche Einträge: das falsche fixen
- Index-Einträge über 200 Zeichen → Detail in Topic-Datei auslagern, Zeile kürzen
- Ziel: MEMORY.md bleibt unter 200 Zeilen und unter ~25KB

## Output

Am Ende: **Kurze Summary** was konsolidiert, geupdatet oder gepruned wurde.
Format:
```
🌙 Dream abgeschlossen
✅ Merged: [X neue Infos in bestehende Files]
🗑️ Pruned: [X veraltete Einträge entfernt]  
🔧 Fixed: [X Widersprüche aufgelöst]
📝 MEMORY.md: [vorher] → [nachher] Zeilen
```

Wenn nichts geändert wurde: "Memories sind bereits tight — nichts zu tun."

## Regeln

- **Nicht exhaustiv lesen** — gezielt scrollen, nicht alles lesen
- **Merge statt create** — bestehende Dateien verbessern, keine Duplikate
- **Absolute Daten** — "gestern" ist nach 3 Tagen wertlos
- **Index bleibt Index** — MEMORY.md ist Navigation, kein Content-Dump
- **Secrets niemals** — keine Tokens, Keys, Passwörter in Memory
- **Idempotent** — zweimaliges Ausführen ändert nichts wenn nichts neu ist

## Integration mit daily-reflection

Der daily-reflection Skill ruft am Ende diesen Skill auf.
Reihenfolge: daily-reflection → auto-dream → morning-briefing schreiben.

## Trigger-Logik (für Cron)

Automatisch triggern wenn:
- `wc -l memory/YYYY-MM-DD.md` > 100 Zeilen (viele Aktivitäten)
- `wc -l MEMORY.md` > 180 Zeilen (fast voll)
- Nach Claude Code Sessions > 30 Minuten
