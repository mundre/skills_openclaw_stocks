---
name: google-dorks
description: Structured Google dorking protocol for OSINT investigations. Teaches agents to construct targeted search queries using operators for document discovery, identity research, corporate intel, exposed credentials, email harvesting, legal records, video and podcast appearances, webinar and conference activity, court and legislative hearing recordings, cached content, breach data, and surveillance infrastructure. Use instead of naive keyword searches for any investigation task.
---

# Google Dork Query Protocol

## When to Use This Skill
Use structured dork queries instead of plain keyword searches for ANY of:
- Finding a subject's social media profiles or accounts
- Locating documents (PDFs, spreadsheets, court filings) tied to a person or company
- Discovering email addresses, usernames, or handles
- Finding cached or deleted content
- Mapping exposed credentials, configs, or sensitive files on a target domain
- Finding video appearances, podcast interviews, webinar recordings, conference talks
- Locating court hearing recordings, legislative testimony, administrative proceedings
- Locating surveillance infrastructure (camera feeds) when Signals tools return no results

Never run a plain `FirstName LastName` search when a dorked query returns
higher-signal results. Dorks are the first tool. Sherlock and Spiderfoot are
complementary — use them in parallel or as follow-up.

---

## Two-Track Execution

### Track 1 — web_search (always try first)
Operators supported by Brave Search via web_search:
- `site:` — restrict to a domain
- `inurl:` — match URL substring
- `intitle:` — match page title
- `intext:` — match page body text
- `"exact phrase"` — exact string match
- `filetype:` / `ext:` — file type filter
- `-term` — exclude term or site
- `OR` / `|` — boolean OR
- `*` — wildcard

### Track 2 — browser + Google (when Track 1 returns < 3 useful results)
Navigate to https://www.google.com and enter the full dork string.
Required for:
- `cache:` — Google cached page versions
- `related:` — similar sites
- `AROUND(n)` — proximity operator
- `before:` / `after:` — date range filtering
- Complex multi-operator strings that Brave strips or mishandles

---

## Dork Templates by Category

### 1. Social Media — Profile Discovery
"FirstName LastName" site:linkedin.com
"FirstName LastName" site:twitter.com OR site:x.com
"FirstName LastName" site:facebook.com
"FirstName LastName" site:instagram.com
"FirstName LastName" site:tiktok.com
"FirstName LastName" site:reddit.com
"username" site:reddit.com/user/
"username" site:github.com
"username" site:twitch.tv
"username" site:youtube.com
"FirstName LastName" (site:twitter.com OR site:x.com OR site:instagram.com OR site:facebook.com OR site:tiktok.com)
"FirstName LastName" site:about.me OR site:linktr.ee
"FirstName LastName" site:medium.com OR site:substack.com
"FirstName LastName" site:patreon.com
"FirstName LastName" site:onlyfans.com
"username" (site:tumblr.com OR site:wordpress.com OR site:blogger.com)

### 2. Dating Platform Discovery
"username" site:tinder.com OR site:bumble.com OR site:hinge.co
"username" site:pof.com OR site:match.com OR site:okcupid.com
"FirstName LastName" site:match.com
"email@domain.com" site:pof.com
"username" site:zoosk.com OR site:eharmony.com
"username" site:seeking.com OR site:sugardaddie.com
"username" (site:fetlife.com OR site:kink.com)
"FirstName LastName" inurl:profile (site:pof.com OR site:okcupid.com)

### 3. People Search & Identity
"FirstName LastName" site:whitepages.com
"FirstName LastName" site:spokeo.com
"FirstName LastName" site:beenverified.com
"FirstName LastName" site:intelius.com
"FirstName LastName" site:peoplefinder.com OR site:radaris.com
"FirstName LastName" site:fastpeoplesearch.com OR site:truepeoplesearch.com
"FirstName LastName" "city, state"
"FirstName LastName" "DOB" OR "born" OR "age"
"FirstName LastName" "phone" OR "address" OR "email"
"FirstName LastName" site:addresses.com OR site:addresssearch.com
"FirstName LastName" site:411.com OR site:anywho.com
"FirstName LastName" (resume OR CV OR curriculum) filetype:pdf
"FirstName LastName" site:legacy.com OR site:findagrave.com
"FirstName LastName" site:classmates.com OR site:reunion.com

