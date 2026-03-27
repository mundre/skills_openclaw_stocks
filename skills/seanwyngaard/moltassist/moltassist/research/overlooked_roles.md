# Pulse Research: Overlooked but Large Role Categories
*Deep practical research for proactive AI assistant product design*
*Generated: March 2026*

---

## RESEARCH PHILOSOPHY

These aren't generic job descriptions. Each section is written to answer one question: **what would make a person in this role say "how did it know?"** -- the moment a proactive AI earns trust by surfacing something real, at the right time, before they had to ask.

The differentiator for Pulse is not just being reactive when asked. It's knowing the rhythms, the triggers, the invisible anxieties of each role -- and acting on them unprompted.

---

# SECTION 1: HEALTHCARE ADJACENT & SPECIALIST

---

## 1.1 PHARMACY MANAGERS

### What makes this role unique
Pharmacy managers sit at the intersection of retail, clinical care, and regulatory compliance. Unlike hospital pharmacists, they own P&L responsibility, staff management, AND dispensing oversight simultaneously. The pressure is tripled: a mistake can harm a patient AND tank the business AND trigger regulatory sanctions.

### Daily/Weekly Rhythm
**Daily:**
- Pre-open: check overnight fax/e-script queue, controlled drug register balance, fridge temp logs
- Morning dispensing rush (8-10am): high script volume, repeat prescriptions
- Midday lull: ordering, stock checks, staff scheduling
- Afternoon: more scripts, OTC consultations, end-of-day cash reconciliation
- After close: review the dispensing system exceptions, check anything flagged by dispensing software

**Weekly:**
- Monday: review previous week's sales, controlled drug counts (some jurisdictions require daily)
- Wednesday/Thursday: place main stock orders
- Friday: prepare for weekend staffing gaps, ensure locum is briefed
- Monthly: full controlled drug stock audit, staff performance, expiry date checks

### Before Tasks
- Check dispensing queue backlog before unlocking the doors
- Confirm fridge temperatures are within range (2-8C for vaccines, insulin, certain eye drops)
- Check if any urgent or emergency scripts came in overnight
- Verify the controlled drugs register is balanced from the previous day
- Check if any key staff called in sick -- scramble for locum cover

### After Tasks
- Reconcile daily dispensing count against cash/card receipts
- Log controlled drug dispensings for the day
- Check if any scripts were rejected by insurance/PBS/NHS and need follow-up
- Flag anything for the next dispenser coming in
- Lock narcotics cabinet and sign off handover

### Time-Sensitive Triggers (the sneaky ones)
- **Drug shortages** -- a commonly dispensed medication goes on backorder overnight; patients will come in expecting it tomorrow
- **Expiry dates** -- a batch of medication near expiry that needs to be returned or written off
- **Controlled drug discrepancy** -- even a 1-tablet count mismatch triggers mandatory reporting
- **Locum no-show** -- staff member doesn't arrive; can't legally open without a registered pharmacist
- **Script fraud flags** -- a patient presents with a script that looks altered or the prescriber's DEA/provider number doesn't match
- **Fridge failure** -- a fridge alarm that went off overnight, possibly compromising vaccine stock
- **Regulatory inspection notice** -- boards rarely give much warning
- **Recall notice** -- TGA/MHRA/FDA sends a drug recall; they now have to identify and contact every patient who received the batch

### Stress/Anxiety Points
- Controlled drug counts that don't balance -- the sinking stomach feeling
- A dispensing error that made it out the door
- Understaffing on a busy day with no backup
- Being both the pharmacist on duty AND managing the business (calls, emails, staff dramas)
- Insurance/PBS claim rejections that only surface weeks later but affect cash flow now
- Patient complaints escalating to the regulatory board
- Keeping up with formulary changes, new drug interactions, updated guidelines -- it never stops

### Data Sources
- Dispensing software (Fred Dispense, Minfos, RxOne, Kroll, ScriptPro)
- Drug information databases (MIMS, AMH, BNF, Micromedex)
- PBS/Medicaid/NHS prescription databases
- Controlled drug registers (physical + digital)
- Fridge temperature loggers (IoT)
- Supplier ordering portals (API Healthcare, Sigma, Symbion, McKesson)
- Regulatory board alerts (TGA, AHPRA, GPhC, DEA)
- Drug recall alerts (Medsafe, FDA MedWatch, TGA recalls)

### Proactive AI Opportunities -- "How Did It Know?"

> *"Hey -- Symbion just flagged metformin 500mg as on backorder. You dispensed 47 scripts for it last week. Want me to draft a message to those patients and find the nearest pharmacy with stock?"*

> *"Three of your vaccine fridge items expire in the next 12 days. The return window with your supplier closes in 4. Should I raise a return request?"*

> *"It's Wednesday 7am and there's no locum confirmed for Saturday. Last time this happened you called PharmacyLocums at 8am. Want me to send the request now?"*

> *"There's a TGA recall on Lot #XY4421 of atorvastatin 40mg. You have 3 patients on that batch. I've drafted a recall notification SMS -- want to review before I send?"*

> *"Your controlled drug register for pethidine is 2 tablets down from the expected count. You may want to review this before close of day -- discrepancies need reporting within 24 hours."*

---

## 1.2 OPTICIANS / DISPENSING OPTICIANS

### What makes this role unique
Dispensing opticians are not optometrists -- they don't examine eyes. They translate a prescription into actual eyewear, which requires deep technical knowledge of optics, lens types, frame fitting, and patient face geometry. They also run what is effectively a retail business where the average transaction is $400-$1200. The unique stress: they are personally responsible for a patient's vision clarity. A wrong PD (pupillary distance) measurement means weeks of headaches and a furious return.

### Daily/Weekly Rhythm
**Daily:**
- Morning: check lab orders due in, check open jobs that need fitting appointments
- Frame consultations and lens recommendations (mix of new and returning patients)
- Fitting and adjustments throughout the day
- Afternoon: follow up on lab delays, call patients whose glasses are ready
- End of day: check tomorrow's appointment list, confirm any outstanding lab orders

**Weekly:**
- Monday: review lab turnaround times, anything overdue?
- Mid-week: insurance billing reconciliation
- Friday: patient recalls (annual check reminders), follow up no-shows

### Before Tasks
- Review the day's appointments -- any complex prescriptions or special lens orders?
- Check the lab delivery for the day -- which jobs came in?
- Confirm staff coverage for fitting appointments
- Check if any outstanding jobs are past their promised date

### After Tasks
- Log which glasses were dispensed and whether adjustments were needed
- Update patient records with final PD measurements and fitting notes
- Flag any returns or remakes to the lab
- Set reminders for patients to return in 2 weeks if adapting to progressives

### Time-Sensitive Triggers
- **Lab delay** -- patient was promised glasses by Friday, it's Thursday and the lab hasn't shipped yet
- **Remake request** -- patient is unhappy 5 days after collection; if it's a lab error, they may reimburse; if it's a measurement error, it's on the practice
- **Progressive lens adaptation failure** -- patient calls at the 2-week mark saying they still can't see properly; this is the critical intervention window
- **Annual recall window** -- a patient's contact lens prescription expires in 3 days; they'll need to book or get an emergency supply
- **Insurance authorisation expiry** -- some vision insurance pre-auths expire after 30 days; an unclaimed auth means a lost job
- **Frame discontinued** -- lab calls to say the frame the patient chose is discontinued; need to contact patient quickly before fabrication begins
- **Tray stock running low** -- demo lens trays or popular frame styles running out before market visit

### Stress/Anxiety Points
- A patient insisting their glasses are wrong when the measurements were correct -- but you can't be 100% sure
- A progressive lens remake that the lab won't cover because they say the prescription wasn't transcribed correctly
- An insurance claim that bounces back weeks later
- Managing appointment flow AND lab orders AND frame reps AND patient follow-ups solo
- A patient whose vision has measurably declined since last year -- should they have been referred sooner?

### Data Sources
- Practice management software (Optomate, Specsavers systems, Revolution EHR)
- Lab order portals (Essilor, Hoya, Zeiss, local lab portals)
- Insurance portals (VSP, EyeMed, Medibank, Specsavers insurance)
- Patient recall lists (anniversary-based, prescription expiry)
- Frame inventory system

### Proactive AI Opportunities -- "How Did It Know?"

> *"Mr. Patel's progressive lenses were collected 12 days ago. He hasn't called, but this is the typical adaptation window. Want me to send a quick check-in message?"*

> *"Your lab portal shows 3 jobs are past their promised date. The oldest was due Tuesday -- should I send a chase message to the lab?"*

> *"You have 14 patients whose annual contact lens Rx expires this month. Want me to send renewal reminder messages?"*

> *"Sarah Kim's insurance pre-authorisation expires in 5 days and the order hasn't been placed yet. Her frame selection is confirmed -- should I flag this for urgent ordering?"*

> *"The frame brand rep is visiting next Tuesday. Based on your current tray stock, your Lindberg and Oliver Peoples selections are running low -- want me to prep a reorder list?"*

---

## 1.3 VETERINARY NURSES

### What makes this role unique
Vet nurses are the emotional and clinical backbone of a veterinary practice, but unlike human nurses, they also have to manage anxious *owners* as much as anxious *patients*. The emotional weight is different -- animals can't consent or communicate, and the financial dimension of treatment decisions is ever-present ("we can save him, but it'll cost $4,000"). Many vet nurses are emotionally exhausted from grief (euthanasia) and from being the bearers of bad news. Burnout and compassion fatigue are endemic.

### Daily/Weekly Rhythm
**Daily:**
- Pre-clinic: check inpatient animals (any that stayed overnight), check surgical prep list
- Morning surgeries/procedures: prep, anaesthesia monitoring, scrubbing in
- Afternoon: consultations support, recovery monitoring, discharge appointments
- Late afternoon: kennel checks, evening medications, ward clean
- End of day: handover for any overnight patients or on-call

**Weekly:**
- Monday: surgery schedule, stock check of anaesthetic agents and consumables
- Wednesday: often a heavy consult day
- Ongoing: CPD (continuing professional development) credits required annually
- Monthly: drug register audit, autoclave certification, sharps disposal

### Before Tasks
- Morning inpatient check: are all overnight patients stable?
- Confirm surgical prep -- correct patient, correct procedure, consent form signed
- Check controlled drug levels before first surgery
- Review the consult diary for complexity (e.g., aggressive breeds, known difficult owners)

### After Tasks
- Post-op monitoring and documentation
- Update patient records (weight, temp, treatment notes)
- Drug usage logged against the controlled drug register
- Owner discharge instructions -- printed AND verbally explained
- Flag anything for overnight staff or on-call vet

### Time-Sensitive Triggers
- **Anaesthetic emergency** -- a patient's vitals dropping during surgery; seconds matter
- **Post-op complication** -- patient that went home yesterday is being brought back as an emergency
- **Drug expiry** -- controlled drugs or surgical consumables near expiry (regulatory requirement to remove from use)
- **Annual CPD deadline** -- nurses often leave this to the last month of their renewal period
- **Vaccination reminder surge** -- spring/summer brings a flood of annual vaccination reminders needing booking
- **Kennel cough outbreak** -- one boarding dog presents with symptoms; potential exposure to others
- **Euthanasia scheduling** -- a client called to book a euthanasia appointment; these need particular handling (who is the vet, is there a private room, is there a sympathy card ready)

### Stress/Anxiety Points
- Compassion fatigue -- multiple euthanasias in a week takes a toll
- Being alone in the practice when an emergency comes in
- An owner who can't afford treatment asking "what would YOU do?" (impossible position)
- A controlled drug count that doesn't balance
- Being blamed for an outcome that was the vet's decision
- Keeping up with CPD requirements while working full time

### Data Sources
- Practice management software (RxWorks, VetSoft, Provet Cloud, EzyVet)
- Controlled drug registers
- CPD tracking platforms (VNCA, RCVS, NAVTA portals)
- Vaccination/reminder systems within PMS
- Anaesthetic monitoring equipment logs
- Surgical schedule

### Proactive AI Opportunities -- "How Did It Know?"

> *"Bella Thompson had her surgery on Monday. It's now day 3 post-op -- she was discharged with wound care instructions. Worth a quick follow-up call to check she's eating and no swelling?"*

> *"Your CPD renewal deadline is in 47 days and you're 3.5 hours short of your required 15. There's a free RCVS webinar on pain management this Thursday -- want me to book it?"*

> *"Max (kennel occupant 3) has been showing reduced appetite for 2 days. He's been here 4 days total -- this might be stress eating, but worth flagging to the duty vet."*

> *"You have 23 vaccination reminder letters going out this week. Three of the clients haven't responded to the last two reminders. Want me to flag them for a phone call?"*

> *"It's been 6 months since your autoclave last had its formal certification service. Regulatory guidelines recommend annual servicing -- want me to book that?"*

---

## 1.4 DENTAL PRACTICE MANAGERS

