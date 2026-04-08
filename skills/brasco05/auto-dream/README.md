# 🌙 Auto Dream — Memory Consolidation

**Repliziert Anthropics Auto Dream Feature für OpenClaw und Claude Code.**

Dein Agent akkumuliert mit der Zeit Hunderte von Memory-Dateien, veraltete Fakten und widersprüchliche Einträge. Das Kontextfenster wird voll, die Qualität sinkt.

Auto Dream löst das — genau wie dein Gehirn nachts Erinnerungen konsolidiert.

---

## Was es macht

Ein 4-Phasen-Pass über alle Memory-Dateien:

| Phase | Was passiert |
|-------|-------------|
| 🔍 **Orient** | Verstehen was existiert — ls, Index lesen, Topic-Files überfliegen |
| 📡 **Gather** | Neue Signale sammeln — Tages-Logs, Nacht-Summary, Git-Commits |
| 🔀 **Merge** | In bestehende Files mergen, Widersprüche auflösen, Daten absolutieren |
| ✂️ **Prune** | Veraltetes raus, MEMORY.md unter 200 Zeilen halten |

## Wann triggert es

- Manuell: "führe einen dream durch"
- Nach langen Sessions
- Automatisch via daily-reflection Cron
- Wenn MEMORY.md > 180 Zeilen

## Basiert auf

Anthropics echtem Auto Dream System-Prompt aus Claude Code (entdeckt März 2026 via GitHub-Analyse der System-Prompts). Für OpenClaw-Workspace angepasst.

---

*by brasco05 · ClawhHub*
