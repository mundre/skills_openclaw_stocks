# Pulse -- Transport & Logistics Role Research
**Product:** Pulse -- Proactive AI Assistant
**Research Date:** 2026-03-17
**Purpose:** Deep role research to identify proactive AI trigger moments across transport & logistics verticals

---

## Table of Contents
1. [Long-Haul Truck Drivers](#1-long-haul-truck-drivers)
2. [Logistics Coordinators](#2-logistics-coordinators)
3. [Warehouse Managers](#3-warehouse-managers)
4. [Freight Forwarders / Customs Brokers](#4-freight-forwarders--customs-brokers)
5. [Fleet Managers](#5-fleet-managers)
6. [Courier / Delivery Drivers (Gig & Employed)](#6-courier--delivery-drivers-gig--employed)
7. [Airline Pilots](#7-airline-pilots)
8. [Air Traffic Controllers](#8-air-traffic-controllers)
9. [Maritime / Ship Officers](#9-maritime--ship-officers)

---

## 1. Long-Haul Truck Drivers

### Daily/Weekly Rhythm
Long-haul drivers operate on highly variable schedules dominated by Hours of Service (HOS) regulations. In the US, the federal limit is **11 hours driving within a 14-hour on-duty window**, followed by a mandatory **10-hour off-duty period**. In the EU it's **9 hours driving** (extendable to 10 twice a week) with mandatory 45-minute breaks every 4.5 hours.

**Typical week:**
- Mon: Pre-trip, load at origin depot (3-5hrs), drive 600-800km, overnight at truck stop
- Tue-Thu: Full driving days, fuel stops, mandatory 30-min breaks, sometimes border crossings
- Fri: Deliver, unload (2-4hrs), deadhead or new load pickup, drive back or restart
- Weekend: Often a 34-hour restart at home or a truck stop to reset weekly HOS

**Route complexity:** Long-haul routes span multiple states/provinces/countries. Drivers manage weight restrictions per road type, low bridge clearances (especially UK/EU), hazmat routing restrictions, and seasonal road bans (spring load restrictions on soft roads in Canada/Northern US).

**Shift patterns:** No fixed shift. Drivers often run nights to avoid traffic and meet morning delivery windows. Sleep rhythm inverts regularly. Team drivers (two drivers in one truck) run nearly 24/7 with shared driving time.

---

### Before Tasks (Pre-Trip)
- **DVIR (Driver Vehicle Inspection Report):** Legally mandated in US/Canada/EU. Covers tyres, brakes, lights, mirrors, coupling devices, fluid levels, horn, wipers. Takes 20-45 minutes.
- **ELD sync check:** Verify Electronic Logging Device is connected, synced, and HOS clock is accurate
- **Load documentation review:** Bill of Lading (BOL), weight manifest, hazmat placards if applicable, temperature settings for reefer (refrigerated) units
- **Route pre-planning:** Weight/height restrictions, toll routes, construction detours, weather (especially in winter -- black ice, mountain passes, fog)
- **Fuel planning:** Plan fuel stops based on tank range (~1,200km typical) and diesel price differentials between states/countries
- **Load securement check:** Verify cargo straps, load bars, seals on containers
- **Reefer pre-cool:** Refrigerated trailers need to be pre-cooled 1-2 hours before loading perishables
- **Border crossing prep:** If international run -- FAST card, PARS/PAPS numbers ready, customs broker contact confirmed

---

### After Tasks (Post-Trip)
- **Post-trip inspection DVIR:** Required by law -- any defects reported to carrier
- **ELD submission:** HOS logs auto-submitted but driver must certify accuracy
- **Delivery receipts:** POD (Proof of Delivery) -- physical or electronic signature capture
- **Fuel receipts:** Upload to fleet management system or IFTA (International Fuel Tax Agreement) reporting
- **Incident/accident reports:** Any event (even minor) must be documented same day
- **Reefer temperature logs:** Download and submit cold chain data for perishable loads
- **Customs clearance confirmation:** Verify broker received all documents, no holds placed
- **Detention time log:** Document any time waiting at shipper/receiver beyond free time (billable)
- **Load completion in TMS:** Mark load delivered in Transport Management System

---

### Time-Sensitive Triggers

| Trigger | Threshold | Consequence of Missing |
|---|---|---|
| HOS daily driving limit | 11h/day (US) | Automatic violation, fine, potential out-of-service |
| HOS weekly limit | 60/70h in 7/8 days | Out-of-service order |
| 30-min break requirement | After 8h driving | Violation |
| Driver's licence CDL renewal | Varies by state (4yr avg) | Can't legally drive commercially |
| Medical certificate (DOT physical) | Every 2 years (annually if conditions) | Licence downgraded, can't drive |
| Hazmat endorsement | Every 5 years (background check) | Can't carry hazmat |
| Vehicle registration | Annual | Out-of-service at weigh station |
| Annual vehicle inspection | Annual | Out-of-service |
| Reefer temperature window | Cargo-specific (e.g., 0-4C for fresh produce) | Load rejection, financial loss |
| Perishable delivery window | Often same-day or 24hr | Cargo loss, penalty |
| IFTA quarterly tax filing | Mar/Jun/Sep/Dec | Fines + interest |
| Dangerous goods recertification | Every 3 years (varies) | Can't haul DG |

---

### Stress / Anxiety Points
- **HOS clock ticking:** Approaching the 14-hour window with delivery still 2 hours away. Choice between violation or disappointing the customer.
- **Weather surprises:** Mountain pass closes mid-route. No alternative. Sitting for 6-12 hours losing HOS.
- **Weigh station overweight:** Load that was supposed to be legal isn't. Risk of fine, load redistribution, or tow.
- **Border delays:** Customs holds a load for 4-8 hours. Temperature-sensitive cargo deteriorating. Customer livid.
- **Mechanical breakdown:** Middle of nowhere, waiting for roadside assistance. Missing delivery window. Cascading effect on next load.
- **Detention time:** Shippers/receivers keep driver waiting beyond free time. Unpaid waiting that burns HOS.
- **Fuel price spikes:** Owner-operators particularly stressed -- diesel at $1.60/L when bid assumed $1.30.
- **Medical recertification anxiety:** Heart condition, blood pressure, sleep apnoea -- any of these can pull a CDL.
- **Load rejection at delivery:** Paperwork error, wrong temp, or damaged goods. Who pays?

---

### Data Sources
- **ELD devices:** Samsara, Keeptruckin (Motive), Omnitracs, PeopleNet -- real-time HOS, location, vehicle diagnostics
- **TMS (Transport Management System):** McLeod, TMW, Mercury Gate -- load details, BOL, dispatch instructions
- **Weather:** Weather.com, Windy, Dark Sky (deprecated), in-cab Garmin/Rand McNally truck GPS with weather overlay
- **Fuel:** GasBuddy, TCS Fuel, Comdata -- fuel card pricing across truck stop networks
- **FMCSA Portal (US):** Driver record, CSA scores, inspection history
- **Customs portals:** ACE (US), CERS (Canada), CHIEF/CDS (UK), AES/NCTS (EU)
- **Load boards:** DAT, Truckstop.com -- for owner-operators finding loads
- **Reefer monitoring:** Carrier Transicold, Thermo King -- temperature logs accessible via app

---

### Proactive AI Opportunity -- "How Did It Know?" Moments

> **"Your DOT medical certificate expires in 47 days. Your nearest certified medical examiner has openings next Tuesday or Thursday. Want me to book one? Missing this means your CDL drops to Class B automatically."**

> **"You've been on duty 11.5 hours. Based on your current position, you're 2h 20min from the Flying J in Amarillo. You won't make your delivery window and stay legal. Want me to notify dispatch now so they can set customer expectations? I can also find the nearest legal parking in case you need to stop sooner."**

> **"Your reefer is showing 6.8C -- it's been above the 4C threshold for 22 minutes on this beef load. That's approaching the rejection threshold. Thermo King diagnostic suggests a condenser airflow issue. Closest Carrier Transicold dealer is 18km off-route. Call now or push through?"**

> **"Spring load restrictions come into effect on Highway 11 in Ontario on April 1st -- that's 6 days away. Your regular Toronto-Thunder Bay route uses that road. I've mapped an alternative via Hwy 17 that's 94km longer but fully unrestricted. Want me to flag this to dispatch for the next three weeks of bookings?"**

> **"You crossed into New Mexico 40 minutes ago. Your IFTA mileage tracker shows you haven't logged fuel from the Love's in El Paso -- that receipt needs to be uploaded for accurate quarterly reporting. Want me to remind you at end of day, or flag it to your fleet manager now?"**

---

## 2. Logistics Coordinators

### Daily/Weekly Rhythm
Logistics Coordinators (also called Freight Coordinators, Shipping Coordinators, or Supply Chain Coordinators) are the operational nerve centre -- they don't move cargo themselves, they orchestrate everything that does.

**Typical day:**
- **06:00-08:00:** Review overnight shipment status, check for delays, escalate anything critical before business hours
- **08:00-10:00:** Carrier booking -- confirm today's loads, chase unconfirmed pickups, manage driver assignments
- **10:00-12:00:** Documentation -- prepare BOLs, packing lists, export declarations, check customs clearance status on inbound
- **12:00-14:00:** Customer communication -- proactive status updates, exception handling (delays, shorts, damages)
- **14:00-17:00:** Plan tomorrow's loads, book carriers, arrange special equipment (reefer, flatbed, oversize)
- **17:00+:** Escalations -- anything that went wrong today that needs a fix tonight

**Weekly pattern:** Monday is chaos (catching up from weekend + new week loads). Friday is controlled chaos (closing the week, pre-planning weekend movements). Wednesday tends to be heaviest documentation day.

**In many companies, coordinators cover rotating on-call shifts** -- late nights and weekends to handle live freight issues.

---

### Before Tasks
- **Morning shipment audit:** Every in-transit load reviewed against ETA. Any variance flagged.
- **Carrier confirmation calls:** Verify drivers are confirmed for today's pickups (especially spot/brokered loads)
- **Documentation prep:** BOL, commercial invoice, packing list, certificates of origin, phytosanitary certs for food/ag
- **Customs pre-lodgement:** File entry summaries, ISF (Importer Security Filing) in US must be filed 24hr before vessel departure
- **Dangerous goods pre-notification:** DG shipments require advance carrier notice and appropriate placarding
- **Customer cut-off management:** Know which customers have hard booking cut-offs (e.g., ocean carrier cut-off is 2 days before vessel departure)

---

### After Tasks
- **POD collection:** Chase carriers for signed Proof of Delivery, upload to TMS/WMS
- **Freight invoice reconciliation:** Compare carrier invoices against agreed rates, flag accessorial charges (fuel surcharges, detention, liftgate)
- **Claims management:** Initiate cargo claims for damage/shortage, gather documentation
- **Carrier performance logging:** On-time %, damage rate, communication score
- **KPI reporting:** Daily/weekly dashboard updates -- fill rate, on-time delivery, cost per shipment
- **Exception reports:** Any shipment that didn't go to plan -- document cause, cost, resolution

---

### Time-Sensitive Triggers

| Trigger | Threshold | Consequence |
|---|---|---|
| ISF filing (US imports) | 24h before vessel load | $5,000/violation penalty |
| Ocean carrier VGM (container weight) | Cut-off varies (typically 24-48h before vessel) | Container refused |
| Export customs filing | Before departure (timing varies by country) | Cargo held, fines |
| Perishable cargo booking | Must be confirmed 24-72h ahead | Carrier unavailable, cargo loss |
| Carrier rate expiry | Spot quotes valid 24-48h typically | Price changes |
| LTL pickup cut-off | Usually 15:00-16:00 local | Miss same-day pickup |
| Reefer pre-cool order | 2-3h before load | Temperature compliance breach |
| Letter of Credit expiry | Trade finance specific | Payment loss |
| Phytosanitary certificate validity | Varies (often 30 days from issue) | Cargo refused at border |

---

### Stress / Anxiety Points
- **Carrier no-show:** A driver doesn't appear for a time-critical pickup. Scrambling for cover at elevated spot rates.
- **Vessel miss:** Documentation late, container misses the vessel. Cargo sits a week for the next sailing.
- **Customs hold:** Unexpected exam or documentation query delays clearance -- customer screaming.
- **Cascading delays:** One late delivery causes a production line shutdown at the customer's facility.
- **Over-commitment:** Booked more loads than available carriers. Managing multiple disappointed shippers at once.
- **Claims management backlog:** Multiple open claims, carriers slow-walking responses, finance chasing.
- **Rate disputes:** Carrier invoices with unexpected charges -- negotiating after the fact.

---

### Data Sources
- **TMS:** Oracle Transportation Management, SAP TM, McLeod, Descartes -- load planning and execution
- **Track & trace portals:** Project44, FourKites, Visibility Hub -- real-time shipment location
- **Customs portals:** CBP ACE (US), HMRC CDS (UK), AMS (EU), SARS RLA (SA)
- **Ocean carrier portals:** Maersk, MSC, CMA CGM -- booking, cut-offs, vessel schedules
- **Load boards:** DAT, Transplace -- spot coverage
- **Communication:** Email, WhatsApp (increasingly), carrier EDI (214/214A status messages)
- **ERP:** SAP, Oracle, NetSuite -- order management, invoicing

---

### Proactive AI Opportunity

> **"The Maersk Sealand vessel for your Rotterdam shipment has been blanked -- Maersk cancelled the sailing. Next available vessel departs in 9 days. You have 3 customer orders on that booking. Want me to draft the customer notifications and check alternatives on MSC and CMA CGM for this week?"**

> **"ISF filing is due in 6 hours for the Shanghai container arriving January 14th. I don't see a filing confirmation in the system yet. Your broker is Santos Freight -- want me to send them an urgent chase now?"**

> **"Carrier on load #TK-4471 hasn't checked in since 14:30 and was due at the cold store at 17:00. It's now 17:45. I've tried the driver's number -- no answer. Want me to escalate to dispatch and notify the cold store?"**

> **"You have 4 phytosanitary certificates expiring in the next 14 days across your Australian export programme. The issuing lab takes 5 business days. If you don't initiate retest this week, you'll breach the August 2nd export window for the citrus consignment."**

> **"Your on-time delivery rate dropped to 84.3% this week -- below your 90% SLA threshold. The two carriers with the most failures are FastFreight (3 lates) and TransLink (2 lates). Want me to generate a performance letter for both, or schedule a review call?"**

---

## 3. Warehouse Managers

### Daily/Weekly Rhythm
Warehouse Managers run a facility that is essentially a live inventory organism -- constantly receiving, storing, picking, packing, and dispatching. Shifts are typically 10-12 hours with a skeleton crew on nights.

**Typical day:**
- **05:30-06:30:** Walk the floor before shift change -- check overnight progress, note exceptions
- **06:30-08:00:** Shift briefing, assign picking/packing zones, review inbound schedule
- **08:00-12:00:** Manage inbound receiving (cross-checking against POs), oversee picking for AM outbound wave
- **12:00-14:00:** Outbound wave dispatch -- carrier check-in, loading, seal and hand off
- **14:00-16:00:** Admin: KPI review, inventory discrepancy investigation, staff HR issues
- **16:00-18:00:** Plan next day -- inbound volumes, space allocation, labour requirement

**Weekly pattern:** Monday is high volume outbound (catching up from weekend orders). Friday outbound is heavy. Cycle counting is typically mid-week. Physical inventory can be monthly or quarterly.

---

### Before Tasks
- **Labour planning:** Match staff to expected wave volumes. Arrange casuals if volume surge expected.
- **Equipment checks:** Forklifts, reach trucks, pallet jacks -- daily safety check before first use
- **Space planning:** Clear staging areas, allocate bays for inbound trucks
- **WMS wave release:** Review and release picking waves in the Warehouse Management System
- **Inbound schedule review:** Know what's arriving, when, from where -- especially time-sensitive (reefer, DG, high-value)
- **Temperature zone checks:** Ambient/chilled/frozen -- verify correct temps recorded overnight
- **Dangerous goods location check:** DG stored in correct segregated areas

---

### After Tasks
- **EOD inventory reconciliation:** Compare picks vs WMS expected -- investigate variances
- **Outbound scan confirmation:** All pallets loaded and scanned out -- no phantom inventory
- **Equipment damage reports:** Any forklift incident or racking strike logged
- **Staff timesheet sign-off**
- **Temperature log download:** Cold chain records for QA
- **Carrier performance notes:** Any no-shows, late arrivals, damage observed at loading
- **Housekeeping sign-off:** Aisle clear, emergency exits clear, fire doors closed

---

### Time-Sensitive Triggers

| Trigger | Threshold | Consequence |
|---|---|---|
| Forklift operator licence | Annual/biennial depending on jurisdiction | Operator can't use equipment |
| Racking inspection | Annual (BS EN 15635 in UK, OSHA in US) | Regulatory fine, injury liability |
| Fire extinguisher service | Annual | Non-compliance |
| DG storage compliance audit | Varies | Shutdown |
| Perishable inventory -- FEFO management | Product-specific BBD | Waste, recalls |
| Carrier cut-off time | Daily (typically 15:00-16:00) | Miss carrier, orders delayed |
| SLA pick-pack-ship window | Order-specific (e.g., same-day if ordered by 12:00) | Penalty, chargebacks from retailers |
| Retail compliance windows | Retailer-specific (ASDA, Walmart etc.) | Chargebacks up to 5% of invoice |
| Staff certification (manual handling, DG awareness) | Annual typically | Liability |

---

### Stress / Anxiety Points
- **Volume surges:** Black Friday, promotional events -- 3-5x normal volume with same or barely increased staff
- **WMS errors/downtime:** System goes down during peak wave. Manual picking chaos.
- **Inventory discrepancies:** $50K of stock missing. Investigation takes days.
- **Staff absenteeism:** Key forklift operator calls in sick. Equipment sits. Inbound backs up.
- **Carrier late arrival:** Truck arrives 3 hours late, now everything is a recovery situation
- **Racking collapse:** Structural incident stops all operations in a zone for hours or days
- **Retail chargebacks:** Walmart/ASDA/Woolworths issues chargebacks for non-compliance (label, window, mixed pallets)
- **Temperature excursion:** Cold chain breach discovered in morning -- entire pallet potentially unusable

---

### Data Sources
- **WMS:** Manhattan Associates, Blue Yonder (JDA), SAP EWM, Deposco, Fishbowl -- inventory, waves, labour
- **ERP:** SAP, Oracle, NetSuite -- orders, POs, invoicing
- **TMS (outbound):** Integrated or separate -- carrier bookings, tracking
- **Temperature monitoring:** IoT sensors (Sensitech, ELPRO, Monnit) -- live cold chain data
- **Labour management:** Kronos/UKG, Deputy -- timesheets, scheduling
- **Carrier portals:** DHL, UPS, FedEx, TNT -- booking, label generation, POD
- **CCTV/WMS audit trails:** Proof for insurance and investigations

---

### Proactive AI Opportunity

> **"You have 847 units of SKU #FZ-4421 (frozen salmon) hitting best-before date in 6 days. Current pick rate suggests 320 units will move in that window. Want me to flag the remaining 527 units for a markdown or a retail promotion push? I can also check if your Lidl account has a short-notice promotional slot."**

> **"Three of your Toyota reach trucks are overdue for their annual safety inspection -- last service was 13 months ago. The fourth is due in 3 weeks. I found a Toyota forklift service slot this Thursday -- book all four at once and save a second call-out fee?"**

> **"Your Walmart routing guide requires pallets to be labelled with a GS1-128 label on the short side of the pallet. Shipment #WM-8842 is due to load in 2 hours, but I can't see a palletisation confirmation scan in the WMS. Want me to alert the pack team now?"**

> **"Your Tuesday inbound schedule shows 11 trucks arriving between 09:00 and 12:00, but you currently have 4 bays available. Two trucks are carrying your promotional stock for the Valentine's campaign -- those need priority. Want me to resequence arrivals and notify carriers of updated dock appointment times?"**

> **"Staff absenteeism on today's early shift is 22% -- 4 of your 18 booked staff called out. You have a 14:00 carrier cut-off for the Tesco outbound. Based on current pick rate, you'll be short by approximately 200 cases. Want me to contact your labour agency for emergency staff, or should I flag this to the transport team to request a 1-hour extension?"**

---

## 4. Freight Forwarders / Customs Brokers

### Daily/Weekly Rhythm
Freight forwarders arrange the entire journey of goods across borders -- they don't own the trucks, ships, or planes, but they orchestrate all of them. Customs brokers are specialists in the legal/regulatory side of border crossing.

**Typical day:**
- **07:00-09:00:** Review overnight status -- especially sea/air freight that moved while office was closed. Check customs holds, vessel ETAs.
- **09:00-12:00:** New booking intake, rate quoting, carrier booking (sea, air, road, rail)
- **12:00-14:00:** Documentation -- commercial invoices, packing lists, certificates of origin, HS code classification
- **14:00-17:00:** Customs entries -- lodge import/export declarations, respond to queries, arrange duty payments
- **17:00+:** Exceptions -- missed cut-offs, holds, urgent client escalations

**Customs broker specific:** Heavy documentation work. HS code classification (wrong code = wrong duty rate = either overpay or audit risk). Duty calculation. Tariff preference certificates (EUR.1, Form A, GSP). Valuation queries from customs authorities.

---

### Before Tasks
- **Document collection from client:** Commercial invoice, packing list, certificate of origin, licences (export control, CITES permits)
- **HS code verification:** Classify goods under the correct Harmonized System code -- this determines duty rate
- **Duty and tax calculation:** DDP (Delivered Duty Paid) or DAP? Who pays? Pre-calculate to avoid surprises
- **Customs regime selection:** Inward Processing Relief, bonded warehouse, free zone, full duty payment?
- **Sanctions/restricted party screening:** Check consignee, consignor, and country against sanctions lists
- **Export licence check:** Dual-use goods, military items, pharmaceuticals may require export licences
- **Cut-off planning:** Work backwards from vessel/flight departure to ensure all docs submitted in time

---

### After Tasks
- **Entry acceptance confirmation:** Confirm customs authority has accepted the entry (no queries/holds)
- **Duty payment confirmation:** Verify duty and VAT paid where applicable
- **Release notification to client:** "Your cargo has cleared customs and is available for collection/delivery"
- **Archive documentation:** All customs entries must be retained (7 years UK, 5 years US, varies)
- **Import duty deferment reconciliation:** Monthly for duty deferment account holders
- **Post-clearance audit prep:** Any entry flagged by customs for review -- prepare supporting documents
- **Invoice to client:** Freight + customs fees + duty disbursements

---

### Time-Sensitive Triggers

| Trigger | Threshold | Consequence |
|---|---|---|
| ISF (Importer Security Filing) | 24h before vessel loading (US imports) | $5,000 penalty per filing |
| Entry summary filing (US) | Within 15 days of arrival | Penalty |
| UK customs entry | Same day as goods arrive at port | Storage fees, demurrage |
| AES export filing (US) | Before departure (>$2,500 or controlled goods) | Violation |
| EU ENS (Entry Summary Declaration) | 2h before truck arrival, 4h before short sea | Cargo refused at border |
| Certificate of Origin validity | Varies (typically 12 months) | Preference denied |
| Phytosanitary certificate | 7-30 days from issue | Cargo rejected |
| T1 Transit document completion | Must be discharged at destination customs | Financial liability for duty |
| ATA Carnet | Valid for 12 months | Customs liability |
| Temporary admission | Country-specific time limits | Full duty charged |
| Bonded warehouse time limit | US: 5 years, UK: 4 years | Compulsory entry + duty |
| Restricted Party Screening | Pre-shipment | Criminal liability, fines |

---

### Stress / Anxiety Points
- **Customs hold/examination:** Port authority selects a container for physical exam. 2-3 day delay, devanning costs passed to client. Client furious.
- **Wrong HS code discovered post-entry:** Either under-declared duty (audit risk, penalties) or over-declared (need to file an amendment and claim refund)
- **Missing documents at clearance:** Client didn't send certificate of origin. Can't claim preference. Client owes extra duty.
- **Sanctions surprise:** Post-shipment discovery that a party on the transaction is sanctioned. Legal exposure.
- **Demurrage and detention:** Ship arrived, customs cleared, but import agent can't deliver in time -- container hire cost running at 200/day
- **Multiple country complexity:** One shipment transiting 3 countries, each with different documentation requirements
- **Tariff changes:** Government announces new tariffs/trade measures with short notice. Everything repriced.
- **Brexit-style disruption:** Sudden regulatory change. All processes invalidated overnight.

---

### Data Sources
- **Customs portals:** CBP ACE Portal (US), HMRC CDS / CHIEF (UK), SARS Manifest (SA), EU AES/NCTS
- **Tariff databases:** UK Global Tariff, US HTS, EU TARIC -- HS codes, duty rates, measures
- **Restricted party screening:** Descartes, Amber Road, Thomson Reuters ONESOURCE Trade
- **Freight booking platforms:** Flexport, Freightos, Cargowise, Netsol
- **Vessel tracking:** MarineTraffic, VesselFinder, Searoutes
- **Flight tracking:** FlightAware, CargoAI -- for air freight
- **CargoWise:** All-in-one freight forwarding platform -- widely used
- **CHIEF/CDS:** UK customs entry system
- **Client communication:** Email, WhatsApp, EDI (EDIFACT messages)

---

### Proactive AI Opportunity

> **"The EUR.1 certificate on your client's Italian wine shipment was issued on March 3rd. It expires in 12 months, but the Italian Chamber of Commerce typically takes 10 days to reissue. You have 4 shipments scheduled in Q1 next year that will need a new certificate. If you initiate now, you'll avoid any gap. Want me to draft the request to the client?"**

> **"MarineTraffic shows the MSC Glsn is now 3 days behind schedule due to port congestion in Singapore -- it will arrive at Felixstowe on the 24th, not the 21st. Your client has a production start date of the 22nd. I'd suggest notifying them now and checking if there's a faster air freight option for the critical 200-unit sub-assembly. Want a rough quote comparison?"**

> **"I flagged an issue on entry #GB-2024-884421 -- the HS code used (8471.30.00) carries a 0% duty rate, but the goods description 'industrial handheld scanners with cellular module' may fall under 8517.62.00 which carries 3.7%. If HMRC audits this, you're looking at a post-clearance demand plus interest. Recommend a formal classification ruling before you process the next three shipments."**

> **"Your client Apex Manufacturing has a new supplier in Shenzhen. Before you accept the first shipment, I've run a restricted party screening -- the Shenzhen entity name is a close match to an entity on the BIS Entity List. This needs manual review before you proceed. Want me to flag it to your compliance officer?"**

> **"The US-China tariff exclusion on HS 8483.40.90 (gearboxes) expires in 6 weeks. Your client has $2.1M of this product on order. If it ships before expiry, they save approximately $42,000 in Section 301 tariffs. Want me to flag this to their procurement team and check if the orders can be expedited?"**

---

## 5. Fleet Managers

### Daily/Weekly Rhythm
Fleet Managers are responsible for the operational, legal, and financial health of a vehicle fleet -- anything from 10 vans to 10,000 trucks. They don't drive. They manage everything so drivers can.

**Typical day:**
- **07:00-08:30:** Review overnight alerts -- breakdowns, incidents, vehicles off-road
- **08:30-10:30:** Coordination -- arrange recovery for breakdowns, organise replacement vehicles, brief maintenance team
- **10:30-12:30:** Compliance checks -- review DVIR reports, flag defects, schedule repairs
- **12:30-14:00:** Administrative -- insurance renewals, vehicle licensing, fuel card management, driver licence checks
- **14:00-17:00:** Strategic -- analyse telematics data, fuel consumption, driver behaviour scores, plan vehicle replacements

**Weekly:** Monday morning fleet status review. Thursday typically for supplier calls (maintenance providers, tyre companies, fuel card providers). Friday for KPI reporting to senior management.

---

### Before Tasks
- **Shift deployment check:** All vehicles assigned to drivers, all drivers have valid licences and medicals
- **Defect resolution confirmation:** Any vehicle flagged on yesterday's DVIR -- confirmed repaired before going back on road
- **New driver onboarding check:** Any driver starting today -- induction complete, licence verified, insurance added
- **Tachograph/ELD compliance review:** Any violations from previous 24 hours

---

### After Tasks
- **Daily telematics report review:** Speeding events, harsh braking, idling time, fuel consumption anomalies
- **Defect report triage:** Which vehicles need same-day repair vs. next scheduled service?
- **Driver behaviour scoring:** Weekly scores reviewed, coaching flagged for poor performers
- **Mileage and fuel reconciliation:** Total mileage vs. fuel issued -- detect theft or inefficiency
- **Incident report processing:** Accident reports -> insurance notification -> repair authorisation
- **Compliance file updates:** Document service, inspection, and repair records per vehicle

---

### Time-Sensitive Triggers

| Trigger | Threshold | Consequence |
|---|---|---|
| MOT/Vehicle inspection | Annual (UK MOT, US annual DOT inspection) | Illegal to operate |
| Vehicle tax/registration | Annual | Illegal to operate |
| Tachograph calibration | Every 2 years | Illegal to operate vehicle |
| Driver licence check | UK: monthly recommended; varies by country | Liable if unlicensed driver causes accident |
| Driver CPC (Certificate of Professional Competence) | 35h/5 years EU | Licence downgrade |
| Digital tachograph card renewal | Every 5 years | Can't record HOS legally |
| Insurance renewal | Annual (but review monthly) | Uninsured operation |
| LOLER inspection (tail lifts) | 6 monthly | Illegal use, injury liability |
| Tyre replacement threshold | Tread depth legal limit varies (1.6mm EU/UK) | Fine per tyre + prohibition |
| Preventive maintenance schedule | Mileage or time based | Warranty void, breakdown risk |

---

### Stress / Anxiety Points
- **Multiple simultaneous breakdowns:** Three trucks off-road at once. Recovery, replacement, customer impact.
- **DVSA/DOT roadside stop:** Enforcement officer finds a defect. Vehicle prohibited. Customer delivery fails.
- **Licence surprise:** Driver's licence shows a disqualification the company didn't know about. That driver's been driving all week.
- **Major incident:** Accident involving serious injury. Insurance, investigation, potential prosecution of the company for operator licence breach.
- **Fleet funding squeeze:** Management cuts maintenance budget. Fleet manager knows it will increase breakdowns but can't resist.
- **Fuel card fraud:** $8,000 of unusual fuel transactions in a week. Multiple drivers involved?
- **Rental fleet explosion:** Suddenly need 20 temporary vehicles. Market tight, rates double.

---

### Data Sources
- **Telematics:** Samsara, Geotab, Teletrac Navman, Masternaut, Microlise -- location, speed, behaviour, diagnostics
- **Fleet management software:** FleetWave, RTA Fleet, AssetWorks, Fleetio -- maintenance, compliance, costs
- **Fuel card providers:** WEX, Fleetcor, Allstar -- transaction data, consumption
- **DVLA (UK) / FMCSA (US):** Licence checks, operator licence status
- **DVSA (UK):** Prohibition notices, earned recognition scheme
- **Insurance portals:** Broker platforms, first notification of loss (FNOL) systems
- **Tachograph analysis:** Optac, Tachomaster, DD-Tacholog -- HOS compliance analysis
- **Vehicle manufacturer portals:** Ford Fleet, Mercedes FleetBoard -- warranty, recalls, remote diagnostics

---

### Proactive AI Opportunity

> **"You have 7 vehicles with MOTs expiring in the next 30 days. Three are currently deployed on long-haul routes that return Friday. If you book them in Monday, they'll be clear before expiry with 9 days to spare. The other four are local vehicles -- I've found availability at your preferred garage on Wednesday. Want me to block-book all seven?"**

> **"Driver Marcus Webb's telematics shows a pattern of late-night harsh braking events on the M62 corridor -- 11 events this week vs. his average of 2. His shift ends at 23:30. This could be fatigue. I'd recommend a direct conversation before his next shift. His next rostered drive is tomorrow at 18:00."**

> **"Vehicle TK-447 (DAF XF) is showing a coolant temperature warning via OBD -- not a critical alarm yet, but it's trending upward over the last 3 drives. The nearest DAF dealer is 14km from the driver's current location. Better to divert now than a breakdown on the A1 tonight. Driver is James Holt, currently en route to Doncaster."**

> **"Your operator licence O-2021/4471 renewal is due in 6 weeks. The Traffic Commissioner's office recommends submitting 8 weeks ahead. You'll need your latest financial standing evidence, transport manager CPC certificate (Sarah Collins -- still valid until 2027), and an updated maintenance contractor agreement -- your current one with Truck Assist expired last month."**

> **"Fuel card spend analysis for the week shows Vehicle TK-219 used 340L of diesel against a route-expected consumption of 195L. Either the vehicle has a mechanical issue (possible fuel leak or injector fault), or there's an anomaly worth investigating. Do you want me to pull the transaction locations and overlay them with the vehicle's GPS track?"**

---

## 6. Courier / Delivery Drivers (Gig & Employed)

### Daily/Weekly Rhythm
Two distinct segments here with very different operating realities:

**Employed couriers (DHL, UPS, FedEx, Royal Mail, national postal services):**
- Fixed shifts: typically 06:00-15:00 or 08:00-18:00
- Assigned geographic territory (round) with 80-200 stops per day
- Depot-based: sort and load at depot, then deliver
- Union protections, fixed pay, vehicle provided

**Gig couriers (Uber Eats, DoorDash, Amazon Flex, Stuart, Gophr):**
- Self-scheduled: log in when you want to work
- Algorithm-based dispatch -- no fixed round
- Own vehicle (car, bike, scooter, cargo bike)
- Pay per delivery, surge pricing, ratings pressure
- No sick pay, no vehicle maintenance support

**Typical employed courier day:**
- 06:00: Report to depot, sort and load van (1-2hrs)
- 08:00: First delivery
- 12:00-12:30: Lunch break
- 15:00-18:00: Return to depot, POD upload, vehicle return

**Typical gig courier day:**
- Log in to app during a busy window (lunch 11:00-14:00, dinner 17:00-22:00)
- Accept/decline orders based on value/distance
- Multiple platforms simultaneously ("multi-apping")
- Manage own fuel, maintenance, insurance

---

### Before Tasks (Employed)
- **Van check:** Lights, tyres, load secure (usually a pre-shift checklist in depot app)
- **Scan load:** All parcels scanned onto vehicle, manifest reviewed
- **Route optimisation:** Handheld device generates optimised delivery sequence
- **Signature requirement check:** Which parcels need ID, age verification, signature?
- **Special items:** Dangerous goods (batteries, aerosols), refrigerated items, high-value items

### Before Tasks (Gig)
- **Vehicle check:** Especially for cyclists/bikers -- brakes, lights, insulated bag condition
- **App status check:** Any promotions or boost zones active? Platform status ok?
- **Insurance validity:** Commercial hire & reward insurance required (often overlooked)

---

### After Tasks
- **Employed:** POD upload (automatic via scanning), failed delivery card left, redelivery scheduled, van return, fuel level checked
- **Gig:** Earnings review, mileage log (for tax deduction), review star ratings, manage any negative customer feedback

---

### Time-Sensitive Triggers

| Trigger | Threshold | Consequence |
|---|---|---|
| Driver's licence renewal | Every 10 years (varies) | Can't drive |
| Vehicle MOT/inspection | Annual | Illegal to drive |
| Vehicle insurance | Annual (gig: commercial H&R insurance) | Uninsured operation -- criminal |
| DBS/background check (employed) | Often annual or 2-yearly | Can't deliver certain goods |
| Age verification deliveries | Per-parcel (alcohol, knives, medication) | Personal criminal liability |
| Dangerous goods awareness cert | Required for some postal/courier | Can't carry DG |
| Food hygiene cert (gig food delivery) | Often required by platforms | Account suspension |
| Platform rating threshold | Ongoing (e.g., <4.6 stars on DoorDash) | Deactivation |
| Delivery SLA window | Per parcel (same-day, 1hr, next-day before 12:00) | Failed delivery, penalty |

---

### Stress / Anxiety Points
- **Gig: algorithm volatility:** Earnings drop without explanation. Algorithm changed. Income uncertainty is constant.
- **Gig: deactivation:** One bad week of ratings or a customer complaint can suspend your account -- no income, no appeal clarity
- **Gig: insurance grey zone:** Many drivers don't have proper commercial insurance. One accident = catastrophic personal liability.
- **Parking:** Urban couriers spend meaningful time circling for parking. Failed delivery attempts cost them.
- **Unsafe delivery locations:** Being asked to deliver to locations that feel unsafe
- **Weather:** Cyclists/bikers exposed to all weather -- no rain = less food delivery demand, rain = dangerous riding
- **Vehicle maintenance:** Gig drivers absorb all maintenance costs. Unexpected breakdown = no income.
- **Tax complexity:** Gig workers often underprepared for self-assessment tax, national insurance, VAT threshold

---

### Data Sources
- **Dispatch apps:** DHL On Demand Delivery, UPS ORION (employed), Uber Eats app, DoorDash Dasher app, Amazon Flex app
- **Vehicle telematics:** Employer-installed (employed); none typically for gig
- **Mileage tracking:** MileIQ, TripLog, Everlance -- for tax deduction purposes (gig)
- **Fuel cards:** Company-issued (employed); personal credit card + app tracking (gig)
- **Rating platforms:** Platform apps -- real-time feedback
- **Navigation:** Google Maps, Waze, Citymapper (urban)

---

### Proactive AI Opportunity

> **"Your Amazon Flex insurance is up for renewal in 11 days and you don't have commercial hire & reward cover -- your standard personal car insurance policy on file explicitly excludes delivery work. If you're in an accident while on a delivery without this, you're personally liable and uninsured. Here are three providers that cover Flex drivers: Zego (8.40/day), Hiscox (annual policy 680), Rideshur (per-mile). Want a quick comparison?"**

> **"It's been 14 months since your van's last service and you're at 28,400 miles -- your manufacturer schedule recommends service every 12 months or 25,000 miles, whichever comes first. You've missed both. With winter coming, this is worth booking now. Your usual garage has a slot Thursday 08:00 -- your route that day is shorter, should be back by 12:00."**

> **"You've had 3 'Item Not Delivered' customer claims in the last 10 days on DoorDash -- you're currently at 4.5 stars, one more complaint away from their review threshold. Two of the three were for the same restaurant (Burger King Streatham) -- the orders were consistently late leaving that location. I can flag this to DoorDash support as a restaurant-side issue rather than a driver issue, which may protect your rating."**

> **"Surge pricing just activated in the Shoreditch zone -- 1.8x multiplier for the next 45 minutes. Based on your current location you're 8 minutes away. That window will likely net you 2-3 orders at roughly 11-14 each vs. your current zone average of 6.50. Worth heading over?"**

> **"Your self-assessment tax return is due January 31st -- that's 23 days away. Based on your mileage logs and earnings data I've tracked, you earned 34,200 from gig platforms this tax year. Your allowable mileage deduction is 4,860 (8,100 miles @ 45p), and your insulated bag/equipment costs were 340. Estimated tax bill: 5,420. Want me to pre-populate a draft return?"**

---

## 7. Airline Pilots

### Daily/Weekly Rhythm
Airline pilots operate under some of the strictest regulatory frameworks in any profession -- EASA (Europe), FAA (US), CASA (Australia), SACAA (SA), etc. Flight Time Limitations (FTL) govern everything.

**Short-haul/narrowbody (e.g., Ryanair, Southwest):**
- Early starts (03:00-05:00 report times for 06:00 departures)
- 3-5 sectors per day
- Home base return possible most days, but not always
- Duty day typically 9-13 hours

**Long-haul/widebody (e.g., British Airways, Emirates, Singapore Airlines):**
- Typically 1 sector per day (or 2 for medium-haul long-haul like JNB-LHR-JNB)
- Augmented crew for ultra-long-haul (3-4 pilots rotating rest on bunk)
- Layovers of 24-48h in destination cities
- 10-14 day rosters with 10-14 days off

**Monthly limits (EASA FTL example):**
- Max 100 flight hours per 28 days
- Max 900 hours per calendar year
- Max 1,000 hours per 12 consecutive months
- Minimum rest: 12h between duties (can be reduced under certain conditions)

**Roster structure:**
- Bid system (senior pilots bid preferred schedules)
- Standby duties -- be available to fly with 1-2hr call-out notice
- Simulator recurrency every 6 months (mandatory)

---

### Before Tasks (Pre-Flight)
- **Report time:** Typically 60-90min before departure for short-haul, 90-120min for long-haul
- **Weather briefing:** NOTAMs (Notices to Airmen), SIGMET, METAR, TAF -- departure, destination, alternates. Especially: icing, turbulence, thunderstorm routing
- **ATIS:** Automatic Terminal Information Service -- current airport conditions
- **Fuel calculation:** Minimum fuel (trip fuel + contingency + alternate + final reserve + extra). Captain's discretion to uplift extra.
- **Flight plan review:** Route, levels, significant points, alternates -- filed by dispatch, reviewed by crew
- **ACARS review:** Any maintenance messages, MEL (Minimum Equipment List) deferred items on the aircraft
- **Aircraft technical log review:** What was wrong on last flight? Has it been rectified or deferred?
- **Walkaround (external pre-flight inspection):** Completed by first officer typically -- controls, tyres, engine intakes, fuel caps, airframe condition
- **Cockpit checks:** Standard Operating Procedures (SOPs) -- checklist-driven, non-negotiable
- **Passenger and cargo load:** Final loadsheet -- CG (centre of gravity) and total weight must be within limits
- **Slot time confirmation:** ATC departure slot -- must push back and depart within 5min window

---

### After Tasks (Post-Flight)
- **Technical log entry:** Any defects observed during flight -- squawks logged
- **Fuel used vs. planned:** Discrepancies worth noting
- **Flight time logging:** Personal logbook and company records
- **ACARS / EFB download:** Any performance data flagged
- **Debrief (if incident):** Near-miss, turbulence injury, tech issue -- verbal or written report
- **Rest period begins:** Officially from off-chocks/block-in time -- minimum rest applies immediately
- **Expense claims (layovers):** Hotel, meals, transport

---

### Time-Sensitive Triggers

| Trigger | Threshold | Consequence |
|---|---|---|
| ATPL/CPL medical certificate (Class 1) | Every 12 months (<40yr old), every 6 months (>40) | Licence invalid, grounded |
| OPC (Operator Proficiency Check) | Every 6 months | Grounded |
| Line check | Annual | Grounded |
| SEP (Safety & Emergency Procedures) | Annual | Grounded |
| Simulator recurrency | Every 6 months | Grounded |
| Type rating renewal | Ongoing via OPC/LPC | Grounded |
| Dangerous goods awareness | Biennial | Can't operate |
| Flight time limitations -- daily | 9-12h FDP depending on acclimatisation/sectors | Illegal to fly |
| Flight time limitations -- monthly | 100h per 28 days | Illegal to fly |
| CRM (Crew Resource Management) | Annual | Grounded |
| EFB (Electronic Flight Bag) currency | Per airline, typically annual | Can't use EFB |
| Visa requirements for route | Per destination country | Can't enter/depart |

---

### Stress / Anxiety Points
- **Medical events:** Any health concern -- blood pressure, cardiac, mental health -- can ground a pilot immediately. Career anxiety around medical renewals is pervasive.
- **Fatigue:** Night stops, early starts, disrupted circadian rhythm. Fatigue is the constant background condition.
- **Technical issues in flight:** Decision to divert or continue -- commercial pressure vs. safety.
- **Weather diversions:** Unplanned divert, crew out of rest hours, passengers angry, hotel rooms needed.
- **FTL approaching:** Crew approaching max duty hours mid-operation. Flight may have to cancel.
- **Go-around/missed approach:** Not dangerous, but the review process that follows adds stress.
- **Discretion usage:** Flying beyond normal FTL under commander's discretion -- used, but scrutinised.
- **Recurrency/simulator failure:** Failing an OPC is career-threatening. Simulator check pressure.
- **Roster instability:** Standby duties with no notice. Sleep disruption. Family life impact.

---

### Data Sources
- **EFB (Electronic Flight Bag):** Jeppesen, Navblue, Lido -- charts, NOTAMs, weather, flight plan on iPad/tablet
- **ACARS:** Aircraft Communications Addressing and Reporting System -- ATC comms, weather updates, loadsheet, tech log
- **OFP (Operational Flight Plan):** Generated by airline operations, includes fuel, route, alternates
- **Weather:** ATIS, SIGMET, METAR, TAF -- via EFB or airline weather service (WSI, AviationWeather.gov)
- **ATC:** Via radio (VHF), CPDLC (Controller Pilot Data Link Communications) for oceanic
- **Crew portal (company):** Roster, training records, medical status, pay, company notices
- **SITA/airline operations system:** AOC (Airline Operations Centre) for flight operations management
- **Personal logbook app:** LogTen Pro, ForeFlight -- tracking hours for currency

---

### Proactive AI Opportunity

> **"Your Class 1 medical is due for renewal on April 14th -- that's 34 days away. Your AME (Authorised Medical Examiner) at Heathrow Aviation Medicine has a slot on March 28th. Book now, before your April 3rd long-haul block starts. Missing the renewal date means your licence is technically invalid and you'd need chief pilot approval to delay any flights."**

> **"Your OPC (Operator Proficiency Check) is due in 6 weeks. Your simulator qualification is on the B787-9 at CAE Burgess Hill. Your rostered training date is May 12th, but you have 4 sectors scheduled May 10th-11th with a JNB overnight -- you'll arrive back Heathrow on the 12th at 07:30, and sim starts at 10:00. That's 2.5h rest before a proficiency check. Based on EASA FTL, this is technically legal but not ideal. Want me to flag it to your fleet manager to explore a date swap?"**

> **"NOTAMs for your BCN destination tonight include a NOTAM-U for ILS Runway 25L out of service until 23:59 -- your planned arrival is 22:40. You'll be on ILS 07R or visual approach to 25R. Weather at Barcelona is 8/8 overcast at 600ft -- marginal for visual. Suggest you review the approach plates for 07R and 25R before dispatch. I can pull them up now."**

> **"Your cumulative FDP (Flight Duty Period) this month is 87 hours against a 100h/28-day limit. You have 11 days left in the period and 4 duties rostered. Duty 3 (JFK rotation) is planned at 16h FDP -- that will take you to 103h. Either that duty needs crew augmentation or the roster needs adjustment. Your crew controller hasn't flagged this yet."**

> **"You're coming up on your 6-month CRM requirement -- last completed November 4th. There's a ground school CRM day running at Gatwick on April 8th with 4 open seats. That date falls in your leave block, so it won't eat into flying days. Want me to request enrolment through the crew portal?"**

---

## 8. Air Traffic Controllers

### Daily/Weekly Rhythm
ATCs manage the safe, orderly, and expeditious flow of aircraft in assigned airspace or at aerodromes. The work is mentally demanding, deadline-every-second work. Strict rest rules apply.

**Shift patterns:**
- ATCs work rotating shifts: early (06:00-14:00), day (10:00-18:00), late (14:00-22:00), night (22:00-06:00)
- Maximum continuous control time is **2 hours** in most jurisdictions before mandatory break
- Night shifts are typically quieter but fatigue risk is higher
- Typical week: 4-5 shifts with mandatory days off

**Working environment:**
- **Aerodrome control (Tower):** Manages aircraft on ground and in immediate airspace (typically within 5NM, below 3,000ft)
- **Approach control (TRACON/RAPCON):** Manages arrivals and departures in the approach environment (5-50NM)
- **Area/Enroute control (Centre/ACC):** Manages en-route traffic at high altitude over large areas

**Traffic load:** Major hub (Heathrow, JFK, Frankfurt) -- 1,200-1,500 movements per day. Controllers may manage 10-20 aircraft simultaneously at peak.

---

### Before Tasks (Pre-Position)
- **Briefing/handover:** Incoming controller briefs on all current traffic, active special procedures, weather, NOTAMs, SIDs/STARs in use
- **ATIS check:** Current weather, active runways, approach types in use
- **NOTAMs review:** Active airspace restrictions, equipment outages, military activity
- **Weather radar check:** Convective activity, low visibility procedures (LVP) status
- **Equipment status:** Check all comms and radar systems are functional. Any radar degradation changes separation standards.
- **Flow control status:** Any GDPs (Ground Delay Programmes) or MIT (Miles-In-Trail) restrictions in effect

---

### After Tasks (Post-Shift)
- **Handover:** Thorough traffic state brief to relieving controller
- **Incident reporting:** Any AIRPROX (Airborne Proximity Event), runway incursion, or unusual event must be reported same day
- **Operational log entries:** Significant events, equipment failures, traffic anomalies
- **Voice recording review:** If an incident occurred -- recordings preserved and reviewed
- **Rest period begins:** Minimum rest between shifts (ICAO/EASA/national rules vary -- typically 10-12h)

---

### Time-Sensitive Triggers

| Trigger | Threshold | Consequence |
|---|---|---|
| ATC licence validation | Annual (medical + competency) | Can't control |
| Unit endorsement revalidation | Annual or biennial (unit-specific) | Can't control at that position |
| English language proficiency | Every 3-6 years (ICAO Level 6: indefinite) | Licence invalid |
| Continuous control time | 2h maximum (most jurisdictions) | Mandatory break |
| Shift duration | Varies (8-10h max typically) | Fatigue violation |
| Medical certificate | Annual | Grounded |
| Emergency simulation exercise | Typically annual | Certification lapse |
| Transition training (new equipment) | On system upgrade | Can't use new system |

---

### Stress / Anxiety Points
- **Traffic complexity spikes:** Weather diversion causes 8 extra aircraft to enter a sector simultaneously. Mental workload peaks.
- **Equipment failure:** Primary radar goes down. Revert to procedural separation. Drastically reduced capacity.
- **Comms failure:** Pilot stops responding. Emergency protocol activated.
- **Runway incursion:** Vehicle or aircraft enters active runway without clearance. The most feared ground incident.
- **Loss of separation:** Two aircraft closer than required separation minima -- AIRPROX filing, investigation, career review.
- **Mental health/burnout:** The job's precision demands lead to chronic stress. Errors are career-defining.
- **Night fatigue:** Circadian trough at 03:00-05:00 on nights. Error risk highest.

---

### Data Sources
- **Radar systems:** Primary radar, SSR (Secondary Surveillance Radar), MLAT, ADS-B
- **FDPS (Flight Data Processing System):** Flight plan data, flight strips (electronic or paper)
- **ATIS:** Automated weather at aerodromes
- **SIGMET/METAR/TAF:** Weather products via AMAN (Arrival Manager) and DMAN (Departure Manager) systems
- **ACAS/TCAS:** Airborne collision avoidance -- controller aware when TCAS RA issued
- **Departure/arrival sequencing tools:** AMAN/DMAN systems at major airports
- **Coordination tools:** LoA (Letter of Agreement) between sectors/units
- **EUROCONTROL CFMU (EU):** Central flow management -- slot allocation, GDP notices

---

### Proactive AI Opportunity

> **"Your annual medical is due in 28 days. The CAA approved aeromedical centre in Gatwick has a 3-week wait -- you need to book today to ensure your certificate doesn't lapse before your Heathrow Tower endorsement revalidation on May 2nd. Missing the medical means your licence is invalid and you can't legally control."**

> **"Your English Language Proficiency (ELP) endorsement is currently rated at ICAO Level 5 with a 3-year renewal -- it expires September 14th. That's 54 days from now. The CAA renewal assessment requires a 2-week booking lead time. You have no leave booked in August -- I'd suggest securing a late August slot before summer leave bids close."**

> **"There's a SIGMET for severe turbulence (CAT) over FL310-390 in your sector for the next 4 hours -- 12 of your next 14 inbounds are at FL350-370. Expect significant pilot requests for altitude changes. AMAN is currently showing a 14-minute delay at Heathrow. A heads-up for your handover to the incoming controller."**

> **"EUROCONTROL has issued a GDP notice for your sector -- traffic flow reduction to 28 arrivals/hour from 14:00 due to the LVP now active at Heathrow. That affects 34 flights currently airborne. Slot delays ranging from 12 to 47 minutes are now in effect. Airline ops teams are starting to query. Your ATFM coordinator has the full list."**

> **"Your unit endorsement for the West Sector position is due for revalidation in 6 weeks. Per NATS training records, you haven't controlled on West Sector in 89 days -- the revalidation requires a minimum of 3 operational sessions within 90 days of assessment. You have one session scheduled. You need 2 more in the next 13 days to remain within the qualifying window. Check with the watch manager for availability."**

---

## 9. Maritime / Ship Officers

### Daily/Weekly Rhythm
Ship officers work on a **watchkeeping system** -- unlike shore-based roles, the ship never stops, and the sea doesn't care about working hours. Officers stand watches, manage cargo operations, maintain the vessel, and navigate -- sometimes simultaneously.

**Watch systems:**
- **4-on/8-off:** Traditional system -- 4 hours on bridge/engine room, 8 hours off (sleep, admin, maintenance)
- **6-on/6-off:** Often used on short-sea or during cargo operations
- **Continuous operations:** During port stays, cargo operations may run around the clock

**Typical voyage cycle:**
- **Day 1-2:** Departure. Intensive nav work -- port exit, coastal pilotage, traffic separation schemes
- **Day 3-10 (deep sea):** Ocean passage. Watch routines. Weather routing. Maintenance.
- **Day 10-12:** Approach, port entry, pilotage, mooring operations
- **Port stay:** Cargo operations (loading/discharging), bunkering, provisions, crew changes, inspections

**Officer roles:**
- **Master (Captain):** Overall command and legal responsibility. Does not normally stand a regular watch.
- **Chief Officer (First Mate):** Cargo operations, stability, deck maintenance, safety.
- **2nd Officer:** Navigation, charts, voyage planning, safety equipment.
- **3rd Officer:** Safety equipment (firefighting, lifesaving), bridge watch.
- **Chief Engineer:** Engine room overall responsibility.
- **2nd Engineer:** Day-to-day engine maintenance.

---

### Before Tasks (Pre-Voyage / Port Departure)
- **Voyage plan:** Full passage plan from berth to berth -- port entry/exit procedures, waypoints, tidal gates, weather routing, contingency ports. Reviewed and signed off by Master.
- **Chart correction:** Charts must be up to date -- NtM (Notices to Mariners) corrections applied
- **Weather briefing:** GFS/ECMWF model downloads, ship weather routing service advisory (Bon Voyage System, Weathernews), GMDSS weather alerts
- **Cargo check / stability calculation:** Loading computer updated -- GM (metacentric height) within safe limits, stress and bending moments within class limits, hazmat stowage verified
- **ISPS/Port State security check:** ISPS compliance, AIS transmitting, SSAS armed
- **Pre-departure checklist:** All watertight doors, navigation lights, steering gear test, communication test, emergency equipment checks
- **Pilot boarding arrangements:** Pilot ladder rigged correctly (SOLAS requirements for pilot ladder height, width, condition)
- **Bunkering records completed:** Fuel oil quantity, sulphur content, bunker delivery note filed
- **Drug & alcohol check:** Many operators require random testing before departure
- **MARPOL compliance check:** Garbage management plan reviewed, oily water separator operational, no illegal discharges

---

### After Tasks (Post-Voyage / Port Arrival)
- **Arrival report:** Port authority notification -- ETA, crew list, dangerous goods declaration, deratting certificate
- **Customs and immigration:** Crew passports checked, stores list submitted, health declaration
- **Deck log / Official log book entries:** All significant events during passage -- weather, position, any incidents
- **Voyage data recorder (VDR) maintenance check:** Black box data integrity confirmed
- **Port State Control (PSC) inspection prep:** Any known deficiencies must be corrected before PSC inspector boards
- **Cargo damage survey:** Any cargo claims -- pre- and post-loading surveys documented
- **Oil record book update:** All machinery space operations involving oil -- legally required per MARPOL
- **MLC (Maritime Labour Convention) compliance:** Crew rest hours recorded, no violations
- **Class and flag state reports:** Any structural or machinery defects notified

---

### Time-Sensitive Triggers

| Trigger | Threshold | Consequence |
|---|---|---|
| STCW medical certificate (ENG1/ML5) | Every 2 years | Can't sail |
| STCW certificate of competency | Revalidation every 5 years | Illegal to serve in that capacity |
| GMDSS certificate | 5-year revalidation | Can't operate comms equipment |
| Advanced Firefighting | 5-year refresher | Licence invalid |
| MARPOL -- ECA compliance | Entering ECA: must switch to <0.1% sulphur fuel within 1h | Port State fine |
| Drills (fire, abandon ship, man overboard) | Monthly or per SOLAS requirement | Safety deficiency |
| Dry dock / Special Survey | 5-year cycle (class survey) | Insurance invalid, flag state prohibition |
| Annual survey (class) | Annual | Class certificate lapses |
| ISM internal audit | Annual | DOC at risk |
| Dangerous goods IMDG compliance | Per-consignment | Port State detention |
| Port State Control inspection | Random (but high-risk ships targeted) | Detention |
| Visa/yellow fever/vaccination | Destination port requirements | Shore leave refused, crew change impossible |
| Seafarer discharge book | Continuous | Immigration refusal |
| Tidal window for port entry | Hours-specific (e.g., Rotterdam Europort tidal gates) | Miss the tide, wait 12h |

---

### Stress / Anxiety Points
- **Port State Control detention:** PSC inspector finds 10 deficiencies. Ship detained until all fixed. Demurrage running. Owner furious. Chief Officer responsible for safety deficiencies.
- **Heavy weather:** Forecast shows Force 10 gale on the crossing. Cargo shifting risk. Crew safety. Do you slow down, alter route, or push through?
- **Piracy risk zones:** HRA (High Risk Area) -- Indian Ocean, Gulf of Guinea. Armed guards, citadel drill, razor wire, speed up.
- **Class survey overdue:** Annual survey missed. Insurance may be voided. Ship technically uninspectable.
- **Crew change difficulty:** COVID-era but still relevant -- crew stuck on board beyond contract end. Mental health deteriorates. STCW violations accumulate.
- **Bunker shortage:** Unexpected consumption. Not enough fuel to reach next bunker port. Re-routing required.
- **Cargo claim:** Large cargo damage claim. Evidence gathering under time pressure. Expert surveyors needed.
- **Near collision:** Close-quarters situation with another vessel. COLREG compliance review. Near miss report.

---

### Data Sources
- **ECDIS (Electronic Chart Display):** Furuno, JRC, Transas -- digital navigation charts
- **AIS/RADAR:** Traffic monitoring, collision avoidance
- **GMDSS (Global Maritime Distress and Safety System):** Weather, distress comms, Navtex
- **Ship weather routing services:** Bon Voyage System (BVS), Weathernews, StormGeo -- optimised routing
- **Loading computer:** NAPA, Loadmaster -- stability, stress calculations
- **Port authority portals:** PORTNET (Rotterdam), Maritime NZ, Port Community Systems (Portbase etc.)
- **Class society portals:** Lloyd's Register, DNV, Bureau Veritas -- survey status, deficiency tracking
- **LRIT (Long Range Identification and Tracking):** Flag state mandated position reporting
- **Crew management software:** COMPAS, COMPASS (BASS), Crewing Manager -- certificates, rest hours, contracts
- **MARPOL logs:** Oil Record Book, Garbage Record Book, Cargo Record Book (chemicals)

---

### Proactive AI Opportunity

> **"Chief Officer Chen -- the ship's class annual survey is due in 14 days. The DNV surveyor roster shows availability at the Port of Rotterdam on your scheduled arrival day (March 28th). However, your aft mooring winch brake test and the emergency fire pump annual test are both outstanding -- these are standard items that will be inspected. Book the surveyor now and I'll generate a pre-survey deficiency closure checklist so nothing fails on the day."**

> **"You're 8 hours from the North Sea Emission Control Area (SECA). Current MDO (Marine Diesel Oil) stock is 42MT -- your SECA transit at current consumption will require approximately 38MT. You're fine on quantity, but the ECR needs to log the switchover with position, time, and fuel changeover sequence. The MARPOL Oil Record Book entry needs to be made before entering the ECA. Do you want me to pre-fill the entry for Chief Engineer sign-off?"**

> **"2nd Officer Patel -- your GMDSS General Operator's Certificate expires July 3rd. Revalidation requires a 1-day refresher course followed by a CAA/MCA oral exam. Courses are available at Warsash Maritime Academy in May (3 available dates) and at Fleetwood Nautical Campus in June. Your contract ends June 15th and the June course falls within your scheduled leave. May is the window."**

> **"Tidal gate for the Maas entrance to Rotterdam opens at 07:20 tomorrow. Based on current speed and position, you'll arrive at the pilot station at 07:05 -- that's tight with the 45-minute pilot boarding allowance. If you increase speed by 0.4 knots now, you'll arrive at 06:30, comfortably ahead of the tide. Fuel cost differential: approximately 1.2MT. Against port demurrage at 8,500/hour, the call is straightforward. Should I update the passage plan?"**

> **"AB Rodriguez and Oiler Kim have both reached 11 months at sea -- their contracts expire in 28 days. Under MLC 2006, maximum continuous service is 12 months. The next crew change port is Antwerp on April 4th. Crewing agency needs a minimum of 3 weeks notice for replacement seafarers. If you don't initiate the crew change request today, you risk an MLC violation that will show as a deficiency at any Port State Control inspection. Want me to send the crew change request to the manning agent now?"**

---

## Cross-Role Patterns for Pulse

### Universal Proactive Trigger Categories
Across all 9 roles, the same categories of proactive opportunity appear:

1. **Certification/Licence expiry** -- Every role has licences, certificates, or medicals that expire on fixed schedules. The window between "you need to act" and "expiry" is always known, the renewal lead time is always known, and the consequences of missing are always severe. This is the highest-value proactive category.

2. **Time/Hours of Service limits** -- Real-time awareness of accumulated hours (driving, flight time, control time, sea service) enables proactive flagging before limits become violations.

3. **Document completeness for upcoming events** -- Before a vessel departs, a flight operates, or a customs entry is filed, there is always a checklist of documents. Gaps in that checklist can be detected in advance.

4. **Asset health/maintenance** -- Vehicles, aircraft, vessels, and equipment all have scheduled and condition-based maintenance intervals. Upcoming intervals can be surfaced proactively, especially when the asset is unavailable for a window.

5. **Regulatory change** -- Tariff changes, ECA zone expansions, HOS rule updates -- proactive monitoring of regulatory feeds and notifying affected operators before the change bites.

6. **Cascading delay prediction** -- Vessel missing its berth, aircraft diverting, truck running late -- the downstream impact can be calculated and communicated proactively rather than reactively.

7. **Weather windows** -- For maritime, aviation, and road transport, weather forecasts allow proactive routing and timing decisions hours before the weather arrives.

8. **Financial optimisation** -- Fuel prices, tariff exclusion windows, crew change timing, rate expiry -- there are money-saving moments in every role that pass unnoticed.

---

## Implementation Notes for Pulse

### Data Integration Priority
| Integration | Roles Served | Value |
|---|---|---|
| Government licence/medical databases | All | Critical |
| Fleet telematics APIs | Truck, Fleet, Courier | High |
| Customs portal APIs | Forwarder, Coordinator | High |
| Weather APIs (aviation + maritime) | Pilot, ATC, Maritime | High |
| TMS/WMS webhooks | Coordinator, Warehouse | High |
| Class society survey portals | Maritime | Medium-High |
| ELD/tachograph data | Truck, Fleet | High |
| Load board APIs | Truck, Courier | Medium |

### Notification Timing Principles
- **Licence/cert expiry:** First alert at 90 days, second at 30 days, urgent at 14 days, critical at 7 days
- **HOS/FTL limits:** Alert when 75% consumed for shift, 80% for weekly/monthly limits
- **Document completeness:** Alert 48h before cut-off, re-alert 24h, urgent 6h
- **Weather impact:** Alert when significant weather is 24h+ out and routing decisions are still reversible
- **Regulatory changes:** Alert 30 days before effective date

### Trust & Tone Calibration per Role
- **Truck drivers:** Practical, no-nonsense, time is money. Short messages. Actionable.
- **Logistics coordinators:** More detail, trade-off analysis, draft communications ready to go.
- **Warehouse managers:** Operational focus, staff/volume context, linked to WMS data.
- **Freight forwarders:** Regulatory precision, document-level specificity, financial impact quantified.
- **Fleet managers:** Dashboard-style, multiple vehicles in one view, cost-impact framing.
- **Couriers (gig):** Mobile-first, earnings-focused, immediate actions.
- **Airline pilots:** High precision, ICAO/regulatory framing, safety language, calendar-first.
- **ATCs:** Safety language, procedural framing, fatigue-aware, never overwhelming.
- **Ship officers:** Document-heavy, MARPOL/STCW/ISM regulatory framing, voyage-timeline anchored.

---

*Research compiled: 2026-03-17 | Version: 1.0 | Purpose: Pulse Product Development*