### What makes this role unique
Dental practice managers are business operators who don't hold a clinical qualification but are responsible for everything *around* the clinical work: scheduling, billing, insurance, HR, compliance, and patient experience. The unique challenge: they're managing highly skilled clinicians (dentists) who often have strong personalities and may not respect non-clinical management decisions. Also, dental revenue is heavily dependent on chair utilisation -- a gap in the appointment book is money directly lost, unlike most service businesses.

### Daily/Weekly Rhythm
**Daily:**
- Morning: review the day's schedule, identify gaps, call the cancellation/waitlist
- Confirm all patients have completed consent forms and insurance pre-auths
- Coordinate with dental assistants on room prep and sterilisation compliance
- Review overnight voicemail/online booking requests
- Afternoon: billing and insurance claim submissions, patient account queries
- End of day: prepare next-day schedule, identify gaps, check tomorrow's lab work has arrived

**Weekly:**
- Monday: weekly revenue snapshot, gap analysis in the schedule
- Tuesday/Wednesday: insurance follow-up on pending claims
- Thursday: staff check-ins, rostering for next week
- Friday: end-of-week reconciliation, any outstanding patient account issues

### Before Tasks
- Chair utilisation check -- any gaps in the next 48 hours?
- Lab work confirmed for tomorrow's cases (crowns, dentures, bridges)
- Insurance pre-auths in place for tomorrow's major work
- Sterilisation log compliance check

### After Tasks
- Daily billing run -- submit claims for the day's work
- Log any insurance denials for follow-up
- Update patient accounts for any co-pays collected
- Document any patient complaints or incidents

### Time-Sensitive Triggers
- **Same-day cancellation** -- a crown appointment or major procedure gap is $500-$1500 lost revenue; the window to fill it is 2-3 hours
- **Lab delay** -- patient booked for crown fit, lab hasn't delivered; need to reschedule before patient arrives
- **Insurance pre-auth expiry** -- some dental pre-auths expire after 60-90 days; if treatment is delayed, they need resubmission
- **OSHA/infection control audit** -- unannounced inspections require logs to be current
- **Staff conflict escalation** -- a dentist/DA relationship issue that needs to be managed before it affects the schedule
- **Patient account aging** -- accounts >90 days overdue start to become uncollectible
- **Year-end insurance benefits deadline** -- many patients have "use it or lose it" benefits resetting December 31; this creates a November/December booking surge if managed proactively

### Stress/Anxiety Points
- A dentist running late cascading through the whole day's schedule
- A patient complaint about billing that turns into a dispute
- Insurance claim denials that require extensive documentation
- Staff no-show with no backup (a dental assistant is legally required in many jurisdictions)
- Sterilisation compliance gaps discovered during a log review
- Managing a dentist owner who doesn't understand (or care about) the business side

### Data Sources
- Practice management software (Dentrix, Eaglesoft, Curve Dental, Exact by Software of Excellence)
- Insurance portals (Delta Dental, Cigna, MetLife provider portals)
- Dental lab portals
- ADA/CDA/BDA billing code updates
- OSHA compliance platforms
- Accounts receivable aging reports

### Proactive AI Opportunities -- "How Did It Know?"

> *"There's a 90-minute gap in Dr. Chen's schedule tomorrow at 2pm. You have 4 patients on the waitlist who requested that time slot -- want me to send them an availability text?"*

> *"The lab hasn't confirmed delivery for Mrs. Rossi's crown fitting booked for Thursday. It's Tuesday -- should I contact the lab now while there's still time to reschedule if needed?"*

> *"You have 34 patients whose year-end dental benefits haven't been used. If they lapse December 31, you're potentially leaving $18k in chair time on the table. Want me to draft a 'use your benefits before December' campaign?"*

> *"I notice 12 insurance claims submitted more than 60 days ago haven't been marked as paid or denied. These may need chasing -- want me to generate a follow-up list?"*

> *"Your sterilisation log has a gap on March 14 -- if you're audited, that's a compliance flag. Want to document a note for that date while you still remember what happened?"*

---

## 1.5 MEDICAL PRACTICE MANAGERS

### What makes this role unique
Medical practice managers run the business of a GP/specialist clinic, navigating Medicare/NHS/insurance billing, regulatory compliance, GP registration requirements, and patient flow simultaneously. The key differentiator from a hospital administrator: they're running a small business (usually 2-8 GPs) with enterprise-level compliance requirements and no enterprise support team. They often carry compliance knowledge that the GPs themselves don't have -- which creates a peculiar authority dynamic.

### Daily/Weekly Rhythm
**Daily:**
- Open: check appointment book utilisation, review overnight online bookings
- Confirm doctors are in -- any sick calls, locum needed?
- Triage urgent appointment requests
- Monitor billing submissions and Medicare rejections
- End of day: billing reconciliation, any patient incidents documented

**Weekly:**
- Mon/Tue: payroll processing, rostering next week
- Wed: billing and accounts receivable review
- Thu/Fri: credentialing checks, any upcoming expiries on doctor registrations

**Monthly/Annually:**
- Accreditation (AGPAL, RACGP, QPA, CQC) -- significant prep work
- AHPRA/GMC/MCNZ registration renewals for all GPs
- Medical indemnity renewal
- Professional development logs for the practice

### Before Tasks
- Any doctor reporting sick? Rearrange patients, activate locum protocol
- Medicare provider number active for all billing doctors (new doctors especially)
- Flu vaccine stock levels before flu season campaigns
- Appointment book gaps flagged for recall campaigns

### After Tasks
- Medicare bulk billing submissions for the day
- Any after-hours advice line callbacks logged
- Patient complaints documented
- Staff incidents documented

### Time-Sensitive Triggers
- **Doctor registration lapse** -- an AHPRA/GMC registration expires; that doctor cannot legally see patients from midnight on the expiry date
- **Medicare provider number issue** -- a billing error that flags a provider number means claims bounced and potentially suspended
- **Accreditation audit notice** -- often given 6-8 weeks' notice; there's a huge amount of prep
- **Doctor resignation** -- gives 3 months notice; Medicare patient records, billing setup, recruitment all kick off immediately
- **Drug representative visit** -- practice policy on rep access needs to be enforced
- **Mandatory reporting obligation** -- if a staff member reports concerns about a doctor's health/conduct, there are legal obligations with tight timelines
- **PBS/formulary change** -- a commonly prescribed drug changes its subsidy status; patient impacts need to be communicated