### 4. Username & Handle Hunting
"username" -site:twitter.com -site:x.com -site:instagram.com -site:facebook.com
inurl:"username" site:reddit.com
"username" site:github.com
"username" (forum OR board OR community OR member OR profile OR user)
"username" site:deviantart.com OR site:artstation.com
"username" site:soundcloud.com OR site:bandcamp.com
"username" site:steamcommunity.com
"username" site:last.fm OR site:rateyourmusic.com
"username" site:letterboxd.com OR site:goodreads.com
"username" site:chess.com OR site:lichess.org
"username" inurl:profile (gaming OR forum OR community)

### 5. Document & File Discovery
"FirstName LastName" filetype:pdf
"FirstName LastName" filetype:pdf (resume OR CV OR bio OR biography)
"Company Name" filetype:pdf (contract OR agreement OR NDA OR proposal)
"Company Name" filetype:xlsx OR filetype:csv
"Company Name" filetype:pdf (invoice OR statement OR financial)
"subject name" filetype:pdf site:gov
site:domain.com filetype:pdf
site:domain.com filetype:xlsx OR filetype:csv OR filetype:docx
site:domain.com ext:(doc | pdf | xls | txt | ppt)
"Company Name" filetype:pdf (board OR directors OR officers OR annual)
intitle:"index of" (pdf OR xls OR doc OR csv) "FirstName LastName"
ext:(doc | pdf | xls | txt | rtf | odt | ppt | pps) intext:"confidential" site:domain.com

### 6. Court Records & Legal Filings
"FirstName LastName" site:pacer.gov OR site:courtlistener.com
"FirstName LastName" site:unicourt.com OR site:judyrecords.com
"FirstName LastName" (lawsuit OR litigation OR settlement OR plaintiff OR defendant)
"FirstName LastName" site:courtlistener.com (criminal OR civil OR bankruptcy)
"Company Name" site:sec.gov (filing OR 10-K OR 8-K OR lawsuit)
"Company Name" site:courtlistener.com
"FirstName LastName" (arrest OR mugshot OR conviction OR felony OR misdemeanor)
"FirstName LastName" site:vinelink.com OR site:inmatelocator.com
"FirstName LastName" filetype:pdf site:court OR site:judiciary
"Company Name" (complaint OR injunction OR restraining) filetype:pdf

### 7. Court & Legislative Hearing Recordings
"FirstName LastName" site:c-span.org
"FirstName LastName" (testimony OR hearing OR deposition) site:youtube.com
"FirstName LastName" (testimony OR statement OR appearance) site:c-span.org
"FirstName LastName" site:congress.gov (hearing OR testimony OR committee)
"FirstName LastName" (committee hearing OR subcommittee) site:youtube.com
"FirstName LastName" (congressional testimony OR senate hearing OR house hearing)
"FirstName LastName" site:lawandcrime.com OR site:courttv.com
"FirstName LastName" (trial OR deposition OR proceeding) site:youtube.com
"FirstName LastName" (city council OR county commission OR zoning) site:youtube.com
"FirstName LastName" site:archive.org (hearing OR testimony OR trial OR proceeding)
"FirstName LastName" (FTC OR SEC OR FDA OR NLRB OR EEOC) (hearing OR proceeding OR testimony)
"FirstName LastName" (state legislature OR state assembly OR state senate) (testimony OR hearing)
"Company Name" (FTC OR SEC OR FDA) (hearing OR investigation OR proceeding) site:youtube.com
"FirstName LastName" intitle:(deposition OR testimony OR hearing) site:youtube.com
"FirstName LastName" site:regulations.gov (comment OR testimony OR submission)

### 8. Video Appearances
"FirstName LastName" site:youtube.com
"FirstName LastName" site:vimeo.com
"FirstName LastName" site:rumble.com OR site:odysee.com OR site:bitchute.com
"FirstName LastName" (interview OR appearance OR speech) site:youtube.com
"FirstName LastName" site:ted.com OR inurl:tedx site:youtube.com
"FirstName LastName" inurl:watch (site:youtube.com OR site:vimeo.com)
"Company Name" (earnings call OR investor day OR conference) site:youtube.com
"FirstName LastName" site:dailymotion.com
"FirstName LastName" site:c-span.org

