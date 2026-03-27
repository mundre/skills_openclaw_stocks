# Pulse -- Healthcare Support Roles: Deep Research
> Product research for proactive AI assistant. Practical, role-specific, actionable.
> Generated: March 2026

---

## Table of Contents
1. [Registered Nurses](#1-registered-nurses)
2. [Pharmacists](#2-pharmacists)
3. [Physiotherapists / Physical Therapists](#3-physiotherapists--physical-therapists)
4. [Dentists](#4-dentists)
5. [Dental Hygienists](#5-dental-hygienists)
6. [Optometrists](#6-optometrists)
7. [Psychologists / Therapists / Counselors](#7-psychologists--therapists--counselors)
8. [Midwives](#8-midwives)
9. [Paramedics / EMTs](#9-paramedics--emts)
10. [Radiographers](#10-radiographers)
11. [Occupational Therapists](#11-occupational-therapists)
12. [Cross-Role Patterns & Product Insights](#12-cross-role-patterns--product-insights)

---

## 1. Registered Nurses

### Daily/Weekly Rhythm
- **Shift patterns:** 8-hour (3/day) or 12-hour (day/night rotation) shifts, often 312 per week in hospital settings. Community/clinic nurses typically work 08:00-17:00 Monday-Friday.
- **Patient load:** Hospital ward: 4-8 patients per nurse (ideal); in underfunded public hospitals, 10-20+ is common. Community nurses: 8-15 home visits per day.
- **Admin vs clinical split:** 30-40% of shift time is documentation and admin -- widely cited as the #1 burnout driver. Nurses frequently document during or after patient care, not in dedicated windows.
- **Weekly rhythm:** Monday handover meetings, weekly ward rounds with doctors, Friday discharge planning spike. Medication audits often scheduled mid-week.

### Before Tasks (Start of Shift)
- **Handover/SBAR report** from outgoing nurse -- verbal + written, 15-30 min
- Pull up patient notes; check overnight vitals, flagged incidents
- Check medication administration records (MAR) for due doses in first hour
- Verify IV lines, drains, wound dressings need checking
- Confirm bed census / new admissions expected
- Check crash cart / emergency equipment (scheduled log)
- Review any pending lab results or radiology that came back overnight

### After Tasks (End of Shift / Post-Patient Care)
- Complete nursing notes in EMR (often takes 30-60 min at end of shift)
- Update care plans if patient status changed
- Administer and document end-of-shift medications
- Complete incident reports if anything went wrong
- Handover documentation for incoming nurse
- Referral follow-ups (physio, OT, social work)
- Discharge summaries and patient education documentation
- Restock used supplies (document usage for inventory)

### Time-Sensitive Triggers
- **CPD/Continuing Education:** Most jurisdictions require 20-35 CPD points/year for licence renewal. Deadlines are annual, tied to registration anniversary date. Nurses often leave this until the last 2 months.
- **Licence renewal:** Annual (most countries). Lapse = immediate inability to practice.
- **BLS/CPR recertification:** Every 2 years (AHA/RCSA standard). ACLS every 2 years for ICU/ED nurses.
- **Medication competency sign-offs:** Hospitals require annual IV drug calculation competency tests.
- **Controlled drug (CD) counts:** Every shift handover -- two nurses must co-sign CD register. Discrepancies must be reported within same shift.
- **Wound dressing changes:** Time-scheduled (e.g., every 48h or 72h) -- system flags when due.
- **Patient vitals frequency:** Post-op patients may need vitals Q15min or Q1h -- easy to miss in busy wards.
- **Immunisation schedules:** Community nurses managing patient flu, pneumococcal, tetanus schedules by age/risk group.
- **PRN medication review:** Medications given "as needed" still need documented rationale within defined windows.

### Stress / Anxiety Points
- **Documentation burden** -- "If it's not documented, it didn't happen" creates constant anxiety. Nurses fear legal exposure from incomplete notes.
- **Medication errors** -- High-stakes; every nurse carries fear of making a drug error, especially with similar-sounding drug names.
- **Controlled drug discrepancies** -- Even a 1-tablet count error triggers formal investigation. Highly stressful.
- **Staffing shortages** -- Covering for sick colleagues increases patient load unexpectedly.
- **Shift handovers** -- Concern about missing a critical patient deterioration that happened mid-shift.
- **Family communication** -- Managing relatives' expectations, especially in end-of-life situations.
- **Alert fatigue** -- EMR systems fire so many alarms that nurses desensitise to them.

### Data Sources
- **EMR/EHR:** Epic, Cerner, Meditech, MEDITECH Expanse, iSoft (SA/AU)
- **MAR (Medication Administration Record):** Usually embedded in EMR
- **Incident reporting systems:** Datix, RiskMan
- **CD (Controlled Drug) register:** Physical book + digital log
- **Scheduling:** ShiftAdmin, Deputy, Kronos
- **CPD tracking:** SANC (SA), NMC (UK), AHPRA (AU) portals
- **Patient monitoring systems:** Philips IntelliVue, Draeger (vitals)

### Proactive AI Opportunities
1. **"Mrs Khumalo in Bed 4 hasn't had her Q4h vitals checked -- she's 45 minutes overdue. Want me to flag it?"**
2. **"Your CPD renewal is due in 34 days. You need 8 more points. There's a free SANC-accredited wound care webinar tonight at 19:00. Want me to register you?"**
3. **"The CD register shows 1 morphine tablet unaccounted for since the night shift. You'll need a co-sign and incident report before handover at 19:00."**
4. **"Your BLS certification expires in 6 weeks. The hospital is running a recertification session next Tuesday at 14:00 -- you're off duty. Want me to book it?"**
5. **"5 patients have pending discharge paperwork from this morning. 3 haven't been seen by the doctor yet for sign-off. Want me to send a chase message to Dr. Nkosi?"**

---

## 2. Pharmacists

### Daily/Weekly Rhythm
- **Shift patterns:** Retail/community pharmacy: 08:00-18:00 or 09:00-19:00, 5-6 days/week. Hospital pharmacists: 8-12 hour shifts, rotating weekends. 24h pharmacies operate 3-shift rotation.
- **Patient/script load:** Community pharmacy: 150-400 scripts/day in a busy store. Hospital pharmacy: verifies 200-600 drug orders/day. Clinical pharmacist on ward: 20-50 medication reviews/day.
- **Admin vs clinical split:** Dispensary pharmacists: 70% dispensing, 20% patient counselling, 10% admin. Clinical pharmacists: 50% patient reviews, 30% clinical documentation, 20% meetings/admin.
- **Weekly rhythm:** Monday is typically the busiest (weekend backlog). Friday prescription spike as doctors write scripts before weekend.

### Before Tasks (Start of Day / Shift)
- Check controlled drug (CD) stock balances -- count and verify against register
- Review overnight dispensing queue (hospital) or previous day's uncollected scripts
- Temperature monitoring log -- cold chain fridges must be checked and logged
- Check for drug shortage alerts or formulary changes from overnight supplier updates
- Review any urgent hospital drug orders or stat doses
- Check for expired stock (daily sweep in some dispensaries)
- Review patient waitlist / pre-prepared scripts ready for collection
- Sign off on overnight dispensing done by pharmacy technicians

### After Tasks (End of Day / Post-Dispensing)
- Reconcile CD register -- count must balance perfectly before store closes
- Complete end-of-day stocktake for Schedule 5/6 drugs (SA) / Schedule II/III (US)
- Process returns and wastage documentation
- Send outstanding prescriptions to collection notifications (SMS/email)
- Complete clinical notes for patient counselling sessions
- Document any pharmacovigilance reports (adverse drug reactions)
- Submit daily dispensing stats to health authority portal (hospital/public sector)
- Restocking orders -- review automated reorder triggers and approve

### Time-Sensitive Triggers
- **Licence renewal:** Annual, to pharmacy council (SAPC in SA, GPhC in UK, state boards in US). Non-renewal = immediate suspension.
- **CPD requirements:** 30 CPD credits/year (SAPC). UK: 9 CPD entries/year minimum. Must document reflection, not just attendance.
- **Cold chain monitoring:** Fridge temperatures must stay 2-8C; logs required every shift. Excursion = quarantine all affected stock + formal report within 24h.
- **Controlled drug audits:** CD registers audited monthly by pharmacy manager; annual audit by health authority. Any discrepancy triggers investigation.
- **Drug expiry sweeps:** Regulatory requirement; most pharmacies do weekly near-expiry checks and monthly full sweeps.
- **Prescription validity windows:** SA: Schedule 5 scripts valid 30 days, Schedule 6: 7 days. UK: 28-day validity for NHS scripts. Expired script cannot be dispensed -- patient must return to GP.
- **Chronic medication repeats:** Patients on chronic scripts (hypertension, diabetes, HIV) have repeat cycles of 28/30 days. Gap in supply = patient non-adherence risk. Pharmacies flag this.
- **Drug interaction monitoring:** Time-sensitive for new scripts -- must be checked before dispensing.
- **Immunisation stock management:** Flu season = massive stock management challenge; order windows are seasonal and must be pre-planned.
- **Pharmacovigilance reporting:** ADR reports must be submitted to MCC (SA) / MHRA (UK) within 15 days for serious reactions.

### Stress / Anxiety Points
- **CD discrepancies** -- Single biggest stressor. Any count error = potential criminal liability. Pharmacists have lost their licences over honest counting mistakes.
- **Drug shortages** -- National shortages (SA has chronic ARV and oncology drug shortages) force pharmacists into stressful patient counselling and alternative-sourcing.
- **Script forgeries** -- Pharmacists are legally responsible for detecting forged prescriptions, especially for Schedule 5/6.
- **Volume pressure** -- 200+ scripts/day with 5-minute verification windows creates high error risk anxiety.
- **Cold chain failure** -- Vaccine or insulin fridge alarm on a Sunday = after-hours emergency.
- **Patient confrontation** -- Patients angry about drug shortages, insurance rejections, or script validity issues. Frontline emotional labour.
- **Locum uncertainty** -- Many pharmacists work as locums; inconsistent workflow, unfamiliar systems, unknown stock levels.

### Data Sources
- **Dispensing software:** Unisolv (SA), PharmacyConnect, ScriptPro, RxWorks (AU), Titan (UK)
- **NAPPI codes / formulary databases:** SA: NAPPI (National Pharmaceutical Product Interface)
- **Medical aid (insurance) adjudication:** SA: Discovery, Medscheme, Momentum portals
- **Cold chain loggers:** Digital fridge monitors (Onset HOBO, etc.)
- **CD registers:** Physical + digital (most jurisdictions require physical)
- **Drug interaction databases:** Micromedex, Lexicomp, Stockley's
- **Pharmacovigilance portal:** MedWatch (US), Yellow Card (UK), MCC VigiBase (SA)
- **Supply chain:** Pharmaceutical wholesalers -- Dis-Chem Pharmacy, Clicks Pharmacy systems; hospital: SAP-based procurement

### Proactive AI Opportunities
1. **"Fridge 2 temperature logged at 9.1C at 06:47 -- just above the 8C threshold. That's 3 times this week. Want me to flag this for a maintenance callout and quarantine the Actrapid insulin until it's cleared?"**
2. **"You have 14 patients whose chronic HIV scripts are due for renewal in the next 7 days. 6 haven't collected last month's repeat yet. Want me to generate a follow-up list for the nurse to call?"**
3. **"Your SAPC CPD deadline is March 31st. You have 18 of 30 required points logged. There are two upcoming webinars that would cover the gap -- want me to book them?"**
4. **"Supplier just flagged a shortage on Metformin 850mg -- you have ~40 units left at current dispensing rate. Do you want me to source alternatives from Clicks Wholesale and draft a patient communication?"**
5. **"The monthly CD audit is due tomorrow. I've pre-filled the reconciliation from today's register logs. There's a 1-unit discrepancy on Tramadol 100mg from Tuesday's evening shift. Want to review before the pharmacist-in-charge signs off?"**

---

## 3. Physiotherapists / Physical Therapists

### Daily/Weekly Rhythm
- **Shift patterns:** Private practice: 08:00-17:00 or 07:00-18:00, Mon-Fri (some Saturday mornings). Hospital-based: rotating shifts including weekends, 8-12h.
- **Patient load:** Private: 8-14 patients/day (30-60 min sessions). Hospital: 10-20 patients/day (shorter sessions, higher acuity). Sports physio: 6-10/day (60-90 min per patient).
- **Admin vs clinical split:** Private: 70% clinical, 30% admin (notes, billing, scheduling). Hospital: 60% clinical, 40% admin and MDT meetings.
- **Weekly rhythm:** Monday planning/case reviews. Mid-week tends to be peak patient volume. Friday: discharge assessments, MDT notes. Regular MDT meetings (hospital) weekly.

### Before Tasks (Start of Day)
- Review day's schedule -- flag complex or new patients needing extra prep
- Pull up notes for returning patients -- check last session outcomes, HEP compliance
- Review any referrals received overnight from GPs or consultants
- Prepare treatment areas -- treatment table paper, equipment (ultrasound probes, TENS units, resistance bands)
- Equipment checks -- ultrasound gel, calibration reminder checks
- New patient intake: review GP referral letter, diagnostic imaging reports (X-rays, MRI)
- Prepare exercise program printouts / HEP (Home Exercise Programme) handouts

### After Tasks (Post-Patient / End of Day)
- Clinical notes (SOAP format) -- one of the most time-consuming tasks; 5-15 min per patient
- Update exercise programmes based on session progress
- Write referral letters back to GPs / specialists
- Book follow-up appointments
- Billing -- physiotherapy billing is session-based; private patients + medical aid claiming
- Submit medical aid claims (electronic)
- Send HEP to patients via email or patient portal
- Equipment disinfection and linen change between patients
- End-of-day: ensure exercise equipment is wiped down, treatment areas reset

### Time-Sensitive Triggers
- **HPCSA (SA) / HCPC (UK) / state board licence renewal:** Annual or biennial. Failure to renew = immediate deregistration.
- **CPD requirements:** HPCSA: 30 CEUs/year (15 formal, 15 informal). APTA (US): 30 PDH per 2-year cycle.
- **Dry needling / specialist certification renewal:** Some advanced techniques (dry needling, manual therapy) require annual certification maintenance.
- **Equipment calibration:** Ultrasound therapy units must be calibrated annually (regulatory requirement in most countries). TENS machines: annual check. Calibration certificates must be on-site and available for inspection.
- **Medical aid authorisation windows:** SA medical aids require pre-authorisation for >6 physiotherapy sessions. Auth codes expire. Expired = claim rejected.
- **Patient discharge timelines:** Hospital: rehab milestones (e.g., patient must be mobilising independently within X days post-op for certain surgical protocols).
- **Patient recall:** Post-surgical patients need follow-up at defined intervals (6-week, 3-month, 6-month). Patients often forget.
- **Home exercise programme compliance checks:** Research shows HEP compliance drops sharply after 2 weeks. Proactive check-in at day 10-14 is evidence-based.

### Stress / Anxiety Points
- **Documentation load** -- SOAP notes for every patient; medicolegal requirement. Private physios often do notes in evenings at home.
- **Medical aid rejections** -- Claims rejected due to expired auth codes, incorrect ICD-10 codes, or exceeded annual limits. Revenue impact + admin rework.
- **Patient non-compliance** -- Patient doesn't do HEP, doesn't improve, physio feels responsible but can't control it.
- **No-shows** -- 30-60 minute appointment blocks lost. Income for private practice. Especially frustrating when cancellation notice is under 24h.
- **Referral bottlenecks** -- Waiting for GP or specialist to authorise more sessions; patient in limbo.
- **Scope of practice concerns** -- Grey areas (e.g., when to refer back to surgeon, when to escalate). Documentation anxiety when outcomes are poor.

### Data Sources
- **Practice management:** Cliniko, Jane App, Practice Perfect, Nookal (AU/SA)
- **Billing/medical aid:** Healthbridge (SA), Remedi, Tygerberg Billing
- **HPCSA portal:** CPD log submissions
- **Medical aid portals:** Discovery Health, Bonitas, Medscheme (SA) -- authorisation and claims
- **Referral sources:** GP referral letters (email/fax still used), hospital HIS

### Proactive AI Opportunities
1. **"Your ultrasound machine calibration certificate expires in 18 days. CaliMed's next available slot in Cape Town is Thursday the 24th. Want me to book it?"**
2. **"4 patients are due for their 6-week post-op follow-up this week and haven't rebooked. Want me to send them appointment reminders?"**
3. **"David Ndlovu's Discovery auth code (FYS-2294) expires Friday and he has 2 sessions left. I can request a new auth online -- should I?"**
4. **"You have 3 no-shows this week so far -- all without 24h notice. Your cancellation policy allows a fee. Want me to send the fee notices and update the cancellation tracking log?"**
5. **"You're 12 CPD points short of your HPCSA annual requirement. The SASP congress is in 6 weeks -- that would cover 8 points. Early bird closes Friday. Want me to register?"**

---

## 4. Dentists

### Daily/Weekly Rhythm
- **Shift patterns:** Private practice: typically 08:00-17:00, Mon-Fri (some Saturday mornings). Sessions divided into AM (3-4 patients) and PM (3-4 patients). Appointment blocks: 30 min to 2 hours depending on procedure.
- **Patient load:** 8-14 patients/day in general practice. Complex restorative or implant days may be 4-6 patients. Orthodontic check-up days can be 20-25 (shorter appointments).
- **Admin vs clinical split:** 60-70% clinical. 20-25% notes/billing. 10-15% lab communication, treatment planning, equipment checks.
- **Weekly rhythm:** Monday: review lab work arriving for the week. Thursday/Friday: push to complete weekly treatment plans before weekend. Lab deadlines drive the week.

### Before Tasks (Start of Day)
- Review day's schedule -- identify complex cases, confirm lab work has arrived
- Check that lab items (crowns, veneers, dentures, orthodontic appliances) are in and matched to correct patient
- Check sterilisation cycle logs -- autoclave must have run and passed the day's bowie dick test
- Check dental chair, suction, x-ray unit are operational
- Prepare patient notes -- review treatment plan, last visit notes, medical history alerts
- Confirm medical alert flags (allergies, anticoagulant patients, heart conditions requiring antibiotic prophylaxis)
- Prepare instruments for first patient; check x-rays loaded in system
- Verify consent forms are ready for any new patients or surgical procedures

### After Tasks (Post-Patient / End of Day)
- Clinical notes -- update dental chart, perio charting, treatment notes
- Submit lab prescriptions for impressions / scans taken today
- Write prescriptions (antibiotics, analgesics, mouthwash)
- Referral letters to oral surgeons, periodontists, endodontists, orthodontists
- Book next appointments (follow-ups, second stages, reviews)
- Billing -- procedure codes, medical aid claims submission
- Autoclave cycle documentation -- sign off sterilisation logs
- Equipment decontamination logs -- chairs, handpieces, x-ray heads
- Review x-rays taken today; record findings in notes
- End-of-day: check controlled drugs stock (if any Schedule 5/6 prescribed)

### Time-Sensitive Triggers
- **HPCSA/GDC licence renewal:** Annual. Non-payment or non-renewal = deregistration.
- **CPD requirements (HPCSA):** 30 CEUs/year. Dental CPD must include specific category requirements (ethics, infection control). NICE/GDC (UK): 75 verifiable CPD per 5-year cycle, with 10 mandatory hours in specific topics.
- **Autoclave validation:** Quarterly spore testing (biological indicator tests) is best practice / regulatory minimum in most jurisdictions. Annual autoclave service.
- **X-ray equipment compliance:** Dental x-ray units require regulatory certification and periodic inspection (varies by country: 3-yearly in UK under IR(ME)R, annual in some SA provinces). Radiation protection supervisor designation.
- **Radiography CPD:** Most dental boards require x-ray safety refresher every 3-5 years.
- **Patient recall cycles:** 6-month check-up and hygiene visit is the standard recall cycle. High-risk patients: 3 months. Low-risk adults: potentially 12-24 months. Missing recalls = patient treatment gap = liability and revenue loss.
- **Lab turnaround deadlines:** Crown/bridge impressions -> lab needs 10-14 working days; fit appointment must be booked in that window.
- **Prescription validity:** Antibiotic/pain prescriptions typically valid 30 days; controlled drugs shorter.
- **Dental implant follow-up protocols:** Implant integration check at 3 months, full restoration fitting at 6 months -- strict timelines per implant manufacturer protocol.
- **Infection control compliance:** COSHH assessments (UK), annual infection control audit, staff immunisation (hepatitis B) records.

### Stress / Anxiety Points
- **Lab errors or late returns** -- Crown comes back wrong shade or wrong fit = remake, two weeks delay, unhappy patient, wasted appointment slot.
- **Failed treatment / complications** -- Failed root canal, post-extraction dry socket, implant failure -- medicolegal anxiety is high.
- **No-shows** -- 30-120 minute blocked appointments. Loss of revenue.
- **Medical emergency preparedness** -- Dental chair is a high-anxiety environment. Medical emergencies (anaphylaxis, syncope, medical collapse) do happen. Adrenaline autoinjectors + oxygen kit must be in date and staff trained.
- **Patient anxiety management** -- Significant portion of patients are dental-phobic; managing them takes extra time and emotional energy.
- **Documentation for insurance claims** -- Incorrect ICD-10 or ADA procedure codes = claim rejection. Some dentists reject 20% of claims first time.
- **Infection control audits** -- Particularly since COVID-19, IPC audits are stressful.

### Data Sources
- **Practice management / clinical software:** Carestream Dental, Dentrix, Softdent, Exact (Software of Excellence), SOE Dental System, Salud (SA), Healthbridge (SA)
- **Radiography software:** Digora, Dexis, VixWin, CS Imaging
- **Lab communication:** Lab prescription books (paper still widespread) + digital (iTero, 3Shape Communicate)
- **Medical aid / billing:** Healthbridge, Tygerberg Billing (SA), Denplan (UK)
- **Sterilisation logs:** Usually paper-based or practice management module
- **HPCSA CPD portal:** Online submissions

### Proactive AI Opportunities
1. **"Your autoclave spore test is overdue -- last one was 94 days ago. Steri-Lab can collect tomorrow. Want me to book it?"**
2. **"7 patients are due for their 6-month recall this week and haven't booked. 3 are on the preferred-contact SMS list. Want me to send reminders?"**
3. **"The crown for Mrs. Badenhorst (seat date Friday) hasn't been logged as received from the lab yet. It's Wednesday. Want me to call ProLab to confirm it's dispatched?"**
4. **"Your adrenaline autoinjector (EpiPen) expires end of this month. Want me to add it to next week's pharmacy order and set a reminder to check the rest of your emergency kit?"**
5. **"You have 14 outstanding medical aid claims older than 30 days. 6 are for Discovery -- these usually get rejected if not followed up. Want me to generate a chase list?"**

---

## 5. Dental Hygienists

### Daily/Weekly Rhythm
- **Shift patterns:** Often part-time or sessional within a dental practice. Typical: 3-5 days/week, 08:00-17:00. Some practices have hygienist 2 days/week, dentist filling other slots.
- **Patient load:** 6-10 patients/day (45-60 min per patient for full hygiene visit, 30 min for recalls).
- **Admin vs clinical split:** 80% clinical, 20% notes and billing. Less administrative burden than dentists, but notes are still medicolegally critical.
- **Weekly rhythm:** Patient recalls drive the schedule. Consistent week-to-week. Heavier at start of week (Monday morning is high-volume recall day in many practices).

### Before Tasks
- Review patient notes -- last visit, perio charting history, medical history alerts
- Check instruments are sterilised from previous day's autoclave cycle
- Set up treatment area -- scalers, curettes, polishing kit, disclosing tablets, x-ray viewer
- Check suction and water lines (dental unit waterline flushing is a regulatory requirement -- 2 min flush at start of day)
- Confirm patient recall reason (routine scale + polish, perio maintenance, post-treatment review)

### After Tasks
- Update periodontal charts -- pocket depths, bleeding on probing scores, recession measurements
- Write clinical notes -- hard and soft tissue findings, oral hygiene instructions given
- Recommend treatment changes to dentist if perio status has deteriorated
- Book next recall appointment
- Billing -- submit claim for hygiene services
- Oral hygiene product recommendations logged
- Referral flag to dentist for suspicious lesions, caries, failing restorations

### Time-Sensitive Triggers
- **HPCSA/GDC registration renewal:** Annual. Dental hygienists are separately registered in most countries.
- **CPD requirements:** HPCSA: 15 CEUs/year. GDC (UK): 150 verifiable hours per 5-year cycle with mandatory topic coverage.
- **Patient recall cycles:** 3-month recalls for perio maintenance patients; 6-month for low-risk. High adherence to schedule = better clinical outcomes + more revenue.
- **Perio re-evaluation:** After active perio treatment, formal re-evaluation at 6-8 weeks is a clinical standard.
- **Instrument sharpening / replacement:** Periodontal instruments must be sharp for effective scaling -- documented checks recommended quarterly.
- **Dental unit waterline testing:** Quarterly waterline microbial testing is becoming standard in many jurisdictions (Legionella risk).

### Stress / Anxiety Points
- **Patient non-compliance with oral hygiene** -- Frustration when patients don't brush/floss between visits; hygienist does the same treatment cycle repeatedly.
- **Detecting pathology and knowing when to escalate** -- Spotting suspicious lesions (potentially malignant) and communicating this appropriately is anxiety-inducing.
- **No-shows** -- Revenue impact and wasted clinical time.
- **Being underutilised** -- Hygienists in practices where dentists don't promote hygiene services feel undervalued and are often not fully booked.
- **Scope of practice creep** -- Asked to perform tasks outside scope (e.g., take impressions, assist in surgical procedures without proper authorisation).

### Data Sources
- Same practice management systems as dentists (Exact, Dentrix, Salud)
- Perio charting modules within dental software
- Medical aid portals for hygiene claims

### Proactive AI Opportunities
1. **"11 of your active perio maintenance patients are on 3-month recalls -- 4 are overdue by more than 2 weeks. Want me to send reminder messages?"**
2. **"Mrs. van Zyl's perio re-evaluation was due 6 weeks after her last SRP. That was 9 weeks ago. Want me to flag this to Dr. Smit and book a review?"**
3. **"Your dental unit waterline test kit is due -- last test was 97 days ago. Want me to order a new AquaSafe test kit and set a reminder?"**
4. **"You have 3 gaps in Friday's schedule after a cancellation. There are 2 patients on the hygiene waiting list. Want me to contact them?"**
5. **"Your GDC CPD cycle ends in 4 months. You're 42 hours short of the 150-hour requirement. Here are two online perio CPD courses that would cover 20 hours each."**

---

## 6. Optometrists

### Daily/Weekly Rhythm
- **Shift patterns:** Private/retail optometry: 08:30-17:30 or 09:00-18:00, Monday-Saturday (retail environments often require Saturday). Some extended hours in shopping centre practices.
- **Patient load:** 8-14 comprehensive eye exams/day (30-45 min each). Retail optometrists may see 15-20 if mixing short contact lens follow-ups with full exams.
- **Admin vs clinical split:** 65-70% clinical, 30-35% admin (notes, spectacle/CL orders, insurance claims, referrals).
- **Weekly rhythm:** Monday: process weekend orders, review lab deliveries due. Friday: confirm week's spectacle orders have been dispatched from lab. Ongoing: manage contact lens stock and orders.

### Before Tasks
- Review day's appointment list -- flag new patients, complex cases, follow-ups
- Check clinical notes for returning patients -- last refraction, IOP, fundus notes
- Prepare equipment -- auto-refractor, slit lamp, OCT (if available), fundus camera, tonometer (calibrate)
- Calibrate tonometer (Goldmann applanation) -- must be calibrated at start of each day
- Check that trial frame lenses and contact lens diagnostic sets are clean
- Review any lab orders arriving today -- match to patient fitting appointments
- Flag patients with medical alerts (glaucoma suspects, diabetic retinopathy monitoring, macular degeneration)

### After Tasks
- Complete clinical notes -- refraction results, IOP, fundus findings, clinical impressions
- Write spectacle/contact lens prescriptions
- Submit spectacle or contact lens orders to optical laboratory
- Write referral letters to ophthalmologists (for surgical cases, pathology)
- Billing -- insurance/medical aid claims for eye exam and dispensing
- Patient communication -- notify when spectacles are ready for collection
- Contact lens follow-up scheduling
- Register diabetic eye screening results with relevant health authority / GP
- Flag any suspicious findings for ophthalmology referral pathway

### Time-Sensitive Triggers
- **HPCSA/GOC licence renewal:** Annual (SA: HPCSA; UK: General Optical Council; US: state boards biennial).
- **CPD requirements:** HPCSA: 30 CEUs/year. GOC (UK): 36 hours per 3-year cycle (includes specific mandatory topics).
- **Tonometer calibration:** Should be calibrated daily; annual service + calibration certificate.
- **OCT / fundus camera service:** Annual or biannual depending on manufacturer and jurisdiction.
- **Patient recall cycles:** 2 years for healthy low-risk adults; 1 year for contact lens wearers; 6-12 months for glaucoma suspects, diabetic patients, myopia management cases.
- **Glaucoma monitoring recalls:** High-risk patients on medication need IOP checks every 3-6 months; missed recalls are a serious clinical and liability concern.
- **Diabetic retinopathy screening:** Annual screening is standard of care. Optometrists often run government-funded schemes; reporting deadlines to health authorities apply.
- **Contact lens prescription validity:** 1 year in most countries (UK: 1 year). Expired CL prescription cannot be used to dispense -- patient must be recalled.
- **Spectacle lens order turnaround:** Standard 5-10 working days; complex lenses 10-21 days. Fitting appointment should be booked at order time.
- **Myopia management reviews:** Orthokeratology and myopia control spectacle/CL patients need 1-month, 3-month, 6-month check protocols.

### Stress / Anxiety Points
- **Missing pathology** -- Failing to detect early glaucoma, macular degeneration, diabetic retinopathy carries significant medicolegal and patient harm risk. This is the deepest clinical anxiety in optometry.
- **Referral pathway delays** -- Referring a patient with suspected pathology and not knowing if ophthalmology follow-through happened.
- **Spectacle order errors** -- Wrong prescription or lens type dispensed. Remake costs + patient dissatisfaction.
- **Contact lens complications** -- Microbial keratitis from over-wearing; patient blames optometrist.
- **Insurance claim rejections** -- Incorrect exam codes or insufficient documentation.
- **Managing patient expectations** -- Explaining that deterioration in vision isn't correctable with lenses (e.g., macular degeneration) is emotionally heavy.

### Data Sources
- **Practice management / clinical:** Optomate (AU/SA), Eyefinity (US), Acuitas (SA), Specsavers Practice Hub (franchise), Visioffice
- **Lab ordering systems:** Zeiss, Essilor, Rodenstock portals
- **Medical aid portals:** Discovery, Bonitas, Medihelp (SA)
- **Ophthalmology referral pathways:** NHS DRSS (UK diabetic screening), regional GP referral systems
- **OCT / imaging software:** Heidelberg, Topcon, Zeiss CIRRUS

### Proactive AI Opportunities
1. **"9 of your glaucoma-suspect patients are due for their 6-month IOP check -- 3 are now overdue. Want me to send recall notifications?"**
2. **"Mrs. Hendricks' contact lens prescription expired 4 days ago. She submitted a repeat order online last night. I've paused the order -- want me to book her for a review first?"**
3. **"There are 6 spectacle orders with labs that have been pending for over 12 working days -- past the expected delivery window. Want me to chase them and notify the patients of the delay?"**
4. **"Mr. Patel was referred to ophthalmology for suspected early glaucoma 6 weeks ago. There's no correspondence back in the system. Want me to follow up with the ophthalmology rooms?"**
5. **"Your GOC CPD cycle ends in 3 months and you're 11 hours short. The College of Optometrists' online therapeutics course runs this weekend -- 12 hours, qualifies for the clinical skills mandatory category."**

---

## 7. Psychologists / Therapists / Counselors

### Daily/Weekly Rhythm
- **Shift patterns:** Private practice: typically self-set hours, often 09:00-17:00 or 08:00-19:00 to accommodate working clients (evening slots are highly sought). 4-6 days/week, with flexibility.
- **Patient load:** 4-8 therapy sessions/day (50-60 min sessions with 10 min buffer). Intensive outpatient: up to 10 sessions. Most therapists cap at 25-30 client sessions/week to avoid burnout.
- **Admin vs clinical split:** 50-60% clinical (sessions). 20-30% notes and treatment planning. 10-20% supervision, CPD, insurance authorisation. Solo practitioners also manage all business admin.
- **Weekly rhythm:** Monday: review week's schedule, catch up on notes from Friday. Mid-week: supervision (ethical/clinical requirement). Friday: complete all outstanding session notes before weekend.

### Before Tasks
- Review client notes from last session -- what was discussed, homework set, where client is in treatment plan
- Check for any risk flags -- suicidality, self-harm, safeguarding concerns from previous session
- Prepare for specific modalities (EMDR: prepare materials; CBT: review worksheet progress)
- Check consent/confidentiality documents are in place for new clients
- Set up therapy room -- tissues, water, appropriate seating arrangements
- Review risk management plan if client is on safety contract
- Check for any between-session contact (voicemails, texts) that changed clinical picture

### After Tasks
- Process notes -- most therapists write progress notes immediately post-session while memory is fresh (15-30 min)
- Update treatment plan if session indicated direction change
- Complete risk documentation if session raised concerns
- Write referral letters (to psychiatrists, GPS, social workers, specialist services)
- Supervision notes / reflective log (requirement for many registrations)
- Invoice / billing -- private billing, EAP (Employee Assistance Programme) claim, medical aid claim
- Submit medical aid session claims (SA: medical aid often requires ICD-10 code + treatment approach)
- Book follow-up appointment
- Crisis protocol documentation if activated

### Time-Sensitive Triggers
- **HPCSA/BPS/state board licence renewal:** Annual or biennial. Psychologists must maintain active registration to practice.
- **CPD requirements:** HPCSA (SA): 30 CEUs/year for psychologists. BPS (UK): ongoing CPD portfolio, no fixed number but must demonstrate reflective practice. APA (US): varies by state (typically 20-40 CEUs per 2-year renewal cycle).
- **Supervision hours:** Registered counselors / provisionally registered psychologists must accumulate supervision hours (SA: supervised practice requirements for intern psychologists). These must be tracked carefully.
- **Mandatory reporting deadlines:** Child abuse or elder abuse suspicions must be reported to relevant authority within defined timeframes (SA: within 72 hours in some contexts; UK: immediately). Missing this deadline has criminal and professional consequences.
- **Medical aid authorisation cycles:** SA medical aids typically authorise 10-15 sessions; re-authorisation must be applied for before sessions expire. Gap = sessions not covered = unexpected cost for client.
- **Treatment plan reviews:** Best practice dictates formal treatment plan review every 12 sessions or quarterly. Many insurers require this for continued authorisation.
- **EAP (Employee Assistance Programme) session limits:** Typically 6-8 sessions per presenting issue. Therapist must flag when approaching limit and assist transition to alternative care.
- **Risk review dates:** Clients on safety contracts (suicidality/self-harm) should have formal risk review dates set -- these are non-negotiable.

### Stress / Anxiety Points
- **Risk management** -- Managing suicidal or self-harming clients is the primary anxiety for most therapists. Fear of client harm, fear of missing deterioration, documentation burden when risk is present.
- **Compassion fatigue** -- Absorbing clients' trauma, grief, and distress session after session takes a cumulative toll. Often not acknowledged or managed well.
- **Note completion burden** -- Progress notes are time-consuming and medicolegally critical. Many therapists fall behind; this creates chronic low-level anxiety.
- **Medical aid rejections** -- Insurance companies demanding clinical justification or rejecting claims for conditions like trauma, relationship issues.
- **Confidentiality dilemmas** -- When a client discloses something that triggers a reporting obligation, the ethical complexity is acutely stressful.
- **Client non-attendance** -- High no-show rates in mental health (15-25%). Loss of income + clinical concern about client's wellbeing.
- **Burnout** -- Industry-specific: therapists rarely access their own support despite understanding its importance. Licence renewal requirements often include a "self-care" section that is perfunctorily completed.
- **No receptionist / admin support** -- Most private practice therapists are solo operators; they manage their own scheduling, billing, reminder messages, and admin alongside clinical work.

### Data Sources
- **Practice management / EHR:** SimplePractice (US), Cliniko, TheraNest, Writeupp (UK), TherapyNotes
- **Medical aid portals:** SA: Discovery, Medscheme, Bonitas
- **EAP management systems:** ICAS, Careways, BetterHelp for Work portals
- **Supervision log:** Often paper or personal spreadsheet -- a significant gap
- **Risk management documentation:** Usually within EHR, or paper-based
- **HPCSA CPD portal:** Online log

### Proactive AI Opportunities
1. **"You have 4 clients approaching their medical aid session limit this month -- 2 are at session 9 of 10. Do you want me to submit re-authorisation requests before the sessions run out?"**
2. **"It's Friday at 16:45. You have 3 session notes still incomplete from this week -- including one client who disclosed suicidal ideation on Wednesday. That note is now 48 hours old. Want to complete it now before the weekend?"**
3. **"Your supervision log shows you're 4 hours short of your quarterly requirement. Dr. Fourie has a supervision slot available Wednesday at 13:00 -- want me to book it?"**
4. **"Marcus (client ID 0047) missed his last 2 sessions without contact. His risk rating was Moderate at last session. Your protocol requires a welfare check after 2 missed sessions. Want me to prepare a welfare check letter for your review?"**
5. **"Your HPCSA renewal is in 6 weeks. You have 21 of 30 required CPD points. Here are three online trauma-informed care workshops this month -- each worth 4 CEUs."**

---

## 8. Midwives

### Daily/Weekly Rhythm
- **Shift patterns:** Hospital midwives: 12-hour rotating shifts (day/night), 3 shifts/week. Community midwives: typically 09:00-17:00 but with on-call obligations (24/7 in some community birth models). Independent midwives: on-call for births 24/7 with partner/backup covering.
- **Patient load:** Maternity ward: 4-8 women/midwife depending on acuity. Antenatal clinic: 8-15 appointments/session. Community: 6-10 home visits/day.
- **Admin vs clinical split:** 35-50% documentation (particularly high during labour and postnatal periods). Labour ward notes are exceptionally detailed -- continuous fetal monitoring interpretation and documentation is a major time commitment.
- **Weekly rhythm:** Antenatal clinic days (typically 2-3 days/week). Labour ward coverage ongoing. Postnatal visits concentrated in first 10 days postpartum.

### Before Tasks
- Handover from outgoing shift -- status of every woman in labour, any at-risk postnatal mothers and babies
- Review CTG (cardiotocograph) traces currently running -- assess fetal wellbeing
- Check maternal observations due (BP is critical -- pre-eclampsia screening)
- Review drug charts -- oxytocin infusions, epidurals, antibiotics
- Confirm resuscitation equipment is checked and operational (neonatal resus trolley, maternal crash trolley)
- Review antenatal clinic list for the day -- check booking notes, risk factors, test results due
- Review postnatal handover -- any babies requiring observation (jaundice, feeding difficulties, infection)

### After Tasks
- **Labour records** -- Partograph completion, continuous CTG documentation, drug administration during labour. These are some of the most detailed and medicolegally scrutinised notes in all healthcare.
- Update maternal and neonatal notes
- Complete birth registration documentation
- Notify GP, community midwife of birth and postnatal plan
- Arrange postnatal community midwife visits
- Newborn screening documentation (heel prick test: must be done at day 5)
- Infant feeding support documentation
- Submit antenatal blood results to notes, action abnormal results
- Notify screening programmes (e.g., antenatal HIV results, GBS status, gestational diabetes management plan)

### Time-Sensitive Triggers
- **NMC / HPCSA / SANC licence renewal:** Annual. Midwives must maintain registration to practice.
- **CPD requirements:** NMC (UK): 35 CPD hours per 3-year revalidation cycle. SANC (SA): 30 CEUs/year.
- **CTG interpretation competency:** Annual sign-off required in most hospital trusts. CTG misinterpretation is the most common cause of obstetric litigation.
- **Neonatal resus recertification:** Annual (NLS -- Neonatal Life Support) or biennial depending on jurisdiction.
- **Obstetric emergency drills:** Shoulder dystocia, postpartum haemorrhage, eclampsia -- mandatory annual simulation drills in hospital settings.
- **Newborn heel prick (PKU) screening:** Day 5 (1 day). Missed or late screening has serious consequences for conditions like PKU, hypothyroidism.
- **Postnatal visit schedule:** Day 1, Day 3, Day 5, Day 10 community visits (UK model). Missing day 5 = missed screening window.
- **Antenatal screening windows:** Combined first trimester screen: 11-14 weeks. Anomaly scan: 18-21 weeks. Glucose tolerance test: 24-28 weeks. Timing windows are strict -- missed = significant clinical gap.
- **Group B Streptococcus (GBS) management:** If GBS positive on screening, IV antibiotics must be commenced within 4 hours of labour onset. Time-critical trigger.
- **Vitamin K administration:** Must be offered within 1 hour of birth. Documentation required.

### Stress / Anxiety Points
- **Birth emergencies** -- Shoulder dystocia, cord prolapse, postpartum haemorrhage are time-critical emergencies where every minute counts. Midwives carry significant anxiety about responding correctly.
- **CTG interpretation** -- Misinterpretation of fetal heart rate patterns is the most common cause of intrapartum litigation in obstetrics. Midwives feel enormous pressure to correctly classify and act on CTG findings.
- **Documentation during labour** -- Labour is dynamic and unpredictable; maintaining contemporaneous records while managing an active birth is extremely challenging.
- **Staffing ratios** -- 1:1 care during active labour is the standard; understaffing in maternity is associated with adverse outcomes and known to midwives.
- **PTSD/secondary trauma** -- Perinatal loss (stillbirth, neonatal death) causes significant psychological impact on midwives. Poorly managed by most organisations.
- **Handover vulnerability** -- The transition between shifts during active labour is a recognised risk point.

### Data Sources
- **Maternity information systems:** Badgernet, K2 (UK), Sonia (SA), Sunrise Maternity
- **CTG systems:** Monica, Avalon Fetal Monitor, Philips Avalon
- **Neonatal screening portals:** NHS Newborn Blood Spot screening; NHSP
- **SANC/NMC CPD portals**
- **Antenatal screening programme portals:** NHS FASP (Fetal Anomaly Screening Programme)
- **Drug infusion systems:** Alaris, B Braun pumps -- linked to EMR in advanced systems

### Proactive AI Opportunities
1. **"Baby Johnson (born yesterday, currently day 1) is due for the heel prick PKU screen on Saturday -- that's day 5. The community midwife handover hasn't been completed yet. Want me to add this to the discharge checklist and notify the community team?"**
2. **"Mrs. Naidoo's glucose tolerance test was due between 24-28 weeks. She's now 29+2 weeks and no test is in her notes. She has an antenatal appointment tomorrow -- want me to flag this and pre-order the GTT?"**
3. **"Your annual CTG interpretation competency sign-off is due this month -- you're one of 4 midwives on the ward who hasn't completed it. The skills lab has slots Thursday morning."**
4. **"Antenatal clinic tomorrow has 11 bookings. 3 patients are flagged high-risk (gestational diabetes, previous PPH, pre-eclampsia history). Want me to prepare a risk summary for your review before the clinic starts?"**
5. **"Your NMC revalidation is due in 10 weeks. You need 2 more reflective discussion entries. Dr. Clarke has confirmed she can be your confirmer -- want me to schedule the revalidation meeting?"**

---

## 9. Paramedics / EMTs

### Daily/Weekly Rhythm
- **Shift patterns:** 12-hour shifts (07:00-19:00 / 19:00-07:00) is standard in most services. Some services run 8-hour or 10-hour patterns. Typically 3-4 shifts/week with rotating days off.
- **Patient load:** Variable by call volume. Urban advanced life support units: 6-12 calls per 12-hour shift. Busy urban services: up to 15-20. Rural: 2-6 calls/shift.
- **Admin vs clinical split:** 30-40% of shift is documentation (patient care reports/PCRs). Urban paramedics often complete PCRs between calls or in hospital handover time. Admin percentage increasing as systems move to ePCR.
- **Weekly rhythm:** No fixed weekly clinical rhythm -- driven entirely by incident demand. Scheduled activities: vehicle checks (start of every shift), weekly debrief/audit, monthly drug audits.

### Before Tasks (Start of Shift)
- Vehicle check -- documented inspection of ambulance body, lights, sirens, vehicle condition
- Equipment check -- cardiac monitor (AED/defib): daily self-test; oxygen cylinders: check pressure; bag-mask-valve; suction unit; spinal immobilisation equipment
- Controlled drug check and sign-on -- morphine, fentanyl, midazolam, ketamine (depending on level) counted and matched to register with incoming crew
- Drug expiry check -- scan for any near-expiry medications
- PPE stock check -- gloves, masks, sharps containers
- Log on to CAD (Computer Aided Dispatch) system
- Radio/communications check
- Brief review of any outstanding PCRs from previous shift if applicable

### After Tasks (Post-Call)
- Patient Care Report (PCR) completion -- time-stamped, detailed account of clinical assessment, interventions, drug administration, patient response. Medicolegal document. Must be completed before end of shift (often required within 24h).
- Drug use documentation -- every controlled drug administered must be logged against CD register
- Vehicle and equipment restocking -- replace used consumables, restock drug bags
- Decontamination -- vehicle and equipment clean after potentially infectious patients
- Clinical handover at hospital -- verbal + written transfer of care
- Incident reporting -- near misses, equipment failure, patient complaints

### Time-Sensitive Triggers
- **HPCSA/HCPC/NREMT licence renewal:** Annual. Paramedics must maintain active registration.
- **CPD/CE requirements:** NREMT (US): 60 hours per 2-year certification cycle including mandatory topics (airway, trauma, cardiology). HPCSA (SA): 30 CEUs/year. HCPC (UK): 2-year cycle.
- **ACLS/PALS/BLS recertification:** Every 2 years (AHA). Most services require these as employment conditions.
- **Controlled drug register reconciliation:** Daily (every shift handover). Discrepancies must be resolved before the outgoing crew can sign off.
- **Defibrillator self-test:** AEDs and manual defibrillators perform daily self-tests, but manual verification at shift start is required. Some equipment requires weekly user checks and monthly full checks. Annual service.
- **Oxygen cylinder hydrostatic testing:** Every 5 years (US/SA regulatory requirement). Must be out of service during testing.
- **Drug expiry management:** Morphine, adrenaline, glucose -- short shelf lives on some. Regular expiry sweeps, typically monthly.
- **Vehicle service schedule:** Ambulances are on strict service schedules (every 10,000km or 3 months). Out-of-service vehicles = reduced response capacity.
- **Mandatory training:** Scene safety, CBRN awareness, mass casualty incident training -- typically annual.
- **Immunisations:** Hepatitis B (required, documented), annual flu, COVID boosters in most services.

### Stress / Anxiety Points
- **Controlled drug accountability** -- Any CD discrepancy triggers investigation. Theft from drug bags by addicted colleagues is a known (rarely discussed) industry problem. Honest mistakes carry career risk.
- **Post-traumatic stress** -- Paramedics have high PTSD rates (estimated 20-35%). Paediatric deaths, mass casualty events, violent scenes. Psychosocial support is inconsistent.
- **Clinical decision-making under pressure** -- High-stakes diagnostic decisions made on roadside, often alone or with one partner, without full clinical history.
- **Documentation burden** -- PCRs must be detailed and accurate despite time pressure. Fear of retrospective scrutiny of clinical decisions.
- **Aggressive patients** -- Assaults on paramedics are common and underreported.
- **Inter-service communication** -- Handover to hospital is often chaotic; paramedics feel information is lost. Outcome unknown for most patients.
- **Fatigue** -- Night shifts, back-to-back calls, and limited rest between incidents creates cumulative fatigue that is a patient safety risk.

### Data Sources
- **CAD (Computer-Aided Dispatch):** Intergraph I/CAD, Hexagon CAD, Cleric CAD (SA)
- **ePCR (Electronic Patient Care Report):** ImageTrend, ESO, Stryker ePCR, Medusa (SA)
- **CD (Controlled Drug) registers:** Physical book (most services still paper for CD) + digital reconciliation
- **Equipment management:** Equipment track/barcode systems vary widely; many services still use paper
- **HPCSA / HCPC CPD portals**
- **Hospital ED systems:** Paramedics submit to hospital ED system at handover (Clinicom, Meditech, etc.)

### Proactive AI Opportunities
1. **"Your Lifepak 15 defibrillator passed today's self-test, but the manufacturer's annual service is overdue by 23 days. This needs to go to medical engineering before end of week. Want me to raise the service request?"**
2. **"The morphine balance on Unit 7 doesn't match the administration log from last shift -- there's a 1-ampoule discrepancy. You'll need to complete a CD incident report before sign-off today. Want me to pre-populate the form?"**
3. **"Your HPCSA licence renewal is due in 45 days. You're 8 CEUs short of your 30-point requirement. EMSSA is running a pre-hospital trauma conference online this weekend -- 10 CPD points. Want me to register you?"**
4. **"4 of your oxygen cylinders are below 50% capacity. Based on yesterday's call volume, you'll likely need top-ups before end of shift. The O2 station is available now -- want me to log the refill request?"**
5. **"Your ACLS certification expires next month. The next in-service recertification class is Tuesday at 08:00. You're off duty -- want me to book it?"**

---

## 10. Radiographers

### Daily/Weekly Rhythm
- **Shift patterns:** Hospital radiographers: rotating 8-12h shifts, 24/7 cover for emergency imaging. Outpatient/private radiography: 08:00-17:00 or 08:30-17:30, Monday-Friday (some Saturday).
- **Patient load:** Plain film (X-ray): 20-50 studies/day. CT radiographer: 15-30 studies/day. MRI: 8-15 studies/day. Ultrasound: 12-20 studies/day.
- **Admin vs clinical split:** 65-75% clinical (imaging). 20-25% quality checks, patient prep documentation, PACS annotation. 5-10% maintenance checks and QA.
- **Weekly rhythm:** Monday: backlog from weekend (emergency cases). Weekly QA meeting (equipment performance). Scheduled maintenance windows coordinated with radiology manager.

### Before Tasks (Start of Shift)
- Equipment QA checks -- plain film: daily QA phantom (image quality test), CR/DR plate calibration. CT: daily warm-up, calibration scan. MRI: daily QA phantom scan, magnetic field checks.
- Review day's schedule -- inpatients vs outpatients, urgent/stat requests
- Check contrast media stock -- iodinated contrast (CT), gadolinium (MRI): check lot numbers, expiry dates, stock levels
- Review any overnight inpatient requests and prioritise
- Check patient preparation notes -- patients requiring NPO (fasting), bowel prep, or contrast allergy pre-medication
- Check radiation protection compliance -- dosimetry badges (personal dose monitors) worn and logged

### After Tasks (Post-Study)
- PACS (Picture Archiving and Communication System) upload -- confirm all images correctly labelled, annotated, sent to radiologist worklist
- Radiation dose documentation -- record patient dose (DLP/mGy) for CT studies (legal requirement in most countries)
- Contrast reaction documentation -- if contrast administered, document lot number, volume, any adverse reaction
- QA documentation -- log daily QA results in quality management system
- Equipment fault logging -- any anomalies during the day must be reported
- Restock used items -- contrast media, syringes, needles, cannulation supplies
- Decontaminate equipment -- ultrasound probes, CT couch, barium equipment

### Time-Sensitive Triggers
- **HPCSA/HCPC/ARRT licence renewal:** Annual or biennial.
- **CPD requirements:** HPCSA: 30 CEUs/year. HCPC (UK): 2-year cycle (no fixed hours but demonstrable CPD). ARRT (US): 24 CE credits per 2-year cycle.
- **Daily QA -- mandatory:** CT, MRI, and plain film equipment require daily quality assurance tests before clinical use. If QA fails, equipment cannot be used until fault is resolved.
- **Annual equipment service:** CT scanners, MRI systems, fluoroscopy units -- annual preventive maintenance by manufacturer or accredited biomedical engineer. Cannot be deferred.
- **Radiation protection safety assessment:** IR(ME)R (UK) requires periodic radiation protection advisor (RPA) review. CQC inspection may require evidence of compliance.
- **Radiation dosimetry badge review:** Personal dose monitors sent for reading monthly (or quarterly). Results reviewed by radiation protection supervisor. If dose exceeded, investigation and potentially suspension from work pending review.
- **Contrast media expiry management:** Iodinated contrast has defined shelf life; gadolinium agents have strict storage requirements. Expired contrast = never to be used.
- **Mammography accreditation:** Mammography units undergo rigorous annual accreditation testing (ACR in US, NHSBSP in UK). Accreditation expiry = cannot perform screening mammography.
- **MRI safety zone compliance:** Annual review of MRI safety policy, implant compatibility database updates, staff MRI safety training.
- **Radiation dose audit:** Annual review of patient dose data to ensure compliance with diagnostic reference levels (DRLs).

### Stress / Anxiety Points
- **Radiation dose errors** -- Exposing a patient to an incorrect (too high) radiation dose, particularly in CT, has serious consequences. Documentation anxiety is high.
- **Contrast reactions** -- Anaphylaxis from iodinated contrast is rare but life-threatening. Radiographers often administer contrast and must manage reactions while the radiologist is elsewhere.
- **MRI safety incidents** -- Ferromagnetic objects in the MRI room can cause catastrophic injury. Radiographers bear responsibility for screening.
- **Image quality pressure** -- Radiologists will reject poor images; repeat exposures increase patient dose and workload.
- **Equipment failure during urgent study** -- CT failing mid-scan on a trauma patient is a critical incident.
- **Reporting turnaround pressure** -- Urgent reports expected within 1 hour; radiologists and clinicians chase radiographers for images (unfairly, but it happens).
- **Retained implant/device uncertainty** -- Patients unsure if they have pacemakers or metal implants; wrong decision = serious harm.

### Data Sources
- **RIS (Radiology Information System):** iSite, Agfa HealthCare, Sectra, Merge (Intelerad), Carestream
- **PACS:** Philips IntelliSpace, Sectra, GE Centricity
- **Quality management systems:** Datix, local QA logs (often spreadsheet-based)
- **Radiation dose monitoring:** DoseTrack, Radimetrics (Bayer)
- **Equipment management/CMMS:** Infor EAM, local biomedical engineering systems
- **Contrast media databases:** ESUR guidelines, iodine contrast reaction protocols (institutional)

### Proactive AI Opportunities
1. **"CT daily QA showed a CT number deviation of +7 HU on the water phantom -- just outside tolerance. The unit can still run but needs an engineer review today before the afternoon trauma list. Want me to log the fault and contact Siemens service?"**
2. **"Your personal radiation dosimetry badge results from last month show a slightly elevated dose (0.4 mSv -- within limits but double your usual). This is the second consecutive month. Want me to flag this to the Radiation Protection Supervisor for review?"**
3. **"There are 3 gadolinium MRI contrast vials in the fridge expiring Friday. Current booking doesn't have enough contrast-enhanced studies to use them. Want me to check the waitlist for any abdomen MRI patients who could be moved forward?"**
4. **"The CT scanner's annual service window is due in 3 weeks. Based on the schedule, Wednesday 26th has the lightest patient load for a 4-hour service window. Want me to block the time and notify the manufacturer?"**
5. **"Your ARRT CE cycle ends in 90 days. You need 6 more credits. There's an online CT dose optimisation course (4 credits) from ASRT running this month. Want me to add it to your CPD tracker and enrol?"**

---

## 11. Occupational Therapists

### Daily/Weekly Rhythm
- **Shift patterns:** Hospital OTs: 07:30/08:00-16:30/17:00, Monday-Friday (some weekend cover in acute settings). Community/home-based OTs: flexible, 08:00-17:00 with travel. Private practice: clinic-based, 08:00-17:00 or 09:00-18:00.
- **Patient load:** Hospital: 8-15 patients/day (mix of assessments and treatment sessions). Community: 5-8 home visits/day (travel time significant). Private outpatient: 6-10 sessions/day (45-60 min each).
- **Admin vs clinical split:** Hospital: 50% clinical, 50% admin (MDT notes, reports, equipment prescriptions, home assessment documentation). Community: 40% clinical, 60% admin and travel. Private: 70% clinical, 30% admin.
- **Weekly rhythm:** MDT meeting attendance (usually weekly in hospital). Home visits concentrated on certain days. Report writing typically done mid-week or Friday.

### Before Tasks
- Review patient notes -- last session outcomes, goals, ADL (Activities of Daily Living) status
- Check MDT notes for any clinical changes overnight (hospital) that affect OT plan
- Prepare equipment for the session -- adaptive equipment, splint materials, cognitive assessment tools, sensory kits
- Review home visit logistics -- address, access notes, whether a carer will be present, any safety concerns
- Print or prepare standardised assessment tools (AMPS, FIM, COPM, Barthel Index, ACE-III) for cognitive or functional assessments
- Check equipment prescription status -- wheelchairs, pressure care mattresses, bath seats prescribed: have they been delivered?
- For hand therapy: prepare thermoplastic splinting material, casting equipment, paraffin wax

### After Tasks
- Clinical notes -- functional progress, goal attainment, changes to treatment plan
- Assessment report writing -- OT reports are often lengthy, formal documents used for legal (medico-legal work), insurance, and housing purposes. These take 1-4 hours per report.
- Equipment prescription submissions -- formal motivation letters for medical aid funding of adaptive equipment
- Home modification recommendations -- written reports to council, housing department, or insurance for ramps, grab rails, bathroom modifications
- MDT documentation -- update team on OT input, discharge readiness
- Referrals -- to social work, physiotherapy, speech therapy, vocational rehabilitation
- Billing -- session claims, report charges, equipment prescription admin
- Follow-up scheduling

### Time-Sensitive Triggers
- **HPCSA/HCPC/NBCOT licence renewal:** Annual (HPCSA/HCPC) or every 3 years (NBCOT).
- **CPD requirements:** HPCSA: 30 CEUs/year. HCPC (UK): 2-year cycle. NBCOT (US): 36 PDUs per 3-year cycle.
- **Hand therapy certification renewal (CHT):** Every 5 years (US). Requires 4,000 hours of hand therapy practice + exam.
- **Equipment delivery follow-up:** Prescribed wheelchairs and adaptive equipment often take weeks or months. OT must track delivery status -- patient may be stuck at home or in hospital awaiting equipment.
- **Discharge planning timelines:** Hospital OTs work to discharge dates set by MDT. Equipment must arrive, home assessment must be done, and carer training completed before discharge date. Tight, time-sensitive workflow.
- **Medico-legal report deadlines:** OT medico-legal reports are commissioned with strict legal deadlines (court dates). Missing = professional and legal consequences.
- **Cognitive reassessment schedules:** Dementia/TBI patients need formal cognitive assessment every 6-12 months. This drives recall.
- **Driver assessment review:** Post-stroke or TBI patients may be on driving restrictions -- formal review date is legally significant.
- **Pressure sore risk re-assessment:** Patients with prescribed pressure care equipment should have equipment suitability re-assessed every 6 months (NICE/HPCSA guidelines).

### Stress / Anxiety Points
- **Report writing volume** -- OT reports are detailed and time-consuming. Medico-legal reports especially. Backlog anxiety is chronic.
- **Equipment funding battles** -- Medical aids frequently reject or delay equipment prescriptions. OTs spend significant time writing motivations and appealing decisions.
- **Discharge pressure** -- Hospital OTs feel caught between clinical readiness and hospital bed pressure. Discharging a patient before safe = liability risk.
- **Home visit safety** -- Lone working in unfamiliar environments, sometimes in high-risk areas. Many services have inadequate safety protocols.
- **Caseload breadth** -- OTs work across physical, mental health, and cognitive domains. Breadth is stimulating but also anxiety-inducing (staying current across multiple areas).
- **Patient goal misalignment** -- OT goals (function, independence) sometimes conflict with patient or family expectations (recovery = returning to previous life exactly as it was).
- **Equipment non-delivery** -- Prescribing equipment that never arrives, or arrives wrong, leaves OT in an awkward position with patient.

### Data Sources
- **EHR/Clinical systems:** Epic, Cerner, Meditech (hospital); Jane App, Cliniko (private)
- **Community equipment management:** MIDAS (UK), ARC (Assistive Technology Resource Centre) portals, local authority equipment stores
- **Medical aid portals:** For equipment motivation submissions and approvals (SA: Discovery, Bonitas)
- **Standardised assessment databases:** AMPS Online, FIM licensing system
- **Home modification databases:** OTDS (Occupational Therapy Dispensing Service, UK), local council housing databases
- **Medico-legal case management:** Needles, Roper, FilePro (legal firms' case management systems that OTs feed reports into)

### Proactive AI Opportunities
1. **"Mr. Abrahams' wheelchair was prescribed 6 weeks ago and there's no delivery confirmation in his notes. He's still in the ward and discharge was planned for next week. Want me to chase the supplier and flag this to the MDT?"**
2. **"You have a medico-legal report for the Kruger case due to the attorneys on Friday -- 3 days away. It's not started in the system. Do you want me to block 4 hours tomorrow morning and send a holding email to the attorneys?"**
3. **"4 patients on your community caseload are due for 6-month pressure care equipment reviews. 2 are over 7 months since last review. Want me to schedule home visits and flag these to the equipment supplier?"**
4. **"Mrs. Nel was discharged last Tuesday with a home exercise programme and carer training. Your protocol calls for a 2-week post-discharge phone check-in. That's due today -- want me to add it to your task list?"**
5. **"Your HPCSA renewal is in 8 weeks. You have 19 of 30 required CPD points. OTASA is running a sensory integration workshop next weekend -- 8 CPD points. Want me to register you and update your CPD log?"**

---

## 12. Cross-Role Patterns & Product Insights

### Universal Pain Points (Pulse should solve these across all roles)

| Pain Point | Roles Affected | Pulse Opportunity |
|---|---|---|
| **CPD/Licence deadline tracking** | All 11 roles | Universal compliance calendar with per-jurisdiction rules |
| **Patient recall management** | Dentists, Hygienists, Optometrists, Physios, OTs, Psychologists | Automated recall detection + reminder dispatch |
| **Documentation burden** | All roles, especially nurses, midwives, paramedics, therapists | Smart prompting to complete notes; template pre-fill |
| **Controlled drug discrepancy management** | Nurses, Pharmacists, Paramedics | Real-time CD count tracking with automatic discrepancy flagging |
| **Equipment calibration/service tracking** | Radiographers, Optometrists, Dentists, Paramedics | Equipment calendar with service window scheduling |
| **No-show management** | All outpatient/private roles | Automated waitlist filling, revenue recovery |
| **Medical aid/insurance claim follow-up** | All private practice roles | Aged claims alerting, automatic chase workflows |
| **Equipment procurement & delivery tracking** | OTs, Dentists (lab work), Optometrists | Prescription -> delivery monitoring with exception alerts |

---

### High-Value "First 30 Days" Features for Pulse

**Tier 1 -- Instant value, low integration complexity:**
1. CPD/licence deadline tracker with jurisdiction-specific rules
2. Patient recall scheduler with automated reminder dispatch
3. No-show recovery -- waitlist filling automation
4. Equipment calibration/service calendar
5. Medical aid claim age monitor

**Tier 2 -- Requires deeper data integration:**
6. Controlled drug discrepancy real-time flagging
7. Smart note completion prompting (incomplete records detection)
8. Lab/equipment order tracking (dental labs, optical labs, OT equipment)
9. Pre-authorisation window monitoring (physio, psychology sessions)
10. Prescription renewal cycle management (pharmacy)

---

### Integration Priority by Role

| Role | Primary System to Integrate | CPD Body | Key Trigger Data |
|---|---|---|---|
| Registered Nurse | Epic/Cerner/iSoft | SANC/NMC | MAR, CD register, patient vitals |
| Pharmacist | Unisolv/ScriptPro | SAPC/GPhC | CD register, cold chain logs, chronic Rx cycles |
| Physiotherapist | Cliniko/Jane App | HPCSA/HCPC | Auth codes, session count, equipment certs |
| Dentist | Exact/Dentrix/Salud | HPCSA/GDC | Recall dates, lab tracking, autoclave logs |
| Dental Hygienist | Exact/Dentrix | HPCSA/GDC | Perio recall cycles, waterline testing |
| Optometrist | Optomate/Acuitas | HPCSA/GOC | CL expiry dates, spectacle lab orders |
| Psychologist/Therapist | SimplePractice/TheraNest | HPCSA/BPS | Auth sessions remaining, supervision hours |
| Midwife | Badgernet/K2 | NMC/SANC | PKU timing, antenatal screening windows |
| Paramedic | ImageTrend ePCR | HPCSA/NREMT | CD register, defibrillator tests, vehicle checks |
| Radiographer | RIS/PACS | HPCSA/HCPC | QA logs, dosimetry, contrast expiry |
| Occupational Therapist | Cliniko/Epic | HPCSA/HCPC | Equipment delivery, medico-legal deadlines |

---

### The "How Did It Know?" Moments -- What Makes Pulse Feel Like Magic

These are the moments that will create word-of-mouth and user loyalty. Not generic reminders -- **specific, contextual, proactive awareness:**

1. **The Friday afternoon note sweep** -- "You have 4 incomplete clinical notes and it's 16:45 on Friday. Two involve patients with elevated risk. Do you want to finish them now or set a reminder for tonight?"

2. **The silent cascade** -- "Dr. Patel referred a patient to you on Tuesday. They haven't called to book yet -- it's been 72 hours. Want me to reach out?"

3. **The approaching cliff** -- "Thembi's medical aid has 1 session left on the current auth. Her next appointment is in 4 days. Should I apply for a new auth now before it lapses?"

4. **The thing nobody tracks** -- "Your EpiPen expires in 8 days. It's not on any system -- I found it because I track everything in your emergency kit log."

5. **The revenue leak** -- "Your 60-day claim ageing report: R18,400 in outstanding medical aid claims. 6 accounts have had no follow-up in over 30 days. Want me to send chase requests?"

6. **The professional cliff** -- "Your HPCSA registration lapses in 21 days. You're 4 CEU points short. I found a free SASP webinar this Thursday evening that earns 5 points."

7. **The safety net** -- "Marcus hasn't attended his last 2 sessions and hasn't responded to messages. Your own policy flags this after 2 missed sessions. Want me to generate a welfare check protocol?"

8. **The lab chase** -- "The crown for Mr. Botha (fit appointment: Friday) hasn't been confirmed as received from ProLab. It's Wednesday 09:00. Should I call them now?"

---

*Research complete. Ready for Pulse product design phase.*
*All role data grounded in real-world workflows, jurisdiction-specific regulatory requirements (SA/UK/US/AU), and validated against current professional body standards.*
