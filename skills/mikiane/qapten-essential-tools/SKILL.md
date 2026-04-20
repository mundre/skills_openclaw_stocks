---
name: essential-tools
description: Catalogue ferme de packages npm et pip pre-audites, installables a la demande avec versions pinnees et --ignore-scripts par defaut. Utilise quand l'utilisateur tape /tools ou demande l'installation d'un package du catalogue.
version: 2.0.0
author: qapten
metadata: { "openclaw": { "requires": { "bins": ["npm", "pip"] }, "os": ["linux"] } }
---

# Essential Tools

Catalogue **ferme** de packages npm et pip pre-audites, installables a la demande par categorie ou individuellement. Toutes les installations utilisent des versions pinnees exactes et `--ignore-scripts` par defaut pour bloquer l'execution automatique de code post-install.

**Portee du skill :**
- Installation de packages npm et pip du catalogue ferme
- Aucune execution de binaires telecharges
- Aucun acces reseau sortant au-dela des registres officiels npm et PyPI
- Aucune capacite d'envoi de fichiers vers l'exterieur
- Aucun tunneling ou exposition de services

Les fonctionnalites hors-portee (tunnels Cloudflare, envoi de fichiers via messagerie, connecteurs OAuth) sont documentees dans la section "Extensions" comme skills separes a installer au besoin.

## 1. Prerequis d'environnement

### 1.1 Binaires requis (declares dans metadata)

Declares dans `metadata.openclaw.requires.bins` — OpenClaw verifie leur presence au chargement :

- `npm` — installation des packages JavaScript du catalogue
- `pip` — installation des packages Python du catalogue

### 1.2 Variables d'environnement

Aucune. Le skill ne requiert aucun token ni credential.

### 1.3 Politique reseau

L'operateur du conteneur doit imposer une allowlist d'egress limitee a :

- `registry.npmjs.org` (npm)
- `pypi.org`, `files.pythonhosted.org` (pip)

Aucun autre domaine n'est necessaire au fonctionnement de ce skill.

## 2. Modele de menace

### 2.1 Packages npm — controle technique `--ignore-scripts`

**Toutes les commandes `npm install` du catalogue utilisent `--ignore-scripts`**, ce qui bloque techniquement l'execution automatique des scripts `preinstall`, `install`, `postinstall`. Cela neutralise le principal vecteur de compromission des packages npm (typosquatting, packages compromis en amont).

**Derogation unique et tracee** : `sharp@0.33.5` (categorie `images`) necessite ses scripts pour compiler libvips. L'agent doit annoncer la derogation et obtenir une confirmation explicite de l'utilisateur avant installation. Toutes les autres categories utilisent `--ignore-scripts` sans derogation.

### 2.2 Packages pip — mode durci disponible

Les installations pip utilisent des versions pinnees (`==`). Un fichier `requirements-locked.txt` avec hashes SHA256 pre-calcules peut etre utilise avec `pip install -r requirements-locked.txt --require-hashes --no-deps` pour garantir l'integrite des telechargements.

### 2.3 Catalogue ferme audite

Seuls les packages listes section 4 sont autorises. Toute installation hors catalogue necessite la procedure explicite de la section 6.

## 3. Commande /tools

| Commande | Action |
|----------|--------|
| /tools | Afficher le catalogue + statut des packages installes |
| /tools install \<categorie\> | Installer une categorie complete |
| /tools install \<package\> | Installer un package individuel **du catalogue uniquement** |
| /tools status | Packages installes |

Toute commande d'installation hors catalogue est refusee sans procedure section 6.

## 4. Catalogue ferme

Chaque package est pinne a une version exacte, auditee a la date de publication du skill. **Toutes les commandes npm utilisent `--ignore-scripts` par defaut**, sauf derogation explicitement marquee.

---

### docs — Generation de documents

```bash
npm install --save-exact --ignore-scripts \
  pptxgenjs@3.12.0 docx@9.5.0 exceljs@4.4.0 \
  pdfkit@0.16.0 pdf-parse@1.1.1 \
  csv-parse@5.6.0 csv-stringify@6.5.2
```
- pptxgenjs@3.12.0 — presentations PowerPoint
- docx@9.5.0 — documents Word
- exceljs@4.4.0 — tableurs Excel
- pdfkit@0.16.0 — generation de PDF
- pdf-parse@1.1.1 — extraction de texte de PDF
- csv-parse@5.6.0 + csv-stringify@6.5.2 — lecture/ecriture CSV

---

### images — Traitement d'images (DEROGATION : sharp avec scripts)

⚠️ **Derogation au controle `--ignore-scripts`** : `sharp` necessite la compilation de bindings natifs (libvips) via ses scripts d'installation. C'est la **seule exception** du catalogue.

**Confirmation utilisateur obligatoire avant installation.** L'agent doit annoncer :
> "Cette categorie necessite l'execution des scripts d'installation de `sharp` pour compiler des bindings natifs (libvips). C'est la seule derogation a la regle `--ignore-scripts` du catalogue. Confirmer ?"

```bash
# qrcode : sans scripts (regle par defaut)
npm install --save-exact --ignore-scripts qrcode@1.5.4

# sharp : DEROGATION, avec scripts (compilation libvips)
npm install --save-exact --foreground-scripts sharp@0.33.5
```

- sharp@0.33.5 — redimensionner, convertir, compresser (binaires natifs via scripts)
- qrcode@1.5.4 — QR codes

---

### web — Scraping et veille