### 9. Podcast Appearances
"FirstName LastName" site:podcasts.apple.com
"FirstName LastName" site:open.spotify.com/episode
"FirstName LastName" site:podchaser.com
"FirstName LastName" site:listennotes.com
"FirstName LastName" (podcast OR episode OR interview) filetype:mp3
"FirstName LastName" inurl:episode (podcast OR interview)
"FirstName LastName" site:buzzsprout.com OR site:anchor.fm OR site:podbean.com
"FirstName LastName" (guest OR interviewed OR featured) (podcast OR show OR episode)
"Company Name" site:listennotes.com OR site:podchaser.com

### 10. Webinars, Conferences & Speaking
"FirstName LastName" (keynote OR speaker OR panelist OR presenter OR moderator)
"FirstName LastName" site:slideshare.net OR site:speakerdeck.com
"FirstName LastName" site:eventbrite.com
"FirstName LastName" site:speakerhub.com OR site:sessionize.com
"FirstName LastName" (webinar OR online event OR virtual summit) site:youtube.com
"FirstName LastName" site:loom.com OR site:crowdcast.io
"FirstName LastName" site:linkedin.com/events
"FirstName LastName" (conference OR summit OR symposium OR forum) (speaker OR presenter OR panelist)
"FirstName LastName" (slides OR deck OR presentation) filetype:pdf (conference OR summit)
"FirstName LastName" site:ted.com
"FirstName LastName" (talk OR lecture OR workshop) site:youtube.com OR site:vimeo.com
"Company Name" (investor day OR analyst day OR earnings call) site:youtube.com
"FirstName LastName" inurl:speaker (conference OR summit OR event)

### 11. Corporate & Business Intel
"Company Name" site:opencorporates.com
"Company Name" site:bizapedia.com OR site:corporationwiki.com
"Company Name" site:glassdoor.com
"Company Name" site:linkedin.com (employees OR staff OR director OR CEO)
"Company Name" 990 filetype:pdf site:guidestar.org
"Company Name" site:dnb.com OR site:manta.com
"Company Name" (revenue OR funding OR valuation OR acquisition)
"Company Name" site:crunchbase.com OR site:pitchbook.com
"Company Name" (data breach OR hack OR leak OR security incident)
site:domain.com inurl:admin OR inurl:login OR inurl:portal
site:domain.com inurl:staff OR inurl:team OR inurl:about

### 12. Email Address Discovery
"firstname.lastname@domain.com"
"@domain.com" "FirstName LastName"
"@domain.com" filetype:pdf OR filetype:xlsx
"FirstName LastName" "contact" OR "email" OR "reach" -site:linkedin.com
intext:"@domain.com" site:domain.com filetype:pdf
"email" "FirstName LastName" (site:pastebin.com OR site:ghostbin.com)
"@gmail.com" OR "@yahoo.com" "FirstName LastName" filetype:pdf
site:domain.com intext:email filetype:txt OR filetype:csv
"FirstName LastName" intext:"email me" OR "contact me" OR "reach me at"
intitle:"index of" filetype:xls inurl:email

### 13. Breach & Paste Site Discovery
"email@domain.com" site:haveibeenpwned.com
"email@domain.com" (site:pastebin.com OR site:ghostbin.com OR site:rentry.co)
"FirstName LastName" site:pastebin.com
"username" (paste OR leak OR breach OR dump OR database)
"@domain.com" site:pastebin.com
"domain.com" (leak OR breach OR dump OR password) filetype:txt
"username" site:dehashed.com OR site:leakcheck.io
intext:"password" intext:"username" site:pastebin.com "domain.com"

### 14. Exposed Credentials & Sensitive Files (Legitimate Recon)
site:domain.com filetype:log
site:domain.com filetype:env
site:domain.com filetype:cfg OR filetype:conf
site:domain.com filetype:bak OR filetype:backup
site:domain.com inurl:config OR inurl:configuration
site:domain.com "Index of /" (password OR passwd OR credentials)
site:domain.com filetype:sql
site:domain.com ext:pem OR ext:key -intitle:index.of
filetype:log inurl:"password.log" site:domain.com
intext:"Index of /backup" site:domain.com
intext:"not for distribution" OR "confidential" filetype:pdf site:domain.com
"Index of /" +passwd site:domain.com
filetype:xls inurl:email site:domain.com
filetype:csv inurl:password site:domain.com
intitle:"index of" ".env" site:domain.com
intext:"DB_PASSWORD" OR intext:"DB_USER" filetype:env