### Stress/Anxiety Points
- A doctor who won't comply with documentation or billing standards
- Being responsible for compliance outcomes that depend on doctor behaviour you can't fully control
- Managing patient complaints that implicate a doctor (they push back; you're in the middle)
- Keeping accreditation documentation current when doctors don't fill in forms
- Maintaining confidentiality during staff disputes involving clinical staff
- Cash flow gaps when Medicare payments are delayed

### Data Sources
- Practice management software (Best Practice, Medical Director, Genie, EMIS, SystmOne)
- Medicare Online/HPOS, NHS BSA portals
- AHPRA/GMC/MCNZ registration portals
- Accreditation body portals (AGPAL, RACGP, QPA, CQC)
- Payroll software
- Medical indemnity insurer portals (MDA, MIPS, MDU)

### Proactive AI Opportunities -- "How Did It Know?"

> *"Dr. Nguyen's AHPRA registration expires in 31 days. Renewal applications typically take 7-10 business days. You'll want to chase her for the renewal application this week."*

> *"Your AGPAL accreditation assessment is in 8 weeks. Based on your last assessment report, 3 areas were flagged for improvement -- want me to pull those up so you can check current status?"*

> *"Your flu vaccine stock is at 140 doses. Last year you administered 312 doses in the same 6-week window. At current appointment pace, you may run short by week 4. Want me to draft a reorder request?"*

> *"There are 47 outstanding Medicare claims from last month. 12 are flagged with error code 73 (incorrect provider number for service). This is likely the new billing setup for Dr. Patel -- want me to pull those for review?"*

> *"Dr. Williams mentioned she's moving to Brisbane in 6 months. You haven't started recruitment yet -- the average GP vacancy takes 4-6 months to fill. Want me to draft a job listing?"*

---

## 1.6 PHYSIOTHERAPY CLINIC OWNERS

### What makes this role unique
Physio clinic owners are clinicians turned business owners -- most of them never got business training. They're great at treating patients; they often struggle with the business side. The unique dynamic: they often still carry a clinical caseload (seeing their own patients) while managing staff, billing, marketing, and operations. They have a split identity that makes time incredibly scarce. Also, physiotherapy has strong insurance dependencies (WorkCover, TAC, DVA, private health) that create significant billing complexity.

### Daily/Weekly Rhythm
**Daily:**
- See their own patient caseload (often 6-10 appointments)
- Between patients: answer emails, check in with reception, handle staff queries
- Lunch: billing, client progress notes (often behind from the morning)
- Afternoon: more patients, scheduling requests, insurance pre-auths
- After clinic: notes completion, staff communication, business review

**Weekly:**
- Monday: check booking rates for the week, identify slow spots
- Wednesday: any insurance pre-auth requests that need processing
- Friday: end-of-week revenue check, staff payroll review

**Monthly:**
- WorkCover/TAC claim reconciliation
- Marketing review (new patient acquisition, referral sources)
- Staff performance reviews

### Before Tasks
- Notes from yesterday completed before first patient (if not done the night before)
- Check if any DVA/WorkCover approvals need renewal before treating today
- Staff attendance confirmed
- Any new patient referrals to review

### After Tasks
- Clinical notes completed (medicolegal requirement)
- Insurance claim submissions
- Referral letters to GPs or specialists
- Rebooking patients who need follow-up

### Time-Sensitive Triggers
- **Insurance approval lapse** -- WorkCover/TAC often approve a set number of sessions; if the approval lapses, the next session can't be billed; patient might arrive not knowing
- **Referral expiry** -- some private health funds and government schemes require a current GP referral; these expire after 12 months
- **Staff leave creating gaps** -- a physio takes leave and their patient caseload needs redistributing with minimal patient disruption
- **DVA treatment plan renewal** -- Department of Veterans Affairs approvals need renewal; an elderly veteran with complex needs misses a session while admin catches up
- **Competitor opening nearby** -- a new clinic opens 500m away; immediate marketing response needed
- **CPD renewal deadline** -- the owner's own APA/HCPC registration requires annual CPD; often neglected due to business demands
- **Late cancellation surge** -- multiple patients cancelling same day creates empty chairs = lost revenue

### Stress/Anxiety Points
- The split identity -- "am I a clinician or a business owner today?" answer: both, always
- Insurance funding cuts affecting patient volumes overnight (policy changes hit without warning)
- A staff physio resigning and taking some of their patient base
- Being behind on clinical notes and knowing it's a medicolegal liability
- Marketing -- "I'm a physio, not a marketer, but if I don't get referrals the business dies"
- Keeping up with evidence-based practice while running a business

### Data Sources
- Practice management (Cliniko, Power Diary, Nookal, Jane App)
- WorkCover/TAC/DVA portals (jurisdiction-specific)
- Private health fund portals (Medibank, BUPA, HCF, NIB)
- APA/HCPC CPD tracking
- Google Business profile (reviews, search ranking)
- GP referral tracking

### Proactive AI Opportunities -- "How Did It Know?"

> *"Three of your WorkCover patients have approval numbers expiring this week. You'll need to request extensions before treating them Friday -- want me to draft the extension requests?"*

> *"Your Tuesday schedule has 4 gaps -- your utilisation is tracking at 67% this week. You have 8 patients on your waitlist requesting Tuesday afternoon. Want me to send them availability offers?"*

> *"It's been 4 weeks since your Google Business listing had a new review. Your closest competitor got 6 new 5-star reviews last month. Want to send a review request to recently discharged patients?"*

> *"Sarah Chen gave 3 weeks notice today. She has 31 patients currently active. Want me to draft a patient communication about the transition and flag which cases need urgent clinical handover?"*

> *"Your APA CPD log shows 8 hours completed against a 20-hour annual requirement. The renewal deadline is 10 weeks away. There's a manual therapy course running next month -- want me to book it?"*

---

# SECTION 2: SKILLED SPECIALIST TRADES

---

## 2.1 SECURITY GUARDS / SECURITY COMPANY OWNERS

### What makes this role unique (split by role)

**Security Guard (individual):** Works in isolation, often at night, in high-responsibility low-stimulation environments. The cognitive load is inverse to what it looks like -- long stretches of boredom punctuated by sudden high-stress events. Documentation and incident reporting are critical but often poorly done. Guards are also uniquely exposed to legal liability -- they can be held personally responsible for excessive force or improper detention.

**Security Company Owner:** Runs a rostering and logistics nightmare. The product they sell is "someone will be there" -- and if someone isn't there, they've failed the contract and exposed their client to liability. The defining stress is roster coverage: sick calls at 2am, guard no-shows, client emergencies. Also: regulatory compliance (licensing, criminal record checks, insurance) and the constant race between pricing and labour costs.

### Daily/Weekly Rhythm (Company Owner)
- Pre-dawn: any overnight incidents reported? Any shift gaps for the coming morning?
- Morning: roster confirmation for the day, any client calls/complaints overnight
- Midday: invoicing, new client enquiries, quotes
- Afternoon: training compliance checks, guard performance reviews
- Evening: confirm night shift coverage -- this is the high-anxiety window
- Weekend: almost never fully off; always on call for coverage gaps

### Before Tasks (Guard)
- Site briefing with outgoing shift -- any incidents, any known risks for tonight?
- Equipment check: radio, torch, PPE, access cards
- Patrol route review
- Check if any special instructions from the client (VIP visit, maintenance work, etc.)

### After Tasks (Guard)
- Incident report completed for anything above routine
- Patrol log submitted
- Handover brief to incoming guard
- Any equipment faults logged

### Time-Sensitive Triggers
**Company Owner:**
- **Guard calls in sick at 2am** -- need a replacement for a 6am shift; the client contract may have a penalty clause
- **Guard licence expiry** -- a guard working with an expired licence is a massive liability; licensing boards do random checks
- **Client contract renewal** -- often 12-month contracts with 30/60-day notice requirements; renewals sneak up
- **Insurance renewal** -- public liability for security companies is expensive and time-critical
- **Use-of-force incident** -- as soon as it's reported, legal and insurance notifications need to go out within 24 hours
- **CCTV footage preservation** -- if an incident occurs, footage overwrites in 7-30 days; preservation requests need to be immediate

**Guard:**
- **Medical emergency on site** -- first response, call for help, incident report
- **Suspicious person/vehicle** -- decision to engage or escalate; wrong call = liability
- **Fire alarm activation** -- real or false; the guard has to treat it as real every time

### Stress/Anxiety Points (Company Owner)
- The 2am phone call: "I can't come in tonight"
- A client threatening to cancel because of one bad incident
- A guard who did something that's going to cost the business legally
- Undercutting competitors on price to win contracts, then struggling to pay guards adequately
- Keeping every guard's licence, first aid cert, and criminal check current

### Data Sources
- Rostering software (Deputy, Humanforce, Guardso, TrackTik)
- Licensing portals (SIRA, SIA, state police portals)
- Incident reporting platforms
- Client contract management
- Payroll software

### Proactive AI Opportunities -- "How Did It Know?"

> *"James Okafor's security licence expires in 19 days. He's rostered for 8 shifts before then. You'll need him to renew or have a replacement ready."*

> *"Your Westfield contract auto-renews in 45 days. Based on last year, they sent a renewal review request 30 days before. If you want to negotiate rates this cycle, you should initiate contact this week."*

> *"There was a use-of-force incident logged at the George St site at 11:40pm. Your insurance policy requires notification within 24 hours of an incident. Want me to draft the notification?"*

> *"Tonight's night shift at Marina Bay has only 2 of 3 positions filled. The last time you had a gap like this, you called Marcus first -- want me to send him an availability request now?"*

> *"You have 6 guards whose first aid certifications expire within 90 days. The next available course in your area is March 22. That's 4 seats -- want me to book them?"*

---

## 2.2 PEST CONTROLLERS

### What makes this role unique
Pest control is a *seasonal and reactive* business -- demand spikes unpredictably (cockroach season, termite swarm season, rodent invasion in winter) and most customers call in a state of disgust or panic. The job requires chemical handling expertise, regulatory licensing, and physical endurance (crawling in subfloors, working in heat). What makes it unique for Pulse: **the follow-up failure rate is enormous** -- pest control requires follow-up treatments at 2/4/8-week intervals, but these are often forgotten by both the client and the technician, leading to treatment failures and refund demands.

### Daily/Weekly Rhythm
- Early morning: check the day's job list, load the van, mix chemicals for the first jobs
- Job execution: travel -> inspect -> treat -> document
- Between jobs: update job notes on mobile, confirm next appointment
- End of day: unload unused chemicals safely, update job cards, submit invoices
- **Weekly:** review all jobs that need follow-up in the next 2 weeks; check chemical stock

### Before Tasks
- Review today's jobs: what pests, what chemicals, access requirements?
- Chemical inventory check -- enough of the right stuff for today?
- Check any site access instructions (building managers, alarm codes)
- PPE check

### After Tasks
- Chemical usage logged (regulatory requirement)
- Service report completed and signed by client (or emailed)
- Invoice raised
- Follow-up appointment booked (this is often skipped, creating problems 4 weeks later)
- Hazardous waste disposal logged if applicable

### Time-Sensitive Triggers
- **Termite swarm call** -- homeowner sees flying termites; this is an emergency response call; first mover advantage matters, and active termite damage can cost $50k+
- **Cockroach treatment follow-up missed** -- at 4 weeks, if no follow-up, the treatment fails and the client blames the pest controller
- **Chemical expiry** -- diluted chemicals degrade; mixed solutions often need to be used within 24 hours
- **Licence renewal** -- chemical handling licence, business licence; state-specific, often annual
- **Weather window** -- some treatments (termite barrier, external spray) can't be done in rain; schedule needs to flex
- **MSDS/SDS updates** -- chemical safety data sheets need to be current; regulatory inspections check this
- **Seasonal surge** -- January/February in Australia = cockroach season; not having enough capacity pre-booked means losing jobs to competitors

### Stress/Anxiety Points
- A treatment that "didn't work" -- often because the client didn't follow prep instructions, but they want a refund
- Working in confined spaces alone (subfloors, roof voids)
- Chemical exposure risks -- are safety protocols actually being followed every single time?
- The weather ruining a fully booked day of outdoor treatments
- Competing on price against operators who cut safety corners

### Data Sources
- Job management apps (ServiceM8, Jobber, Tradify, AroFlo)
- Chemical regulatory portals (APVMA in Australia, EPA in US)
- Licence renewal portals
- Weather apps (Bureau of Meteorology, Weather.com)
- Supplier portals (Pest-Ex, Agserv, Bell Laboratories)

### Proactive AI Opportunities -- "How Did It Know?"

> *"You have 14 jobs from 4 weeks ago that had a 4-week follow-up note. None have been booked yet. Want me to send follow-up SMS to all 14 clients?"*

> *"It's forecast to rain Thursday and Friday. You have 6 external barrier spray jobs booked those days. Want me to contact those clients to reschedule?"*

> *"Your chemical licence renewal is due in 3 months. The renewal application takes 4-6 weeks to process. Want me to start the application?"*

> *"You've had 3 termite enquiry calls in the last week from the Oakdale area -- that's unusual clustering. Termite swarm season starts in 4 weeks. Want me to draft a pre-season termite offer to your Oakdale client list?"*

> *"Your Biflex Ultra diluted mix from Monday is 72 hours old. Per your SDS protocol, it should be used or disposed of within 48 hours. There's a standing job for 10am -- but you may want to mix fresh for that one."*

---

## 2.3 POOL / SPA TECHNICIANS

### What makes this role unique
Pool technicians are chemistry technicians + plumbers + customer service + seasonal business operators all in one. The unique aspect: **pool chemistry has a time-critical window** -- if a pool goes green or a pump fails, the client wants it fixed *now* and the technician needs to be there within 24-48 hours or the problem compounds (algae blooms, equipment corrosion). Regular service clients expect predictable visits and will notice immediately if the schedule slips.

### Daily/Weekly Rhythm
- Morning: check the day's service route (geographically clustered)
- Each stop: test water chemistry, adjust, check equipment, clean filters
- Between stops: update job notes, flag any that need a return visit or parts
- Afternoon: chemical supply check, quote any repair jobs identified during service
- End of day: chemical stock reconciliation, next day's route prep

**Weekly:**
- Monday: recurring service route planning for the week
- Friday: review any outstanding repair jobs, parts orders
- Seasonal: pool opening/closing services (spring/autumn) -- intensive but predictable surge

### Before Tasks
- Route optimised? (Chemistry matters less if you're 3 hours late due to bad routing)
- Chemical stock loaded -- enough for all today's pools?
- Any customer follow-ups from last week flagged?
- Any pools with known issues (recurring algae, equipment on its last legs)?

### After Tasks
- Service report updated per pool (chemistry readings, chemicals added, observations)
- Parts ordered for any equipment issues identified
- Client notified of any issues requiring additional work
- Invoice raised for any add-on services

### Time-Sensitive Triggers
- **Green pool emergency** -- a client discovers their pool is algae-blooming; they want it fixed before the weekend
- **Equipment failure** -- a pump or chlorinator fails; without circulation, the chemistry collapses fast
- **Pump bearing failure** -- a grinding noise that becomes a locked pump within days; if caught early it's a $200 bearing replacement; missed, it's a $900 pump
- **Chemical imbalance cascade** -- low sanitiser -> algae -> cloudiness -> filter clogging -> pump strain; each step makes the next worse
- **Pre-summer opening surge** -- every client who "closed" their pool for winter calls in the same 2-week window wanting it opened
- **Storm aftermath** -- heavy rain changes pool chemistry dramatically; clients expect a visit the next day
- **Chemical supplier price increase** -- bulk buying before a price rise can significantly affect margins

### Stress/Anxiety Points
- A pool going green between service visits (especially before a party or event)
- Equipment failure on a Saturday when suppliers are closed
- A client who thinks they can manage their own pool chemistry and makes it worse
- Seasonal cash flow -- winter is slow, summer is overwhelming
- Rising chemical costs compressing margins

### Data Sources
- Route management apps (ServiceM8, Jobber, Pool Office Manager)
- Chemical tracking (custom spreadsheets or POM)
- Equipment supplier portals
- Weather apps
- Client communication history

### Proactive AI Opportunities -- "How Did It Know?"

> *"There's a heavy rainfall forecast Friday night -- 40mm. You have 8 pools on Saturday's route. After rain like that, chlorine typically drops significantly. You may want to carry extra chlorine granules Saturday and allow extra time per stop."*

> *"The Henderson pool hasn't had a service note in 19 days -- your standard interval is 14. They're not on this week's route either. Want me to check if they were rescheduled or slipped through?"*

> *"Pool season opening enquiries are up 40% this week compared to last year at this time. You have 12 confirmed opens booked. Based on last year, you typically get 8-10 more before peak. Your chemical stock may not cover that -- want to place a bulk order now at current prices?"*

> *"The Martins called yesterday about a grinding noise from their pump. Based on your notes, their Pentair pump is 6 years old. That symptom at that age is typically bearing failure. Parts are available at your supplier for $180 -- want me to order them so you have them for tomorrow's visit?"*

---

## 2.4 LOCKSMITHS

### What makes this role unique
Locksmiths are on-demand emergency service providers -- their core business is someone locked out at 11pm on a Sunday or a business that just had a break-in. The emergency nature creates a business model tension: you need to be available 24/7 to capture premium emergency rates, but that burns out sole operators. The unique Pulse angle: **missed calls are missed revenue** -- a locksmith who doesn't answer is immediately replaced by the next Google result. Also, locksmiths have significant regulatory and trust obligations (they have the means and knowledge to enter any premises).

### Daily/Weekly Rhythm
- No fixed schedule -- genuinely demand-driven
- Commercial work (rekeying, master key systems, access control installs) tends to be booked in advance
- Emergency/residential work is entirely reactive
- Mornings often have commercial installs booked
- Late nights/weekends: emergency lockout premium pricing

**Weekly:**
- Order parts mid-week (key blanks, cylinders, locks for upcoming installs)
- Review any outstanding commercial quotes
- Follow up on master key system completions

### Before Tasks
- Stock audit: right key blanks loaded? Common cylinders stocked?
- For booked commercial jobs: correct keys, access control gear, drawings if needed
- Check any outstanding quotes needing follow-up

### After Tasks
- Job card completed (what was done, what parts used)
- Invoice raised immediately (especially for emergency callouts)
- Licence/insurance certificate provided if requested (new commercial clients often require this)
- Key cutting log updated (some jurisdictions require this)

### Time-Sensitive Triggers
- **Missed call during peak hours** -- a missed call to a locksmith is almost certainly a lost job; callback within 5 minutes has significantly higher conversion than 30 minutes
- **Post break-in call** -- a business that's been burgled needs locks changed TODAY, not tomorrow
- **End-of-tenancy rekeying** -- property manager calls Friday afternoon wanting rekeying done before new tenant moves in Saturday
- **Key blank discontinued** -- a common key profile is being phased out by the manufacturer; need to stock up before it's unavailable
- **Licence renewal** -- varies by state/country; working without a valid locksmith licence is a criminal offence in most jurisdictions
- **Master key system emergency** -- one key in a master key system is lost; the whole system may need to be changed
- **Access control system failure** -- a business's electronic access control fails overnight; employees can't enter; emergency response needed before business hours

### Stress/Anxiety Points
- Being accused of overcharging for emergency callouts (the nature of 2am pricing is misunderstood)
- A job that takes 4x longer than quoted
- Lost/stolen master keys that require full system replacement (liability question)
- Keeping up with electronic access control technology (rapidly evolving)
- The trust burden -- potential for accusations if a property is subsequently burgled

### Data Sources
- Job management apps (ServiceM8, Tradify)
- Parts supplier portals (Lockwood, Abloy, ASSA, Schlage distributor portals)
- Google Business (incoming calls, reviews -- critical for emergency searches)
- Licence renewal portals
- Invoice/accounting software

### Proactive AI Opportunities -- "How Did It Know?"

> *"You missed 3 calls between 6-8pm last night. Based on the missed call numbers, 2 were likely emergency lockouts (both called back within 20 minutes, a typical pattern). That's potentially $400-600 in lost revenue. Want to set up an SMS auto-response for after-hours missed calls?"*

> *"Your locksmith licence renewal is due in 6 weeks. The application requires a current police check -- those take 2-3 weeks. You should apply for the police check this week."*

> *"The Millers' property management company sent an end-of-tenancy rekeying request at 4:47pm today. Move-out is Friday, new tenant Saturday. This needs to be booked by tomorrow -- want me to add it to Friday morning?"*

> *"Your Lockwood 001 key blank stock is at 8. You've cut 23 of that profile in the last 30 days. Want me to add 50 to your next order?"*

---

## 2.5 APPLIANCE REPAIR TECHNICIANS

### What makes this role unique
Appliance repair technicians are caught in a dying market that still has huge volume -- people still call, but the "repair vs. replace" threshold has dropped. The unique challenge: **parts availability is the defining bottleneck**. A technician can diagnose a washing machine in 10 minutes, but if the part takes 2 weeks to arrive, the customer is furious. Also, technicians carry enormous informal diagnostic knowledge (brand-specific quirks, common failure modes) that isn't easily captured digitally -- and they're constantly having to make split-second "can I fix this profitably?" decisions.

### Daily/Weekly Rhythm
- Morning: review jobs booked for the day, confirm parts have arrived for afternoon repair jobs
- Field visits: diagnose, quote, repair or leave with parts ordered
- Parts-on-hand jobs: more predictable, complete repair in one visit
- Afternoon: follow up on parts orders, contact customers whose parts arrived
- End of day: update job cards, raise invoices for completed jobs

**Weekly:**
- Monday: review all open jobs -- what's waiting for parts?
- Mid-week: bulk parts order to consolidate shipping
- Friday: invoice and follow-up outstanding quotes

### Before Tasks
- Parts confirmed received for today's repair appointments
- Correct tools loaded for the day's appliance types
- Customer confirmations for appointment times
- Check if any warranty job requires service agent authorisation before proceeding

### After Tasks
- Job completion documented with photos (warranty protection)
- Invoice raised
- Parts warranty noted in job card
- Feedback/review request sent (Google reviews are this business's lifeblood)

### Time-Sensitive Triggers
- **Customer frustration point at 7 days** -- research shows customer satisfaction drops sharply when a repair takes more than 7 days; proactive communication prevents cancellations
- **Parts non-availability** -- a part is discontinued; the repair is no longer economically viable; customer needs to know before they've waited 3 weeks
- **Refrigerator/freezer urgency** -- a broken fridge is a 24-hour problem due to food spoilage; customers expect same-day or next-day service
- **Under-warranty manufacturer referral** -- customer assumes the appliance is out of warranty; it's actually still under an extended warranty; missed = lost claim revenue
- **Parts price spike** -- a commonly needed part doubles in price due to supply chain issues; existing quotes become unprofitable
- **Warranty authorisation expiry** -- manufacturer service agent jobs often have 30-day authorisation windows; if repair is delayed past that, re-authorisation is needed

### Stress/Anxiety Points
- Arriving to a job where the diagnosis is clear but the part is unavailable anywhere
- A repair that works when tested but fails again within the repair warranty period
- Being squeezed between labour costs and customers who won't pay more than "half the replacement cost"
- Parts suppliers sending wrong parts
- Manufacturer warranty policies changing without notice

### Data Sources
- Job management software (ServiceM8, Jobber, RepairDesk)
- Parts supplier portals (Appliance Parts Australia, PartsSelect, Encompass)
- Manufacturer service portals (for warranty claims)
- Parts lookup databases (PartSelect, Searspartsdirect)
- Google Business (reviews, incoming calls)

### Proactive AI Opportunities -- "How Did It Know?"

> *"Mrs. Williams' washing machine repair has been waiting 8 days for a part. She hasn't called yet, but based on your job data, customers who wait more than 7 days without an update have a 40% cancellation rate. Want me to send her an update message now?"*

> *"The Bosch control board for job #447 is showing as discontinued at all 3 of your usual suppliers. This repair may not be viable. Want me to draft a message to the customer with the options?"*

> *"You have 4 refrigerator repair enquiries this week -- that's double your usual rate. Fridge failures often cluster around heatwaves. It's 38C forecast for the next 3 days -- you might want to add emergency same-day availability messaging to your Google profile temporarily."*

> *"Job #389 (Samsung dryer, heater element) -- you completed this 28 days ago. Your repair warranty is 30 days. If there's going to be a callback issue, it'll likely happen this week. Worth a quick check-in call?"*

---

## 2.6 IT SUPPORT TECHNICIANS / MSP OWNERS

### What makes this role unique from "regular IT"

An **IT support technician** (solo/employed) is reactive: they fix things that break, respond to tickets, and get paid for time.

An **MSP (Managed Service Provider) owner** has a fundamentally different model: they're paid a flat monthly fee to prevent things from breaking. Their incentive structure is inverted -- the less "fires" there are, the more profitable they are. This creates a proactive, monitoring-heavy mindset. But it also creates enormous complexity: they're responsible for the IT of 5-50 small businesses simultaneously, often with a tiny team.

**The unique MSP stress:** a single ransomware incident at one client can dominate the entire team for weeks AND damage the business's reputation across all clients simultaneously. The most catastrophic events are also the most public.

### Daily/Weekly Rhythm (MSP Owner)
- Morning: review RMM (Remote Monitoring & Management) alerts from overnight; anything critical?
- Triage tickets from the previous evening (clients often log issues outside business hours)
- Check backup job status for all clients -- did they all complete?
- Engineering calls/project work for clients
- Afternoon: sales, proposals, vendor management, staff performance
- Evening: off in theory; in practice, monitoring alerts can come any time

**Weekly:**
- Monday: weekly ops review -- open ticket age, SLA compliance, any clients at risk
- Wednesday: vendor/supplier bills review, licencing reconciliation
- Friday: engineer team check-in, review any projects slipping

**Monthly:**
- Client reporting (executive summary of what we fixed, what we protected)
- Patch compliance report -- are all managed endpoints patched?
- Security review

### Before Tasks
- Overnight RMM alerts reviewed
- Backup success/failure dashboard reviewed -- any client missing backups?
- Active critical tickets reviewed
- Any planned maintenance window expiring today?

### After Tasks
- Tickets closed with resolution notes (billing depends on this)
- Time logged against client accounts
- Any incidents communicated to affected clients
- Out-of-band client communications documented

### Time-Sensitive Triggers
- **Ransomware/malware detection** -- immediate all-hands response; isolation, client notification, insurance notification -- minutes matter
- **Backup failure** -- a client's backup has been failing silently for 3 weeks; you find out when they have a data loss event
- **Microsoft/365 licence expiry** -- a client's licence lapses and 50 users lose email access at 9am; it's the MSP's fault in the client's eyes even if they didn't pay
- **SSL certificate expiry** -- a client's website goes down with a "not secure" warning; often happens because the cert was set up manually before the MSP took over
- **Vendor end-of-life** -- Windows 10 EOL, a router reaching firmware end-of-life; the MSP knew, but did the client authorise the upgrade budget?
- **Staff turnover at client site** -- a key contact leaves; their admin accounts, passwords, and access need immediate review
- **MFA bypass incident** -- a client employee complains that MFA "keeps kicking them out"; sometimes this is a compromise attempt; needs investigation not just disabling
- **SLA breach risk** -- a ticket is approaching SLA response time; missing it triggers a credit and damages the contract

### Stress/Anxiety Points
- The dread of Monday morning alerts
- A security incident at one client that could have been prevented
- A client who won't approve security upgrades and then blames the MSP when something goes wrong
- Flat-fee model eroding during incidents -- 40 hours of emergency work at no extra charge
- Staff retention -- good engineers can always earn more elsewhere
- Keeping up with the threat landscape -- new attack vectors emerge constantly

### Data Sources
- RMM platforms (NinjaRMM, Datto RMM, ConnectWise Automate, Kaseya)
- PSA/ticketing (ConnectWise Manage, Autotask, HaloPSA)
- Backup platforms (Veeam, Datto, Acronis)
- Security platforms (SentinelOne, CrowdStrike, Huntress)
- Microsoft 365 admin centre / Azure AD
- Licence management platforms
- Vendor security bulletins (CISA, Microsoft, CVE databases)

### Proactive AI Opportunities -- "How Did It Know?"

> *"Client Acme Legal's backup job has returned warnings for 3 consecutive nights. It hasn't fully failed yet, but this pattern preceded the last backup failure you had in October. Want me to create a priority ticket?"*

> *"Johnson & Associates has 5 Microsoft 365 licences expiring in 14 days. Their billing contact is Sarah -- and Sarah left the company last month. You'll want to confirm who the new billing contact is before the renewal hits a dead card."*

> *"There's a critical CVE (9.8 severity) for Fortinet FortiGate released 6 hours ago. You manage FortiGate devices at 4 client sites. Patch availability is expected tomorrow. Want me to draft a maintenance window request to those clients?"*

> *"Ryan Mitchell at DataCore just put in 3 'MFA not working' tickets in the last 2 weeks. Each was resolved by resetting. This pattern is a potential credential stuffing indicator -- may be worth a security review of that account rather than another reset."*

> *"Your SLA for Ticket #4821 (critical priority) expires in 47 minutes. No engineer has picked it up yet. Want me to send an alert to the on-call engineer?"*

---

# SECTION 3: FREELANCE & GIG ECONOMY

---

## 3.1 FREELANCE GRAPHIC DESIGNERS

### What makes this role unique
Freelance designers deal with a perpetual tension: the creative work (which they love and are hired for) vs. the business admin (which they hate and often neglect). The dangerous pattern: feast/famine cycles driven by poor pipeline management. When they're busy, they don't market. When they finish a big project, they have no pipeline. Also: **scope creep is their biggest revenue leak** -- a project "expands" through revision requests and they often absorb the cost rather than have the difficult conversation.

### Daily/Weekly Rhythm
- Morning: creative work when energy is highest
- Midday: client communication, revision rounds
- Afternoon: admin, invoicing, new client emails
- No fixed pattern -- entirely self-managed, which is both the freedom and the risk

**Weekly:**
- No defined structure, but good designers self-impose:
  - Monday: week planning, client check-ins
  - Wednesday: mid-week deliverable push
  - Friday: invoices for completed work, business admin

### Before Tasks
- Review brief thoroughly before starting any design work (garbage in, garbage out)
- Confirm deliverables, file formats, and revision policy with client if not in contract
- Check if font/asset licences cover client's intended use

### After Tasks
- Deliver files in agreed format
- Archive project files (clients always come back needing changes)
- Raise invoice (many designers delay this, hurting cash flow)
- Request testimonial/review if work went well
- Note project in portfolio tracker

### Time-Sensitive Triggers
- **Invoice aging** -- a designer who doesn't chase overdue invoices loses 15-20% of revenue to slow payers
- **Licence expiry** -- Adobe CC, Figma, stock image subscriptions; expired tools mean delivery failures
- **Client brief changes mid-project** -- without a paper trail, "it was always supposed to be this way" arguments arise
- **Rush request** -- a client needs something by tomorrow; premium is available but only if responded to within hours
- **Seasonal demand peaks** -- December (Christmas campaigns), January (new year rebranding), pre-Q2 (campaign planning) -- getting booked up before competitors do
- **Portfolio stagnation** -- their own marketing (Behance, Instagram, LinkedIn) is often months stale, directly impacting inbound enquiries

### Stress/Anxiety Points
- A client who wants "unlimited revisions" treating the flat fee as an all-you-can-eat buffet
- Waiting on content from the client that's blocking project delivery (but the deadline is theirs)
- Cash flow gaps when multiple clients pay late simultaneously
- Undercharging -- most freelancers chronically underprice themselves for years
- Isolation and creative blocks with no colleagues to bounce ideas off

### Data Sources
- Project management (Notion, Trello, Asana, ClickUp)
- Time tracking (Toggl, Harvest, Clockify)
- Invoicing (FreshBooks, Wave, QuickBooks, AND.CO)
- Client communication (email, Slack, BaseCamp)
- Design tools (Adobe CC, Figma, Sketch)
- Portfolio platforms (Behance, Dribbble, personal site)

### Proactive AI Opportunities -- "How Did It Know?"

> *"Invoice #47 to Bright Media is 14 days overdue. Your standard payment term is net-14. Want me to send a polite chase email?"*

> *"You haven't posted to your Behance portfolio in 3 months. You have 4 completed projects in your archive folder that aren't in your portfolio. Your last 2 inbound leads mentioned Behance as how they found you."*

> *"The Anderson rebrand project has received 5 revision rounds. Your contract allows 3. You've absorbed the last 2 without charging. Want me to draft a scope change note before the next round starts?"*

> *"Your Adobe CC subscription auto-renews in 3 days. Based on your Toggl data, you've billed $4,200 in Adobe-related project work this month. The renewal is $60. Just confirming you want to renew -- no action needed if yes."*

> *"It's the last week of November. Based on last year, your December booking rate dropped 60% -- but January was your busiest month. Three of your past clients typically commission January work. Want me to draft a quick 'capacity available for Q1' note to them?"*

---

## 3.2 FREELANCE WEB DEVELOPERS

### What makes this role unique
Freelance web developers have technically complex work with business management challenges. The unique dynamic: **technical debt accumulates on client sites they maintain** -- sites they built 3 years ago on older frameworks are becoming security liabilities, and the client hasn't budgeted for updates. Also, developers are uniquely exposed to **scope creep on technical work** where the client doesn't understand what "adding a feature" actually involves. The "it should only take 5 minutes" problem is universal and demoralising.

### Daily/Weekly Rhythm
- Deep work blocks (2-4 hours of uninterrupted coding) -- mornings for most
- Client calls typically early afternoon
- Evening: catching up on emails, reviewing pull requests, deploying
- Weekend: "never working weekends" that turns into emergency site fixes

**Weekly:**
- Scrum-lite: what's in progress, what's blocked, what needs client input?
- Security updates review for any maintained sites
- Hosting billing check (AWS/Cloudflare/Vercel invoices that can spiral)

### Before Tasks
- Backups confirmed before any significant deployment
- Test environment updated before coding new feature
- Client has provided all required content/assets before starting a new section
- Staging site approved by client before pushing to production

### After Tasks
- Git commit with clear message
- Deployment to staging for client review
- Update project documentation (future self will thank you)
- Time logged against project
- Any hosting/domain costs to be recharged to client noted

### Time-Sensitive Triggers
- **SSL certificate expiry** -- a client's site goes "not secure"; their business suffers; they blame the developer
- **Domain expiry** -- client hasn't updated their credit card on file at the registrar; domain lapses and gets snapped up
- **Plugin/CMS security vulnerability** -- a critical WordPress vulnerability is announced; they have 20 WordPress sites to patch
- **Hosting auto-renewal failure** -- a client's hosting renews on an expired card; site goes down at 3am
- **Google Core Update** -- an algorithm update tanks a client's rankings overnight; client calls asking why
- **Node/PHP/Framework deprecation** -- a runtime environment reaches EOL; a client's site starts throwing errors or becomes a security liability
- **Client ghosting before launch** -- project is complete but the client hasn't reviewed in 3 weeks; payment is gated on sign-off

### Stress/Anxiety Points
- A production site going down on a weekend
- A client changing the scope significantly after work is substantially complete
- Being blamed for a site's poor SEO performance when content is the client's responsibility
- Hosting/domain costs on client accounts that they manage but can't track across dozens of clients
- The "one more small thing" that was never in scope

### Data Sources
- Git (GitHub, GitLab, Bitbucket)
- Hosting dashboards (AWS, Cloudflare, WP Engine, Kinsta, Vercel)
- Domain registrars (Namecheap, GoDaddy, Google Domains)
- Uptime monitoring (UptimeRobot, Better Uptime, Pingdom)
- Project management (Linear, Jira, Notion)
- Time tracking (Toggl, Harvest)
- Security scanners (WPScan, Sucuri, Snyk)

### Proactive AI Opportunities -- "How Did It Know?"

> *"Greenleaf Organics' SSL certificate expires in 8 days. It's on their shared hosting account -- want me to log into cPanel and trigger a Let's Encrypt renewal?"*

> *"There's a critical WordPress security update (5.x -> 6.x patch) affecting 3 sites you maintain. The vulnerability was published 6 hours ago and exploit code is already in the wild. Want me to schedule emergency patching for tonight?"*

> *"The TechFlow project has been in client review for 22 days. Your contract has a 'client review delay' clause -- you can invoice for the completed milestone after 14 days. Want me to raise that invoice and send a gentle nudge to Marcus?"*

> *"Dynamic Digital's domain auto-renews October 12. Their card on file expired in August -- last time this happened you spent 3 hours recovering a lapsed domain. Want me to send them a heads up now?"*

---

## 3.3 VIRTUAL ASSISTANTS (FREELANCE)

### What makes this role unique
Freelance VAs are professional multitaskers who work inside multiple clients' businesses simultaneously -- often 3-6 clients at once. The unique challenge: **context-switching overhead is enormous** -- jumping between a real estate agent's CRM at 9am, a coach's email at 10am, and an e-commerce brand's social media at 11am requires rapid mental context switches that most other roles don't demand. Also: VAs often know their clients' businesses better than the clients themselves do, creating an unusual trust dynamic.

### Daily/Weekly Rhythm
- Typically works set hours per client per week (e.g., 10 hours for Client A, 5 hours for Client B)
- Morning: highest-value tasks first (inbox zero for clients, calendar management, urgent requests)
- Context switching is the dominant rhythm
- End of day: update time logs, flag anything urgent for tomorrow
- **The hidden weekly task:** proactive client reporting -- "here's what I did this week" -- but many VAs don't do this and then clients wonder what they're getting

### Before Tasks
- Check each client's urgent channels (WhatsApp, Slack, email) before diving into scheduled work
- Confirm any meetings being managed on behalf of clients (no double-bookings)
- Review task lists across all client workspaces

### After Tasks
- Log time accurately per client
- Update task lists with progress
- Flag anything unfinished for tomorrow
- Weekly: send client summary reports (proactive trust-building)

### Time-Sensitive Triggers
- **Client in different time zones urgently needing something** -- they sent it at 5am their time; it's urgent for them, but you won't see it for 4 hours
- **Travel bookings** -- a client asks for flights/hotels; prices rise with delay; needs to be actioned within hours
- **Content scheduling gaps** -- a social media schedule has a gap appearing; the post was supposed to go out tomorrow but wasn't ready
- **Contract renewal** -- VA contracts are often 3-month rolling; a client not renewing affects income significantly
- **Onboarding new client while managing existing** -- capacity planning fails if not managed carefully
- **Client business emergency** -- a client has a PR crisis, a launch failure, a team member resigning; the VA is often first to know and first to need to help
- **Overdue invoice** -- VAs are terrible at chasing invoices; their own payment terms are often poorly enforced

### Stress/Anxiety Points
- Being treated as an employee rather than a contractor (scope creep of availability expectations)
- The "always available" expectation that erodes personal time
- A client who suddenly demands more hours without paying more
- Income instability when a client contract ends without warning
- Knowing too much about a client's business and having nowhere to process it

### Data Sources
- Client project management tools (Asana, ClickUp, Notion, Trello -- all different)
- Client email accounts (Google Workspace, Outlook -- managing on their behalf)
- Time tracking (Toggl, Harvest, Clockify)
- Own invoicing (FreshBooks, Wave)
- Client CRMs (HubSpot, Keap, various)
- Scheduling tools (Calendly, Acuity)

### Proactive AI Opportunities -- "How Did It Know?"

> *"It's Tuesday morning. Based on your Monday task log, you're 2.5 hours behind on Client B's social media schedule. The next post is due at 10am tomorrow -- if you don't complete this today, it'll run into Client A's priority window tomorrow."*

> *"Your contract with Sarah Williams renews in 3 weeks. She hasn't mentioned renewal -- and last time you left this to the last minute you had a 2-week income gap. Want me to draft a renewal email?"*

> *"James (Client C) sent 4 messages on WhatsApp after 9pm last night. Your contract specifies 9-5 working hours. This is the third time this month. Want me to draft a polite boundary reminder?"*

> *"Invoice #23 to GrowthLab is 21 days overdue. Want me to send an overdue notice? A firm but friendly template is ready."*

---

## 3.4 COPYWRITERS / CONTENT WRITERS

### What makes this role unique
Copywriters and content writers are professional wordsmiths dealing with the invisible product problem -- clients often don't value writing until they need it, and undervalue it even then. The unique pressures: **AI disruption anxiety** (the fear that they're being replaced, often expressed by clients asking for "AI-written with a quick human edit"), **revision loops** (writing is endlessly subjective), and **dependency on client briefs** (bad brief = bad copy = revision hell, but the client thinks it's the writer's fault).

### Daily/Weekly Rhythm
- Morning: first-draft writing (creative energy peak)
- Midday: editing, revisions, client communication
- Afternoon: research for upcoming projects, admin
- Evening: pitching, networking (often neglected)

**Weekly:**
- Monday: review the week's project deadlines
- Wednesday: mid-week deliverable push, client follow-ups
- Friday: invoices, portfolio updates, new client outreach

### Before Tasks
- Brief fully understood before starting (ask clarifying questions proactively)
- Research completed before writing
- Voice/tone guide consulted if brand guidelines exist
- Keyword targets confirmed (for SEO content)

### After Tasks
- Proofread (yes, professional writers miss things when self-editing)
- Submit with clear delivery notes (what was written, why certain decisions were made)
- Invoice raised
- Note delivery for portfolio/case study tracking

### Time-Sensitive Triggers
- **Publication deadlines** -- editorial calendars are unforgiving; a missed delivery means a content gap the client has to fill
- **Product launch copy** -- everything has to land before the launch date; delays cascade
- **SEO content timing** -- Google indexing has latency; content for a seasonal keyword needs to be published 6-8 weeks before the season
- **Contract lapse** -- a retainer client's contract rolling month-to-month; a month with no renewal conversation = unexpected churn
- **AI policy change at a client** -- a client adopts an "all content through AI only" policy; the writer's retainer is immediately at risk
- **Rate increase timing** -- annual rate reviews are often delayed indefinitely by freelancers who are too uncomfortable to raise them

### Stress/Anxiety Points
- A client who hates the first draft and can't articulate why
- Being asked to "make it more engaging" without any specifics
- The AI comparison ("could we just use ChatGPT for this?")
- Clients who want "SEO copy" but don't actually understand SEO
- Feast/famine cash flow cycles
- Overdue invoices from clients who are lovely people but bad payers

### Proactive AI Opportunities -- "How Did It Know?"

> *"The Bravura Foods blog post is due Friday. It's currently Wednesday and you have no draft started. Your other Wednesday project just wrapped -- now might be the best window before the deadline crunch."*

> *"Your blog content for TechStart's spring campaign is due April 15. For the keywords you're targeting, Google recommends publishing 8 weeks before peak -- that means a February 15 publication date. Have you flagged this to the client?"*

> *"Your hourly rate hasn't changed in 14 months. Based on your project data, you're currently billing at $85/hr. Median freelance copywriter rates in your niche are $95-120/hr. Your Bloom Media retainer renews next month -- good time to review."*

---

## 3.5 VOICE OVER ARTISTS

### What makes this role unique
VO artists are a small, specialised market with very specific workflow quirks. They work from home studios, submit auditions at scale (dozens per week for competitive commercial work), and have to manage **acoustic quality obsessively** -- a background noise in a $5,000 project is a catastrophic outcome. The business model often involves **two revenue streams with different rhythms**: P2P (Pay-to-Play) casting sites (Voices.com, Voice123) where they audition competitively, and direct client relationships where they're the preferred voice for a brand or series.

### Daily/Weekly Rhythm
- Morning: check new P2P job listings, select and record auditions (speed matters -- early auditions get more listens)
- Recording sessions for confirmed bookings
- Afternoon: audio editing, quality checking, file delivery
- Evening: marketing, training, equipment maintenance

**Weekly:**
- Review P2P audition win rate -- is the pitch strategy working?
- Check equipment (mics, interface, DAW) for any issues
- Client follow-ups and relationship building

### Before Tasks
- Acoustic check -- any unusual sounds? (HVAC, traffic, neighbours)
- Equipment check -- mic phantom power, interface levels, headphone monitoring
- Script reviewed before recording (cold-read errors waste time)
- Water nearby (hydration affects voice quality)

### After Tasks
- Raw files backed up before editing
- Edited file QC'd -- pop filter, room noise, breaths, levels
- File delivered in correct format (MP3, WAV, AIFF, specific dB levels as specified)
- Invoice raised for project work
- Testimonial requested if first-time client

### Time-Sensitive Triggers
- **Audition window** -- P2P listings often show "10 auditions received" vs "47 auditions received"; early auditions have dramatically higher selection rates; a 2-hour delay can mean 30+ more competitors
- **Directed session** -- a Zoom-directed recording session where the client is waiting; technical failure (mic, internet, DAW crash) is the highest-stress moment
- **Rush delivery** -- a corporate client needs a voiceover for a presentation tomorrow; premium rates apply but the turnaround is 2-4 hours
- **Equipment failure before a booking** -- a mic dies before a $2,000 session; no backup = cancellation = reputation damage
- **Union/non-union project conflict** -- for SAG-AFTRA members, accepting a non-union job can have consequences
- **Booking confirmation ghosting** -- a client said "we'll book you" 2 weeks ago; they may have moved on; following up at the right time without seeming desperate
- **Vocal health** -- a cold or throat issue before a booked session; cancellation vs. pushing through

### Stress/Anxiety Points
- A recording ruined by an unexpected sound (siren, dog barking, fridge compressor)
- Technical failure during a directed session
- Audition-to-booking conversion rate dropping (hard to diagnose)
- Low booking periods with significant studio costs still running
- The "your voice sounds great but we went another direction" loop

### Data Sources
- P2P platforms (Voices.com, Voice123, Backstage, Casting Call Club)
- DAW software (Adobe Audition, Pro Tools, Reaper, Logic)
- Email (client communication and booking confirmations)
- Invoicing software
- Acoustic monitoring apps

### Proactive AI Opportunities -- "How Did It Know?"

> *"There are 3 new corporate narration jobs on Voice123 posted in the last 2 hours -- your highest-converting category. First auditions typically close within 4 hours of posting. Want to review them now?"*

> *"Your microphone hasn't been tested since Monday. You have a directed session with Novartis tomorrow at 10am. A quick level check tonight is worth 5 minutes."*

> *"The Pinnacle Media booking from 6 weeks ago never confirmed. You sent a follow-up at 3 weeks. Based on your data, jobs that don't confirm within 45 days rarely materialise. You may want to mark it as lost and open that slot."*

> *"Your audition-to-booking rate this month is 4.2% -- down from 7.1% last month. Your strongest months coincided with new demo reels. Your current demo is 14 months old -- may be worth a refresh."*

---

## 3.6 TRANSLATORS / INTERPRETERS

### What makes this role unique
Translators (written) and interpreters (spoken, real-time) have different rhythms but share unique stresses: **absolute precision under time pressure** and the **invisible complexity problem** -- clients who don't speak the target language have no idea how hard the work is and chronically undervalue it. Interpreters have an additional unique stress: they're doing cognitively exhausting real-time mental work (simultaneous interpretation can burn 2,000 calories in a day) and are then expected to be immediately available for the next booking.

**Translators:** longer projects, deadline-driven, batched work
**Interpreters:** event/appointment-driven, last-minute bookings, higher acute stress

### Daily/Weekly Rhythm (Translator)
- Deep translation work in focused blocks (3-4 hours max before quality degrades)
- Reference material check between sections
- End of day: word count tracking, deadline review
- Weekly: invoice outstanding completed projects, source new work

**Interpreter:**
- Appointment/event driven -- often booked week-by-week
- Preparation for each booking (subject matter research, terminology review)
- Post-session: brief notes on any unusual terms for next time

### Time-Sensitive Triggers (Translator)
- **Deadline** -- clients often give unrealistic deadlines; managing expectations early is critical
- **Source text updates** -- a client changes the source document after translation has started; the delta needs repricing
- **Certification requirements** -- some translations require notarisation or certification from an official body; these have their own processing times
- **Terminology consistency on large projects** -- on a long-running project, inconsistent term choices cascade into quality problems

**Interpreter:**
- **Last-minute booking** -- a court interpreter called the morning of a hearing; prep time is minimal
- **No-show at a booking** -- they arrive; the client isn't there; cancellation fee policy needs to be enforced
- **Rare language pair surge** -- a sudden spike in demand for their language combination (political event, refugee arrivals, business expansion)
- **Medical/legal certification lapse** -- NAATI, court interpreter certification, medical interpreter certification -- all have renewal requirements

### Stress/Anxiety Points (Interpreter)
- A medical appointment where the patient's life decisions depend on perfect interpretation
- A court interpreter who mishears a date or name -- legal consequences
- Cognitive exhaustion being invisible to clients who book them for 6-hour events
- The "can you also translate this document while you're here?" scope creep
- Being told post-session that the interpretation was wrong by someone who doesn't speak the language

### Data Sources
- CAT tools (SDL Trados, memoQ, Wordfast, DeepL for reference)
- Terminology databases (personal glossaries, client-specific term bases)
- Booking/calendar management (email, dedicated interpreting platforms: LanguageLine, Boostlingo)
- Invoicing software
- CPD and certification portals (NAATI, ATA, AIIC)

### Proactive AI Opportunities -- "How Did It Know?"

> *"The Hansen Legal project is 14,000 words at your standard rate of $0.15/word. Your deadline is Friday. Based on your typical output of 2,000 words/day of quality translation, you need to start tomorrow to hit the deadline comfortably. You haven't started yet."*

> *"Your NAATI certification renewal is due in 4 months. The CPD requirement is 40 points and you have 22 logged. There's a AUSIT webinar on medical terminology next Thursday -- that's 4 CPD points."*

> *"You have a Tuesday medical interpretation booking at Royal Women's Hospital. The referral says 'oncology consultation' -- this is likely a treatment decision meeting. Worth 30 minutes of medical terminology prep tonight."*

---

## 3.7 ONLINE COURSE CREATORS

### What makes this role unique
Course creators are content creators, educators, marketers, and customer service reps simultaneously. The unique challenge: **course revenue is lumpy** -- a product launch might generate $40k in a week, then almost nothing for 2 months. This creates cash flow volatility and the psychological feast/famine cycle. Also, courses have a **content decay problem** -- material becomes outdated, students who bought 2 years ago are now receiving incorrect information, and updating is a significant effort that's easy to indefinitely defer.

### Daily/Weekly Rhythm
- Creation mode (filming, writing): needs focused blocks; often morning
- Marketing mode (email, social, ads): afternoon
- Student support (forum, email, DMs): ongoing throughout day
- Launch periods: completely different, high-intensity rhythm for 5-10 days

**Weekly:**
- Content creation vs. marketing vs. support balance review
- Email list engagement metrics review
- Ad spend review if running paid traffic

**Monthly:**
- Revenue vs. refund rate analysis
- Student completion rate review (low completion = lower future sales testimonials)
- Content update review -- anything factually outdated?

### Before Tasks (before a launch)
- Email sequences loaded and tested
- Sales page live and tested on multiple devices
- Payment processing tested
- Tech stack (Kajabi, Teachable, Thinkific) -- everything working?
- Customer service prepared for incoming questions
- Refund policy clearly communicated

### After Tasks (post-launch)
- Onboarding email sequence triggered for new students
- Student welcome in community/forum
- Refund requests handled within promised timeframe
- Launch debrief -- what worked, what didn't

### Time-Sensitive Triggers
- **Cart close deadline** -- their own artificial urgency; if the cart closing email doesn't go out on time, trust erodes
- **Live webinar technical failure** -- their entire launch funnel might be gated on a live webinar; tech failure = lost sales
- **Platform outage** -- Kajabi/Teachable going down during a launch is catastrophic
- **Affiliate partner communication** -- if affiliates are promoting a launch, they need assets on time and accurate commission tracking
- **Student complaint going public** -- a dissatisfied student posting on social media or forums before the creator can respond
- **Course content becoming factually wrong** -- a major platform or tool they teach about (e.g., a software tool) changes its interface significantly, making their course look outdated
- **Email deliverability issues** -- a launch sequence not reaching inboxes due to spam filter issues; realising this halfway through a launch

### Stress/Anxiety Points
- A launch that underperforms after months of preparation
- Refund requests undermining confidence
- Student complaints about support response time
- Competitors launching similar courses at lower prices
- The content treadmill -- always needing to create more, update more
- Ad platform policy changes killing a traffic strategy overnight

### Data Sources
- Course platforms (Kajabi, Teachable, Thinkific, Podia)
- Email marketing (ConvertKit, ActiveCampaign, Mailchimp)
- Ads platforms (Meta Business Suite, Google Ads)
- Analytics (Google Analytics, platform native analytics)
- Community platforms (Circle, Discord, Facebook Groups)
- Affiliate management (Lemon Squeezy, ThriveCart, PartnerStack)

### Proactive AI Opportunities -- "How Did It Know?"

> *"Your cart closes in 48 hours. The 'last chance' email is scheduled for tomorrow at 9am. But your open rate data suggests your list is most engaged at 7am -- sending at your usual 9am may underperform. Want to shift it forward?"*

> *"Module 4 of your Facebook Ads course references the old Ads Manager interface that was replaced 8 months ago. You have 47 new students since then who've likely hit this. Three left reviews mentioning the interface is different. Want to flag this for a re-record?"*

> *"Your ConvertKit open rate dropped from 38% to 22% over the last 4 weeks. This pattern often indicates a deliverability issue. Your domain may need SPF/DKIM review. Want me to run a deliverability check?"*

> *"The Productivity Mastery launch is in 3 weeks. Last launch your live webinar registration-to-show rate was 28%. With 1,247 registered, that's ~350 live attendees. Your webinar platform maxes out at 300. You'll need to upgrade before launch day."*

---

## 3.8 AMAZON FBA SELLERS

### What makes this role unique
FBA (Fulfilled by Amazon) sellers are supply chain managers, marketing executives, and customer service operators all at once -- for a business that runs 24/7 on a platform they don't fully control. The unique stress: **Amazon can suspend your listing or account with limited explanation**, and while suspended, revenue drops to zero. Also, FBA economics depend heavily on **inventory positioning** -- too much stock means large storage fees; too little means stock-outs that tank ranking and revenue simultaneously.

### Daily/Weekly Rhythm
- Morning: check overnight sales, BSR (Best Seller Rank) movement, any listing issues
- Review ad spend vs. ACOS (Advertising Cost of Sales)
- Check inventory levels and days-of-stock remaining
- Respond to customer reviews and questions
- Afternoon: supplier communication, inventory planning

**Weekly:**
- Monday: weekly P&L snapshot -- revenue, COGS, fees, ads, net profit
- Wednesday: ad optimisation session -- bids, keywords, negative keywords
- Friday: inventory reorder review -- any reorders needed in the next 2 weeks?

**Monthly:**
- Full P&L review including Amazon fee reconciliation
- Supplier performance review
- New product research

### Before Tasks (before sending inventory to Amazon)
- FNSKU labels correct?
- Packaging compliant with Amazon requirements?
- Supplier shipping documents confirmed?
- Inbound shipment created in Seller Central?

### After Tasks
- Monitor inbound shipment for receipt confirmation
- Review first week's sales of any new product launch
- Confirm reviews aren't flagged as manipulated

### Time-Sensitive Triggers
- **Stock-out** -- running out of stock causes ranking collapse; recovering organic ranking after a stock-out can take weeks; this is the most costly mistake
- **Days-of-stock warning** -- at 14 days remaining, reorder should already be placed and in transit; at 7 days, it's an emergency
- **Listing suppression** -- Amazon suppresses a listing for any number of reasons (image compliance, pricing issue, policy flag); sales immediately drop to zero
- **Account suspension** -- the nightmare; requires Plan of Action response within 17 days (first appeal) or the case worsens
- **Price war** -- a competitor drops price by 30% overnight; automated repricing might trigger a race to the bottom
- **Q4 inventory planning** -- Black Friday and Christmas shipping cutoffs are hard deadlines; inventory needs to arrive at Amazon warehouses by early November; containers need to be booked months earlier
- **Long-term storage fees** -- Amazon charges significantly higher fees for inventory that's been in their warehouse for >365 days; a quarterly audit prevents getting hit
- **Negative review surge** -- 3+ negative reviews in a week can drop BSR significantly

### Stress/Anxiety Points
- A suspended listing or account with no clear reason given
- A competitor with fake reviews outranking a legitimate product
- Amazon changing fee structures with 30-day notice that reshapes profitability
- A supplier delivering defective stock that's already at Amazon
- Cash flow -- FBA cash cycles are often 60-90 days from manufacture to payment received
- The "black box" -- not knowing why a listing isn't ranking despite doing everything right

### Data Sources
- Amazon Seller Central (primary dashboard)
- Third-party tools (Helium 10, Jungle Scout, Keepa, Sellerboard)
- Advertising console (AMS)
- Supplier communication (email, Alibaba, WeChat)
- Inventory management tools (InventoryLab, Sellerboard)
- Shipping tools (Freightos, Flexport for large shipments)
- Review monitoring tools

### Proactive AI Opportunities -- "How Did It Know?"

> *"Your top SKU (B09XK4...) has 9 days of stock remaining. Current reorder lead time from your supplier is 21 days. You're already in the stock-out window. Do you want me to send an urgent reorder request to Shenzhen Bright Manufacturing?"*

> *"Your ACOS on the 'stainless steel tumbler 32oz' campaign jumped from 18% to 34% overnight. A new competitor entered with a $3 lower price and is running aggressive ads. Your bid strategy may need to change -- want me to flag the keywords most affected?"*

> *"Q4 inventory planning: Amazon's Black Friday inbound receiving cutoff is November 1. Based on your 2024 Q4 sales velocity, you'll need approximately 1,400 units. Your current container booking lead time with your freight forwarder is 6 weeks. You should be placing a production order this week."*

> *"Your listing for 'bamboo cutting board set' has been suppressed since 8:47am. Suppression reason: 'main image has text overlay.' This has been flagged before -- your June image update may have reintroduced the issue. Sales are paused until resolved."*

---

# SECTION 4: COMMUNITY & CARE

---

## 4.1 AGED CARE WORKERS

### What makes this role unique (vs. general nursing)
Aged care workers are not nurses. They provide personal care -- bathing, dressing, mobility assistance, meals, companionship -- to elderly people in residential facilities or in their homes. The key difference from nursing: **they spend far more time with each client than any nurse does**. They notice the subtle changes -- "Mr. Webb was quieter than usual this morning," "Mrs. Singh hasn't eaten properly in 3 days" -- that nurses and doctors only see in clinical snapshots. They are the clinical early warning system, but often lack the language or confidence to escalate appropriately.

The other unique dimension: **emotional load of grief**. Aged care workers lose residents regularly. This is normalised within the profession but creates cumulative grief that's rarely processed. Also: **families** -- more than any other care setting, family members are intensely involved, opinionated, and sometimes hostile.

### Daily/Weekly Rhythm (Residential Facility)
- Early shift (6am-2pm): morning care routines, breakfast, medications support, handover to day staff
- Day shift (7am-3pm or 9am-5pm): activities, medical appointments, family visits, documentation
- Late shift (2pm-10pm): afternoon care, dinner, evening routines, handover notes
- Night shift (10pm-6am): hourly checks, call responses, safety monitoring
- **No clean break between weeks** -- 24/7 care means this is a continuous rotating operation

**Home Care Worker:**
- Geographically scheduled client visits
- Multiple clients per day, each with their own care plan
- Travel time between visits is unpaid in many arrangements -- the hidden labour
- End of day: shift notes completed for each client

### Before Tasks
- Handover reading -- what happened on the last shift?
- Any new residents to be oriented to?
- Medication changes? Any falls overnight?
- Specific resident flags -- Mrs. Chen's family coming today, Mr. Okafor has a physio appointment at 11

### After Tasks
- Shift notes completed -- behaviours, dietary intake, any observations (this is a clinical and legal document)
- Handover verbal brief to incoming staff
- Any incidents formally documented
- Concerns escalated to the nurse if identified during shift

### Time-Sensitive Triggers
- **Acute deterioration** -- a resident who seemed fine at breakfast is confused and feverish by morning tea; this is a same-hour escalation to the nurse
- **Fall** -- a resident falls; even if uninjured, the documentation and incident response needs to be immediate
- **Medication error** -- a wrong medication given; immediate incident report and nurse notification
- **Behaviour change over days** -- subtle but the worker notices; if not escalated, a treatable delirium becomes a hospitalisation
- **Family complaint** -- a family member makes a formal complaint; facility management needs to know immediately
- **Staffing shortfall** -- a co-worker calls in sick; the remaining staff are now unsafe; this needs to be escalated immediately, not absorbed silently
- **Annual training compliance** -- first aid, manual handling, dementia care training; if lapsed, the worker technically can't perform certain care tasks

### Stress/Anxiety Points
- Caring for a resident who is actively dying with no family present
- Being the person a resident confides in about pain or fear -- carrying that alone
- Families who blame staff for natural decline
- Chronic understaffing -- being asked to do more with less, every shift
- Making an error that affects a vulnerable person's safety
- The difficulty of escalating concerns when you're uncertain ("what if I'm overreacting?")
- Compassion fatigue that's never named

### Data Sources
- Care management systems (eCase, AlayaCare, Leecare, AutumnCare)
- Electronic medication administration records (eMAR)
- Shift handover notes
- Incident reporting systems
- Training compliance portals

### Proactive AI Opportunities -- "How Did It Know?"

> *"Your shift notes show Mr. Okafor has eaten less than 30% of his meals for the last 4 days. Combined with the confusion noted yesterday, this pattern sometimes precedes a urinary tract infection in elderly males. Worth flagging to the RN on duty today."*

> *"Your manual handling competency assessment expires in 6 days. The next in-facility session is this Thursday at 2pm. You're rostered off -- but if you miss this, you may need to work without manual handling clearance until the next session."*

> *"Mrs. Singh's daughter called the facility 3 times yesterday and didn't reach a staff member. She's known to escalate quickly -- someone may want to proactively return her call this morning before it becomes a formal complaint."*

> *"You've had 3 bereavement events in the last 4 weeks. The facility's Employee Assistance Program offers free counselling sessions. It might be worth taking one -- this is a heavy run."*

---

## 4.2 DISABILITY SUPPORT WORKERS

### What makes this role unique (vs. aged care)
Disability support workers work with people across all age groups -- children to elderly -- with a vast spectrum of conditions (physical, intellectual, psychosocial, acquired brain injury). The key difference from aged care: **the goal is capacity-building, not just maintenance**. Aged care often involves managing decline; disability support often involves supporting growth, independence, and participation. The worker's role is to empower, not just assist -- and the tension between doing things *for* participants vs. *with* them is a daily ethical question.

Also unique: **NDIS (Australia) / Medicaid waiver complexity**. The funding is attached to each participant's plan and has strict rules about what can be claimed under which support categories. Workers and their employers must navigate this constantly.

### Daily/Weekly Rhythm
- Shift-based, community access, or in-home support depending on the client and their plan
- **Community access shifts:** attending appointments, recreational activities, social skills practice -- highly variable
- **In-home shifts:** personal care, domestic assistance, meal preparation, communication support
- **Supported Independent Living (SIL):** residential support, similar rhythm to aged care but with a capacity-building focus

### Before Tasks
- Participant's care plan reviewed (especially for new or complex participants)
- Behaviour support plan reviewed if participant has challenging behaviours
- Equipment checks (wheelchair, AAC device, hoist) -- is everything operational?
- Any updates from the previous shift or from the participant's family/coordinator?

### After Tasks
- Shift notes -- progress toward goals, any incidents, changes in behaviour
- NDIS service delivery records updated (supports need to be claimed within a window)
- Incident reports for any restrictive practices, accidents, or property damage
- Handover to next worker

### Time-Sensitive Triggers
- **NDIS plan review approaching** -- a participant's plan typically runs 12 months; the review meeting needs preparation, evidence of progress, updated goals; missing the review window can mean a gap in funding
- **Service agreement expiry** -- the agreement between the participant and the provider has an end date; if not renewed, services can't continue under NDIS rules
- **Restrictive practice monitoring** -- any use of a restrictive practice (even low-level, like redirection) must be documented and reviewed; compliance failures have serious consequences
- **Challenging behaviour incident** -- a participant exhibiting new or escalating challenging behaviour requires a behaviour support specialist review; the longer this is delayed, the harder it becomes
- **SIL roster gap** -- in Supported Independent Living, a roster gap is a compliance failure (someone required 24/7 support was left alone); this needs to be flagged immediately
- **Participant complaint or NDIS Commission complaint** -- formal complaints trigger mandatory responses within specific timeframes
- **Worker registration/NDIS Worker Screening** -- the screening check must be current; it's a criminal offence to work with NDIS participants with an expired screening

### Stress/Anxiety Points
- A participant having a meltdown or violent episode in public
- Not knowing how to handle a complex behaviour and being alone on shift
- Making a documentation error that could be seen as fraudulent NDIS claiming
- Witnessing restrictive practices being used inappropriately by colleagues
- Low pay relative to the emotional and physical demands
- The gap between what the NDIS plan funds and what the participant actually needs

### Data Sources
- NDIS Provider portals (myplace, PRODA)
- Care management systems (Brevity, ShiftCare, Lumary, HumanAbility)
- Behaviour support plans (from registered behaviour support practitioners)
- Worker screening portals (NDIS Quality and Safeguards Commission)

### Proactive AI Opportunities -- "How Did It Know?"

> *"Marcus's NDIS plan review is in 11 weeks. The Support Coordinator needs goal progress evidence by week 8. Based on your shift notes, you have strong progress on his independent transport goals -- want me to compile a summary?"*

> *"Your NDIS Worker Screening clearance expires in 4 months. The renewal takes 6-8 weeks. Given the current processing backlog, you should apply now to avoid a lapse."*

> *"There were 3 incidents involving Jamie this week -- twice involving loud environments triggering distress. The Behaviour Support Plan hasn't been reviewed in 8 months. This pattern may warrant requesting a review from the BSP."*

---

## 4.3 YOUTH WORKERS

### What makes this role unique
Youth workers engage with young people in a variety of settings -- schools, youth centres, outreach programs, residential care, justice settings. The unique challenge: **young people engage on youth people's terms** -- build the relationship over weeks or months, or lose them permanently. This makes the rhythm very different from clinical or administrative roles: it's relationship-first, results-second.

The other unique dimension: **mandatory reporting**. Youth workers are mandated reporters in most jurisdictions -- if they suspect abuse or neglect, they have a legal obligation to report. And the timing and manner of this can be agonising when the young person has just started to trust them.

### Daily/Weekly Rhythm
- Drop-in or scheduled program sessions (afternoons/evenings for school-aged youth)
- Outreach sessions (going to young people, not waiting for them to come in)
- Case file documentation (often after hours -- when the young people are gone)
- Team meetings and case conferences
- **Irregular rhythm is the norm** -- youth workers work when young people are available, which is often evenings and weekends

### Before Tasks
- Reviewing any recent changes in a young person's situation (from case notes or case conference)
- Program activity prep
- Safety planning for any high-risk young people expected today
- Checking if any mandatory reports need to be followed up

### After Tasks
- Case notes written while memory is fresh
- Any disclosures or concerning observations documented accurately
- Mandatory report made if threshold was reached
- Supervisor briefed on anything high-risk

### Time-Sensitive Triggers
- **Disclosure of abuse** -- a young person discloses abuse or self-harm; the mandatory report clock starts ticking immediately (often 24 hours, varies by jurisdiction and risk level)
- **Missing young person** -- a young person in care who doesn't turn up for a scheduled session and isn't contactable; when does this become a welfare check or missing persons report?
- **Young person in crisis** -- a young person reaching out via SMS at midnight in crisis; what's the response protocol outside business hours?
- **Case conference deadline** -- a statutory child protection case conference has a specific date; preparation needs to be done in the days before
- **Program funding cycle** -- many youth programs run on annual government grants with acquittal deadlines; underreporting against KPIs can affect next year's funding
- **Transition from care** -- a young person turning 18 and "aging out" of the system needs to have transition planning completed weeks before their birthday, not after

### Stress/Anxiety Points
- Carrying a disclosure alone before the mandatory report is made
- A young person disengaging after a difficult interaction
- Vicarious trauma -- hearing repeated stories of abuse, violence, and suffering
- Budget cuts threatening programs that young people depend on
- The ethical tension between building trust and mandatory reporting obligations
- Burnout that's normalised and therefore goes unaddressed

### Proactive AI Opportunities -- "How Did It Know?"

> *"Jordan hasn't attended his Wednesday session for 3 weeks. His last check-in note mentioned instability at home. Based on your program's protocol, this is at the threshold for a welfare check call. Want me to draft a reaching-out message?"*

> *"Your quarterly program report is due in 10 days. Based on your case notes, you've had 47 young people through the drop-in this quarter. The KPI target was 40. You're on track -- want me to compile the numbers from your case management system?"*

> *"It's 11:47pm. Based on your notes, Tyler has reached out to you late at night before when in crisis. Your organisation's after-hours protocol says this should be directed to the crisis line number. Do you want me to prepare a message template you can send quickly if he contacts you tonight?"*

---

## 4.4 LIFE COACHES

### What makes this role unique
Life coaches operate in a largely unregulated profession -- anyone can call themselves a life coach, which means credentialed coaches are constantly fighting perception battles. The unique pressure: **demonstrating ROI on an intangible product**. A client pays $500/month and asks "what am I actually getting?" This makes testimonials and transformation stories existentially important to the business.

Also unique: the **dual role paradox** -- a life coach helps clients with clarity, goals, and self-management, but often struggles with the exact same things in their own business. The cobbler's children have no shoes.

### Daily/Weekly Rhythm
- Coaching calls (1:1, group): the actual product delivery
- Prep for coaching sessions (reviewing session notes, preparing frameworks)
- Business development (content creation, social media, lead follow-up)
- Admin (invoicing, scheduling, CRM updates)
- Supervision or peer coaching (good coaches invest in their own development)

**Weekly:**
- Monday: review the week's sessions, prep notes
- Content creation: 2-3 hours for social/email
- Friday: admin day -- invoicing, follow-ups, book new discovery calls

### Before Tasks (before a coaching session)
- Review previous session notes -- what was the client working on?
- Review stated goals for this session (if client pre-submitted reflection)
- Mental and emotional reset -- you need to be fully present

### After Tasks
- Session notes written (these are private, but essential for continuity)
- Any homework/commitments documented and set for follow-up
- Invoice raised if not on retainer

### Time-Sensitive Triggers
- **Client renewal** -- a coaching package is ending in 2 weeks; the renewal conversation needs to happen before the last session, not on it
- **Client crisis between sessions** -- a client reaches out via WhatsApp in a moment of crisis; response protocol needs to be established in the intake agreement
- **ICF/credential renewal** -- International Coaching Federation credentialling requires CCEUs; these expire and require documentation
- **Discovery call no-show** -- a prospect who was warm books a discovery call and doesn't show; follow-up within 1 hour has the highest re-engagement rate
- **Testimonial window** -- the best time to request a testimonial is within 48-72 hours of a client achieving a significant breakthrough or goal
- **Content drought** -- not posting consistently kills inbound enquiries; coaches often go quiet during busy coaching periods and then wonder where the next clients are

### Stress/Anxiety Points
- A client not making progress and doubting the investment
- Charging their value when peers are underselling
- Scope creep into therapy territory (legal/ethical risk)
- Isolation -- no colleagues, no team, no watercooler
- Imposter syndrome -- particularly prominent in a profession where "who are you to coach?"
- The feast/famine cycle of client acquisition

### Proactive AI Opportunities -- "How Did It Know?"

> *"Emma Clarke's 12-session package ends in 2 weeks. Based on your notes, she's had significant breakthroughs around her career transition. This is typically the right time to have a renewal conversation -- while transformation is fresh. Want me to draft a renewal offer?"*

> *"You haven't posted on Instagram in 11 days. Your last 3 clients cited Instagram as their first touchpoint. Based on your patterns, posting gaps of >10 days correlate with slower enquiry periods 3-4 weeks out. Even a quick insight post today would help."*

> *"Your ICF ACC credential renewal requires 40 CCEUs by November and you have 24 logged. There's a virtual supervision group running this Thursday that would earn you 2 CCEUs -- want me to book it?"*

> *"Your 2pm discovery call with Michael Torres didn't occur. He hasn't messaged. Prospects re-engaged within the first hour after a no-show have a 3x rebooking rate compared to next-day follow-up. Want me to draft a quick 'missed you today' message now?"*

---

## 4.5 CAREER COUNSELORS

### What makes this role unique
Career counselors work in three distinct contexts that have completely different rhythms: **school/university settings** (high volume, age-cohort-driven, institutional calendar), **private practice** (small business dynamics, client acquisition, very similar to life coaching), and **government employment services** (case management, compliance targets, high caseloads). Each is a different product.

The unique pressure across all three: **outcomes are long-tail** -- a career counselor's work pays off over months or years, not sessions. This makes it hard to demonstrate value in the moment and easy for clients/institutions to undervalue the service.

### Daily/Weekly Rhythm (University/School Setting)
- Individual appointments throughout the day (30-60 min each)
- Drop-in hours (high variability -- feast/famine)
- Group workshops and seminars (resume writing, interview prep)
- Employer liaison (connecting students with recruiters, organising career fairs)
- Administrative time for case notes, referrals, reports

**Private Practice:**
- Similar to life coach rhythm -- sessions, marketing, admin
- Heavy LinkedIn and professional network maintenance

### Time-Sensitive Triggers
- **Graduate application deadlines** -- large employers open and close graduate programs in specific windows; missing these is career-altering for students; counselors need to be proactive in reminding
- **Exam period vs. career fair timing** -- career fairs often clash with assessment periods; counselors need to plan content accordingly
- **Annual appointment surge** -- final-year students in semester 2 create enormous demand; capacity needs to be managed
- **Economic shifts affecting graduate outcomes** -- a major employer in the field the counselor serves announces layoffs; their entire cohort is affected immediately
- **LinkedIn algorithm changes** -- platform changes affect job search strategies they're teaching; outdated advice is damaging
- **Accreditation/CPD** -- CDAA, NCDA, or equivalent body renewal requirements

### Stress/Anxiety Points
- Being blamed for a client not getting a job (outcome partially outside their control)
- Giving career advice in rapidly changing industries
- High student-to-counselor ratios in institutions (200:1 is not uncommon)
- Supporting highly anxious clients through job rejections
- Keeping up-to-date with hiring practices, salary benchmarks, and in-demand skills

### Proactive AI Opportunities -- "How Did It Know?"

> *"Commonwealth Bank's graduate program applications close in 6 days. You have 14 active students who noted banking/finance as a career interest. None have mentioned applying. Want me to send them a reminder with the link?"*

> *"Your busiest booking period (November-December, final-year students) is 8 weeks away. Based on last year, you were fully booked by week 2 and turned away 30+ students. Want to set up a waitlist system or group workshop for overflow?"*

> *"LinkedIn just changed its resume import feature -- the old method you're teaching in your resume workshops no longer works. I've flagged the relevant help article. Want to update your workshop slides?"*

---

## 4.6 FOSTER CARERS

### What makes this role unique
Foster carers are not professionals in the traditional sense -- they're approved household caregivers for children placed by child protection services. But the administrative, emotional, and regulatory demands are closer to a professional role than most people realise. They navigate multiple bureaucracies (the placing agency, the child's caseworker, the biological family's access arrangements, the school system, the health system) simultaneously, for a child who may arrive with no warning and significant trauma.

The unique dimension: **placement dynamics**. A carer might be asked to take an emergency placement at 10pm on a Friday. The child has nothing with them. They may not know the child's medical history, their triggers, or their name until the handover documents arrive. And they're expected to provide stable, therapeutic care from minute one.

### Daily/Weekly Rhythm
- For foster carers with a child in placement: essentially parenting rhythm plus extraordinary admin
- Morning: school prep, medication administration (if applicable), any appointments
- Daytime: managing their own household, any agency-required documentation
- After school: therapeutic activities, contact visit preparation (if family contact is scheduled)
- Evening: safe care documentation if required, any incident notes
- **Weekly:** court reports (if a case is before the court), access visit transport, caseworker visits

### Before Tasks
- Contact visit preparation -- child emotionally prepared? Transport organised? Required documentation?
- Any court appearance preparation for a case review?
- Medical or therapy appointment confirmed?
- Any school communication that needs addressing?

### After Tasks
- Post-contact visit observation notes (how did the child present before/after contact with birth family?)
- Any incidents documented (behaviour, disclosure, injury)
- Daily care logs updated (some agencies require detailed daily logs)
- Anything flagged to the caseworker

### Time-Sensitive Triggers
- **Emergency placement call** -- can arrive any time; the carer has to decide within minutes whether they have capacity; saying yes when they don't is catastrophically harmful
- **Court date notification** -- foster carers often need to provide reports or appear in court; notification can come with minimal lead time
- **Placement breakdown risk** -- a child's behaviour is escalating beyond the carer's capacity; recognising this and escalating before breakdown is critical for the child's wellbeing
- **Contact visit cancellation** -- a birth parent doesn't show for a scheduled contact visit; the child has been prepared and is now let down; immediate therapeutic response needed
- **Medical consent gap** -- a child needs emergency medical treatment and the carer doesn't have authority to consent; the placing authority needs to be reached immediately
- **Annual re-approval** -- foster carers must be re-approved annually; the process involves home assessments, training hours, and referees; missing the window means a lapse in approved status
- **Respite carer needed** -- a carer approaching burnout needs approved respite; these arrangements take time to organise but feel impossible to ask for

### Stress/Anxiety Points
- The unpredictability -- nothing about foster care is predictable
- The grief when a placement ends (the child leaves, the carer grieves)
- System failures -- a caseworker who doesn't return calls, a court decision that makes no sense
- Biological family dynamics -- contact visits that retraumatise the child
- The financial squeeze -- reimbursements rarely cover actual costs, and carers rarely ask for more
- Being blamed for a child's behaviour by schools or medical professionals who don't understand the child's history
- Carrying trauma responses from a child that was once someone else's horrific experience

### Data Sources
- Agency placement management systems (variable by jurisdiction)
- Documentation apps (Care Monkey, Brolga, paper-based in many smaller agencies)
- Court document portals (jurisdiction-specific)
- Children's health records
- School communication apps (Seesaw, Skoolbag)

### Proactive AI Opportunities -- "How Did It Know?"

> *"Jack's birth mother contact visit is tomorrow at 2pm. Based on your last 3 post-visit notes, Jack has shown heightened anxiety for 24 hours after contact. You might want to have his calming activity kit ready and keep Thursday evening low-stimulation."*

> *"Your annual carer re-approval assessment is in 10 weeks. The training hours requirement shows 12 completed against 20 required. The agency runs a group session on trauma-informed parenting next Thursday -- that's 4 hours toward your requirement."*

> *"It's been 3 weeks since you've had a break. Your last respite weekend was in January. The agency has 2 approved respite carers available for Jack's age group. Would it help if I drafted a respite request?"*

> *"Jack has a medical appointment tomorrow but his Medicare card and health summary are in the placement documentation from November. The specialist may ask for updated consent paperwork. Want me to remind you to pack those?"*

---

# CROSS-CUTTING INSIGHTS FOR PULSE

## Patterns That Emerge Across All 28 Roles

### 1. The "Invisible Deadline" Problem
Nearly every role has deadlines that are known but not tracked properly:
- Licence/registration renewals (pharmacy, security, locksmiths, vet nurses, interpreters)
- Insurance renewals (physio clinics, MSPs, security companies)
- Certification expirations (CPD for all healthcare roles, NDIS screening, foster carer re-approval)
- Contract renewal windows (IT contracts, VA retainers, coaching packages)

**Pulse opportunity:** Calendar-connected deadline intelligence that surfaces these 4-8 weeks before they become urgent, not the day before.

### 2. The Communication Gap
Almost every role has a communication failure that costs them:
- Customers/clients expecting updates they're not getting (appliance repairs, lab delays for opticians)
- Patients/clients who need reminders they won't send themselves (pharmacy recalls, vet vaccinations)
- Escalations that should happen but don't (aged care deterioration, youth worker welfare concerns)

**Pulse opportunity:** Proactive communication drafting -- not just reminding the person to communicate, but drafting the message so they only need to approve.

### 3. The Monday Morning Dread
Many roles have a specific anxiety moment at the start of each week or shift:
- MSP owners: overnight alert backlog
- Security company owners: roster gaps for the week
- Practice managers: first-day-back admin accumulation

**Pulse opportunity:** A pre-shift or pre-week brief that surfaces exactly what needs attention, in priority order.

### 4. Revenue Leak Points
Most roles have predictable, preventable revenue losses:
- Appointment gaps (physio, dentist, optician)
- Overdue invoices (graphic designers, web developers, VAs, locksmiths)
- Expiring approvals that prevent billing (WorkCover, NDIS)
- Missed follow-ups that become cancellations (appliance repairs)

**Pulse opportunity:** Revenue protection prompts -- "here's what's about to slip through the cracks."

### 5. Emotional Labour is Invisible
Roles like aged care workers, vet nurses, youth workers, and foster carers carry enormous emotional weight that is almost never formally acknowledged:
- Compassion fatigue cycles
- Grief processing gaps
- Vicarious trauma accumulation

**Pulse opportunity:** Gentle check-ins and resource surfacing ("you've had a heavy run of losses this month -- the EAP is available") -- not therapy, but awareness.

---

## Data Integration Priorities for Pulse

| Data Source Type | Roles | Integration Value |
|---|---|---|
| Calendar | All roles | Foundation of all scheduling triggers |
| Email | All roles | Invoice aging, client communication gaps |
| Regulatory portal APIs | Healthcare, trades, security | Licence/registration expiry alerts |
| Practice management software | Healthcare roles | Patient recall, billing gaps |
| Job management apps | Trades, freelancers | Follow-up reminders, invoice triggers |
| RMM platforms | MSP owners | Alert aggregation, SLA monitoring |
| Amazon Seller Central | FBA sellers | Inventory, listing status |
| Invoicing software | All freelancers | Overdue invoice detection |
| Weather APIs | Pest control, pool technicians | Schedule adjustment triggers |
| NDIS portals | Disability support | Plan review, billing compliance |

---

*End of Research Document*
*Total roles documented: 28*
*Categories: Healthcare Adjacent (6), Skilled Specialist Trades (6), Freelance/Gig (8), Community & Care (4)*
