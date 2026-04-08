---
name: essential-tools
description: Catalogue d'outils installables a la demande. Utilise quand l'utilisateur tape /tools ou quand tu as besoin d'un package non disponible.
version: 1.1.0
author: qapten
---

# Essential Tools

Catalogue d'outils pre-references et versionnes, installables a la demande par categorie ou individuellement.

## Contexte de securite

Ces packages s'executent dans un conteneur Docker isole (OpenClaw) avec des limites de ressources (memoire, CPU, PIDs) et un reseau Docker dedie. L'installation n'affecte que le conteneur de l'utilisateur, pas le systeme hote.

## Commande /tools

| Commande | Action |
|----------|--------|
| /tools | Afficher le catalogue des outils disponibles par categorie |
| /tools install \<categorie\> | Installer tous les packages d'une categorie |
| /tools install \<package\> | Installer un package specifique |
| /tools status | Voir les packages deja installes |

## Catalogue

### docs — Generation de documents

```bash
npm install pptxgenjs@3.12.0 docx@9.5.0 exceljs@4.4.0 pdfkit@0.16.0 pdf-parse@1.1.1 csv-parse@5.6.0 csv-stringify@6.5.2
pptxgenjs@3.12.0 — creer des presentations PowerPoint (.pptx)
docx@9.5.0 — creer des documents Word (.docx)
exceljs@4.4.0 — creer des tableurs Excel (.xlsx)
pdfkit@0.16.0 — generer des PDF
pdf-parse@1.1.1 — lire et extraire le texte de PDF existants
csv-parse@5.6.0 + csv-stringify@6.5.2 — lire/ecrire des CSV
images — Traitement d'images

npm install sharp@0.33.5 qrcode@1.5.4
sharp@0.33.5 — redimensionner, convertir, compresser des images
qrcode@1.5.4 — generer des QR codes
web — Scraping et veille

npm install cheerio@1.0.0 axios@1.7.9 rss-parser@3.13.0 xml2js@0.6.2
cheerio@1.0.0 — parser du HTML (scraping leger sans navigateur)
axios@1.7.9 — requetes HTTP robustes avec retry
rss-parser@3.13.0 — lire des flux RSS/Atom
xml2js@0.6.2 — parser du XML (BOAMP, TED, etc.)
utils — Utilitaires

npm install lodash@4.17.21 dayjs@1.11.13 archiver@7.0.1 json2csv@6.0.0-alpha.2 turndown@7.2.0 form-data@4.0.1
lodash@4.17.21 — manipulation avancee de donnees
dayjs@1.11.13 — dates, fuseaux horaires, formatage
archiver@7.0.1 — creer des archives ZIP
json2csv@6.0.0-alpha.2 — convertir JSON en CSV
turndown@7.2.0 — convertir HTML en Markdown
form-data@4.0.1 — upload multipart (envoi fichiers Telegram)
python — Outils Python

pip install pandas==2.2.3 matplotlib==3.10.0 openpyxl==3.1.5 requests==2.32.3 beautifulsoup4==4.12.3
pandas==2.2.3 — analyse et manipulation de donnees
matplotlib==3.10.0 — graphiques et visualisations
openpyxl==3.1.5 — lire/ecrire Excel depuis Python
requests==2.32.3 — requetes HTTP
beautifulsoup4==4.12.3 — parsing HTML depuis Python
Comportement
Installation a la demande
Quand l'utilisateur te demande une tache necessitant un package du catalogue :

Verifie si le package est deja installe (npm list <pkg> ou pip show <pkg>)
S'il manque, annonce : "J'installe [package]@[version] pour [raison]..." et attends une confirmation rapide de l'utilisateur avant de proceder
Une fois confirme, installe le package avec la version exacte specifiee dans ce catalogue
Execute la tache demandee
N'installe JAMAIS un package qui ne figure pas dans ce catalogue sans demander une confirmation explicite avec avertissement
Restrictions de securite
Versions fixees : installe TOUJOURS la version exacte listee dans ce catalogue (ex: npm install sharp@0.33.5, jamais npm install sharp)
Catalogue ferme : seuls les packages listes ci-dessus sont autorises en installation rapide. Tout autre package necessite une confirmation explicite avec avertissement sur le risque
Registres officiels uniquement : npm (registry.npmjs.org) et PyPI (pypi.org) exclusivement
Affichage du catalogue
Quand l'utilisateur tape /tools :

Affiche les categories avec une description courte de chaque outil
Indique lesquels sont deja installes (✅) ou non (⬚)
Skill cree le 7 avril 2026 par Qapten.