### 15. Phone & Address Records
"phone number" "FirstName LastName" site:whitepages.com
"555-555-5555" (name OR address OR owner)
"FirstName LastName" "address" site:spokeo.com OR site:radaris.com
intitle:"reverse phone" "555-555-5555"
"FirstName LastName" site:411.com OR site:yellowpages.com
"555-555-5555" site:truecaller.com OR site:spydialer.com
"FirstName LastName" (moved OR relocated OR "new address" OR "forwarding address")

### 16. News & Media Archives
"FirstName LastName" site:newspapers.com OR site:genealogybank.com
"FirstName LastName" (news OR article OR interview OR mention) -site:linkedin.com
"FirstName LastName" site:legacy.com (obituary OR memorial)
"Company Name" site:sec.gov/cgi-bin/browse-edgar
"FirstName LastName" intitle:(arrested OR charged OR convicted OR sentenced)
"FirstName LastName" (press release OR announcement) filetype:pdf

### 17. Camera & Surveillance (Signals Fallback)
Use ONLY when Signals tools (signals-search.py, AISstream, OpenSky,
OpenCelliD, Wigle) return no results or encounter API errors.
intitle:"Live View / - AXIS" inurl:/view/view.shtml
inurl:/view.shtml intitle:"Live View"
intitle:"Toshiba Network Camera" user login
intitle:"i-Catcher Console - Web Monitor"
inurl:ViewerFrame?Mode=
inurl:videostream.cgi
inurl:webcam inurl:view
intitle:"webcam" inurl:view
inurl:/mjpg/video.mjpg
intitle:"Live NetSnap Cam-Server feed"
inurl:"MultiCameraFrame?Mode=" OR inurl:"MultiCameraFrame?Folder="
intitle:"WJ-NT104 Main Page"
inurl:LvAppl intitle:liveapplet
intitle:"snc-rz30 home"
"Active Webcam Page" inurl:8080
inurl:CgiStart?page=Single
inurl:/control/userimage.html
intitle:"Axis 2.x" OR intitle:"Axis 200" OR intitle:"Axis 2100"
intitle:"Network Camera NetworkCamera"
intitle:"netcam" intitle:home inurl:view
intitle:"MOBOTIX M1" intext:"Open Menu"
intitle:"Veo Observer XT"
inurl:"ViewerFrame?Mode=Motion"
intitle:"MJPEG Streaming Server"
site:earthcam.com "city name"
site:webcamtaxi.com "city name"
site:skylinewebcams.com "city name"
"live webcam" "city name" inurl:view
"city name" (webcam OR livecam OR "live cam" OR "live feed") -youtube

---

## Operator Quick Reference

| Operator | Example | Track |
|---|---|---|
| `site:` | `site:linkedin.com` | 1 |
| `inurl:` | `inurl:profile` | 1 |
| `intitle:` | `intitle:"index of"` | 1 |
| `intext:` | `intext:"password"` | 1 |
| `filetype:` / `ext:` | `filetype:pdf` | 1 |
| `"quotes"` | `"John Smith"` | 1 |
| `-` | `-site:twitter.com` | 1 |
| `OR` / `\|` | `site:x.com OR site:twitter.com` | 1 |
| `*` | `"John * Smith"` | 1 |
| `cache:` | `cache:site.com` | 2 only |
| `related:` | `related:site.com` | 2 only |
| `AROUND(n)` | `John AROUND(3) Smith` | 2 only |
| `before:` / `after:` | `before:2023-01-01` | 2 only |

---

## Extended Reference
For the full filtered dork library (700+ entries across all categories),
read the companion file in this skill folder:
~/.openclaw/skills/google-dorks/dorks-reference.md

Agents should read this file when:
- The curated templates above return insufficient results
- A niche platform or file type needs targeted discovery
- Building a comprehensive sweep for a complex investigation