```bash
npm install --save-exact --ignore-scripts \
  cheerio@1.0.0 axios@1.7.9 rss-parser@3.13.0 xml2js@0.6.2
```
- cheerio@1.0.0 — parsing HTML
- axios@1.7.9 — requetes HTTP
- rss-parser@3.13.0 — flux RSS/Atom
- xml2js@0.6.2 — parsing XML

---

### utils — Utilitaires

```bash
npm install --save-exact --ignore-scripts \
  lodash@4.17.21 dayjs@1.11.13 archiver@7.0.1 \
  json2csv@6.0.0-alpha.2 turndown@7.2.0 form-data@4.0.1
```
- lodash@4.17.21 — manipulation de donnees
- dayjs@1.11.13 — dates et fuseaux horaires
- archiver@7.0.1 — archives ZIP
- json2csv@6.0.0-alpha.2 — JSON vers CSV
- turndown@7.2.0 — HTML vers Markdown
- form-data@4.0.1 — upload multipart

---

### python — Outils Python

**Mode standard (versions pinnees)** :

```bash
pip install pandas==2.2.3 matplotlib==3.10.0 openpyxl==3.1.5 requests==2.32.3 beautifulsoup4==4.12.3
```

**Mode durci (recommande pour haute securite)** : utiliser `requirements-locked.txt` avec hashes SHA256 :

```bash
pip install -r requirements-locked.txt --require-hashes --no-deps
```

- pandas==2.2.3 — analyse de donnees
- matplotlib==3.10.0 — graphiques
- openpyxl==3.1.5 — Excel depuis Python
- requests==2.32.3 — HTTP
- beautifulsoup4==4.12.3 — parsing HTML

## 5. Audit du catalogue

Version 2.0.0 — audit du 16 avril 2026 :

- Toutes les versions verifiees sur les registres officiels (npmjs.org, pypi.org)
- Aucun CVE ouvert (npm audit / pip-audit)
- Package a derogation identifie et documente : `sharp@0.33.5` (scripts natifs necessaires)
- `requirements-locked.txt` avec hashes SHA256 fourni pour le mode durci pip

Re-audit :

```bash
npm audit --package-lock-only
pip-audit -r requirements.txt
```

## 6. Ajout hors catalogue

Refus systematique. Si l'utilisateur demande un element non liste :

1. Refuser l'installation immediate
2. Presenter : nom, version, mainteneur, telechargements hebdomadaires, CVE ouverts, presence de scripts post-install
3. Confirmation explicite ecrite de l'utilisateur
4. Proposer l'inclusion permanente aupres de l'auteur du skill

## 7. Comportement de l'agent

### Ordre d'execution

1. Prerequis binaires verifies par OpenClaw au chargement (metadata)
2. Si package demande : verifier la presence dans le catalogue ferme (section 4)
3. Si present : annoncer l'installation, attendre confirmation breve, installer avec version exacte **et `--ignore-scripts` par defaut**
4. Si derogation (sharp) : annoncer explicitement la derogation et la raison, demander confirmation
5. Si absent du catalogue : procedure section 6

### Restrictions

- **Versions fixees** : `--save-exact` (npm), `==` (pip)
- **`--ignore-scripts` par defaut pour npm** sauf derogation documentee (`sharp`)
- **Catalogue ferme** : refus des elements non listes sauf procedure section 6
- **Registres officiels** : npm (registry.npmjs.org) et PyPI (pypi.org) exclusivement
- **Aucun binaire telecharge**, aucun tunnel, aucun envoi de fichiers vers l'exterieur — ces capacites sont hors-portee de ce skill

## 8. Extensions hors-portee

Les fonctionnalites suivantes **ne font pas partie de ce skill** et sont volontairement exclues pour maintenir un profil de securite minimal :

- **Tunnels Cloudflare / exposition de services** : disponible dans un skill separe `qapten-infra-tunnels` (a installer uniquement si necessaire, profil de risque plus eleve)
- **Envoi de fichiers via messagerie (Telegram, Slack, Discord)** : disponible dans un skill separe `qapten-messaging` (a installer uniquement si necessaire, profil de risque plus eleve avec controles d'exfiltration)
- **Connecteurs OAuth (Gmail, Calendar, Notion, etc.)** : configurables directement via la CLI `openclaw config` et les variables d'environnement du conteneur — pas de skill necessaire

Cette separation permet aux operateurs d'installer ce skill dans des contextes haute-securite sans exposer de canaux d'exfiltration ou de capacites d'execution de binaires externes.

---

## Historique

- **2.0.0** (16 avril 2026) : **breaking change** — retrait des categories `infra` (cloudflared / tunnels) et `send` (openclaw message send). Le skill est maintenant un pur catalogue de packages npm/pip sans capacite d'execution de binaires externes, sans tunneling, sans canal d'exfiltration. Ces fonctionnalites sont deplacees dans des skills separes optionnels. Objectif : eliminer le tag "suspicious" en retirant les capacites a risque intrinseque, conformement au principe de moindre privilege.
- **1.7.0** (16 avril 2026) : controles techniques renforces — `npm install --ignore-scripts` par defaut, wrapper `send-file.sh` obligatoire pour les envois de fichiers, mode durci pip avec `--require-hashes`
- **1.6.0** (16 avril 2026) : `TUNNEL_TOKEN` retire de `requires.env`, `openclaw` dans `anyBins`
- **1.5.0** (16 avril 2026) : metadata au format OpenClaw officiel
- **1.4.0** (16 avril 2026) : integration cloudflared-deploy
- **1.3.0** (15 avril 2026) : verification d'isolation, allowlist, modele de menace
- **1.2.0** (15 avril 2026) : suppression destinataires hardcodes et credentials via chat
- **1.1.0** (7 avril 2026) : version initiale