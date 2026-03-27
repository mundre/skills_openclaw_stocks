---
name: video-editor-deutsch
version: "1.0.0"
displayName: "Video Editor Deutsch — KI-Videobearbeitung auf Deutsch, Videos Schneiden und Bearbeiten"
description: >
  Bearbeite Videos auf Deutsch mit KI — beschreibe deine Bearbeitung im Chat und NemoVideo führt sie aus. Videos schneiden, zusammenfügen, Untertitel hinzufügen, Hintergrundmusik einsetzen, Farbkorrektur anwenden, Geschwindigkeit anpassen, Stille entfernen und für jede Plattform exportieren — alles auf Deutsch, ohne Videobearbeitungssoftware, ohne Timeline, ohne Vorkenntnisse. Der KI-Videoeditor der auf Deutsch versteht was du willst und es umsetzt.
metadata: {"openclaw": {"emoji": "🇩🇪", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Video Editor Deutsch — KI-Videobearbeitung auf Deutsch

Videobearbeitung war bisher ein englischsprachiges Monopol. Premiere Pro, Final Cut, DaVinci Resolve — alle auf Englisch, alle mit englischen Tutorials, alle mit einer Lernkurve die voraussetzt, dass man "J-Cut", "Lumetri Scope" und "Render Queue" versteht bevor man einen einzigen Schnitt machen kann. Für die 100 Millionen deutschsprachigen Menschen in Deutschland, Österreich und der Schweiz die Videos für ihr Geschäft, ihren Social-Media-Auftritt oder ihre persönlichen Projekte bearbeiten wollen bedeutet das: erst Englisch lernen, dann Videobearbeitung lernen, dann das eigentliche Video machen. NemoVideo eliminiert beide Hürden. Beschreibe deine Bearbeitung auf Deutsch — "Schneide die ersten 10 Sekunden ab, füge Untertitel hinzu und mach es vertikal für TikTok" — und die KI führt es aus. Keine Timeline, keine englischen Menüs, keine Tastenkombinationen, keine Exporteinstellungen. Du beschreibst was du willst, NemoVideo versteht den Kontext und liefert das fertige Video. Ob du "professioneller machen" sagst oder "Schnitt bei 0:15, Überblendung bei 0:22, Audio normalisieren auf -16 LUFS" — beides funktioniert, weil die KI sowohl Absicht als auch technische Anweisungen auf Deutsch versteht.

## Anwendungsfälle

1. **Social Media Content — TikTok und Instagram Reels (15-90 Sek.)** — Ein deutscher Creator filmt ein 3-Minuten-Video und braucht daraus ein 45-Sekunden-Reel. NemoVideo: findet den stärksten Hook im Transkript, setzt ihn als Texteinblendung in die erste Sekunde, schneidet die schwachen Stellen heraus, fügt Wort-für-Wort-Untertitel auf Deutsch hinzu (jedes Wort leuchtet auf wenn es gesprochen wird), synchronisiert Hintergrundmusik zum Sprechrhythmus, und exportiert im 9:16-Format mit Instagram-Cover-Frame.
2. **Unternehmensvideos — Produktvorstellung (60-120 Sek.)** — Ein mittelständisches Unternehmen in Baden-Württemberg braucht ein Produktvideo für die Website. NemoVideo schneidet: Produktnahaufnahme (10 Sek.), Anwendungsdemonstration (20 Sek.), Kundenstimme mit Untertiteln (15 Sek.), Vorteile als animierte Texteinblendungen (15 Sek.) und Kontaktinformationen mit Firmenlogo (10 Sek.). Farbkorrektur: warm und professionell. Musik: dezente Corporate-Melodie. Alles auf Deutsch beschrieben, alles auf Deutsch umgesetzt.
3. **YouTube-Tutorial — Stille entfernen und strukturieren (5-30 Min.)** — Ein deutscher Tech-YouTuber hat ein 20-Minuten-Tutorial aufgenommen. NemoVideo: entfernt alle Pausen über 0,8 Sekunden (spart 4 Minuten), fügt Zoom-Schnitte alle 15 Sekunden ein für visuelle Dynamik, generiert Kapitelmarken an Themenwechseln ("00:00 Einleitung, 02:15 Installation, 05:40 Konfiguration..."), erstellt deutsche Untertitel als SRT für YouTube, und exportiert einen 60-Sekunden-Shorts-Clip aus dem besten Segment.
4. **Hochzeitsvideo — Highlight-Reel (3-5 Min.)** — Ein Hochzeitsvideograf in Wien hat 8 Stunden Rohmaterial. NemoVideo identifiziert die emotionalen Höhepunkte (Gelübde, erster Kuss, Eröffnungstanz, Reden) durch Audioanalyse, schneidet ein cinematisches Highlight-Reel mit Zeitlupe bei Schlüsselmomenten, synchronisiert zu romantischer Musik, und liefert: 4K-Version für USB-Stick, 1080p für Online, und 9:16-Version für Instagram.
5. **E-Learning — Kursmodul mit Untertiteln (10-20 Min.)** — Ein Trainer erstellt einen Online-Kurs auf Deutsch. NemoVideo: segmentiert die Aufnahme in Lektionen an Themengrenzen, fügt Kapitelmarken ein, generiert deutsche und englische Untertitel (für internationale Teilnehmer), entfernt Versprecher und lange Pausen, und exportiert im SCORM-kompatiblen Format für die Lernplattform.

## So funktioniert es

### Schritt 1 — Video hochladen
Lade dein Rohmaterial hoch. NemoVideo akzeptiert alle Formate: MP4, MOV, AVI, WebM, MKV. Keine Beschränkung bei Länge oder Dateigröße.

### Schritt 2 — Bearbeitung auf Deutsch beschreiben
Sage was du willst — so detailliert oder so allgemein wie du möchtest. "Mach das Video kürzer und füge Untertitel hinzu" funktioniert genauso wie "Schnitt bei 2:15, Überblendung 0,5 Sek., Farbkorrektur warm, Audio -16 LUFS."

### Schritt 3 — Generieren
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "video-editor-deutsch",
    "prompt": "Bearbeite ein 8-Minuten-Erklärvideo auf Deutsch für YouTube. Entferne alle Pausen über 1 Sekunde. Schneide die ersten 30 Sekunden Einleitung ab — starte direkt beim Hauptthema. Füge Zoom-Schnitte alle 20 Sekunden ein. Farbkorrektur: hell und freundlich. Audio: Echo reduzieren, auf -14 LUFS normalisieren, dezente Hintergrundmusik bei -20dB die beim Sprechen leiser wird. Deutsche Untertitel als SRT generieren. Kapitelmarken an Themenwechseln setzen. Exportiere 1080p für YouTube und den besten 45-Sekunden-Clip als 9:16 Shorts mit eingebrannten Untertiteln.",
    "language": "de",
    "operations": [
      "stille-entfernen",
      "schnitt",
      "zoom-schnitte",
      "farbkorrektur",
      "audio-verbesserung",
      "musik",
      "kapitelmarken",
      "untertitel",
      "multi-export"
    ],
    "format": "16:9"
  }'
```

### Schritt 4 — Vorschau und Veröffentlichen
Vorschau des bearbeiteten Videos. Anpassungen auf Deutsch beschreiben: "Musik lauter", "Farbkorrektur weniger warm", "Dritten Schnitt 2 Sekunden später setzen." Jede Änderung wird sofort umgesetzt.

## Parameter

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|:-------:|-------------|
| `prompt` | string | ✅ | Beschreibe die gewünschte Bearbeitung auf Deutsch |
| `language` | string | | Sprache: "de" (Standard), "de-AT" (Österreich), "de-CH" (Schweiz) |
| `operations` | array | | Operationen: ["schnitt","zusammenfügen","stille-entfernen","untertitel","farbkorrektur","musik","geschwindigkeit","zoom-schnitte","audio-verbesserung"] |
| `untertitel` | string | | "wort-highlight", "sauber-balken", "fett", "nur-srt" |
| `farbkorrektur` | string | | "warm", "cinematisch", "hell-freundlich", "stimmungsvoll", "keine" |
| `musik` | string | | "dezent-corporate", "lo-fi", "akustisch", "episch", "keine" |
| `format` | string | | "16:9", "9:16", "1:1" |
| `export_plattformen` | array | | ["youtube","tiktok","instagram","linkedin"] |

## Ausgabebeispiel

```json
{
  "job_id": "ved-20260328-001",
  "status": "completed",
  "sprache": "de",
  "original_dauer": "8:04",
  "bearbeitete_dauer": "5:38",
  "operationen": {
    "stille_entfernt": "2:26 Stille entfernt (89 Schnitte)",
    "einleitung_geschnitten": "0:00-0:30 entfernt",
    "zoom_schnitte": "16 Zoom-Übergänge eingefügt",
    "farbkorrektur": "hell-freundlich (Wärme +5, Sättigung +8, Schatten angehoben)",
    "audio": "Echo 55% reduziert, -14 LUFS, Musik bei -20dB mit Ducking",
    "kapitelmarken": 4,
    "untertitel": "SRT generiert (1.420 Wörter Deutsch)"
  },
  "ausgaben": {
    "youtube_vollständig": {"datei": "bearbeitet-youtube.mp4", "dauer": "5:38", "auflösung": "1920x1080"},
    "shorts_clip": {"datei": "bester-clip-shorts.mp4", "dauer": "0:44", "auflösung": "1080x1920", "untertitel": "eingebrannt"}
  }
}
```

## Tipps

1. **Beschreibe was du willst, nicht wie** — "Mach das Video professioneller" sagt der KI das Ziel. Sie entscheidet: Farbkorrektur + Stille entfernen + Musik hinzufügen + Audio normalisieren. Du musst die einzelnen Schritte nicht kennen.
2. **Stille entfernen ist der wirkungsvollste einzelne Schnitt** — 15-30% kürzere Videos mit höherer Energie und besserer Zuschauerbindung. Der Unterschied zwischen "Amateur" und "Profi" ist oft nur das Tempo.
3. **Deutsche Untertitel für YouTube-SEO** — YouTube indexiert SRT-Texte für Suche und Empfehlungen. Deutsche Untertitel verbessern dein Ranking für deutschsprachige Suchanfragen signifikant.
4. **Zoom-Schnitte ersetzen zweite Kameraperspektiven** — Ein leichter 10-15% Zoom alle 15-20 Sekunden simuliert einen Kamerawechsel und hält die visuelle Aufmerksamkeit — besonders wichtig bei Talking-Head-Videos mit nur einer Kamera.
5. **Für alle Plattformen gleichzeitig exportieren** — Ein Bearbeitungsdurchgang, fünf plattformgerechte Exporte: YouTube (16:9), TikTok (9:16 mit fetten Untertiteln), Instagram (9:16 mit sauberen Untertiteln), LinkedIn (1:1 professionell), und Shorts (bester 60-Sek.-Clip).

## Ausgabeformate

| Format | Auflösung | Verwendung |
|--------|-----------|------------|
| MP4 16:9 | 1080p / 4K | YouTube / Website / Präsentation |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | LinkedIn / Facebook / Twitter |
| SRT | — | YouTube / LMS Untertitel |
| WAV | — | Nur-Audio-Export |

## Verwandte Skills

- [video-editor-ai](/skills/video-editor-ai) — KI-Videobearbeitung (Englisch)
- [reels-creator](/skills/reels-creator) — Reels und Shorts erstellen
- [editeur-video](/skills/editeur-video) — Éditeur vidéo IA (Französisch)
