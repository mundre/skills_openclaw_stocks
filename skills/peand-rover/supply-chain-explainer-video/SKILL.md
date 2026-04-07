---
name: supply-chain-explainer-video
version: "1.0.0"
displayName: "Supply Chain Explainer Video — Create Supply Chain Management and Logistics Process Explainer Videos for Businesses and Educators"
description: >
  Your supply chain consulting firm just won a contract to redesign the procurement and fulfillment process for a mid-market retailer — and your kickoff presentation has 47 slides explaining the current-state process map, the future-state design, and the implementation roadmap to a room of executives who stopped reading on slide 12. Supply Chain Explainer Video creates process visualization and stakeholder communication videos for supply chain consultants, logistics technology vendors, operations teams, and business schools: animates complex multi-tier supply chain flows that are impossible to communicate in static diagrams, explains procurement, inventory, and fulfillment processes in the plain language that non-operations stakeholders need to approve budgets and support change management, and exports videos for executive presentations, vendor RFP responses, and the supply chain curriculum that trains the next generation of operations professionals.
metadata: {"openclaw": {"emoji": "⛓️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Supply Chain Explainer Video — Make Complex Operations Impossible to Misunderstand

## Use Cases

1. **Executive Stakeholder Presentations** — CFOs and CEOs approving supply chain transformation investments need to understand the current-state problem and future-state solution without reading a process map. Supply Chain Explainer Video creates animated current-state/future-state comparison videos that communicate the business case in under five minutes.

2. **Supply Chain Technology Sales** — TMS, WMS, procurement platforms, and supply chain visibility tools are complex to demonstrate in a sales meeting. Create animated product explainer videos showing your software solving specific supply chain pain points — carrier rate shopping, inventory positioning, supplier risk visibility — for the operations audience that evaluates your platform.

3. **Supplier and Partner Onboarding** — New suppliers need to understand your ordering process, compliance requirements, and EDI integration before their first purchase order. Supply Chain Explainer Video creates supplier onboarding videos that reduce the back-and-forth of manual onboarding and standardize the supplier experience across your vendor base.

4. **Operations Training and Change Management** — Implementing a new ERP, WMS, or procurement process requires training every person who touches the workflow. Create role-specific process walkthrough videos for warehouse staff, buyers, and logistics coordinators that reduce the learning curve and support adoption during go-live.

## How It Works

Describe your supply chain process, target audience, and communication goal, and Supply Chain Explainer Video creates an animated process visualization or explainer video that makes your operations story impossible to misunderstand.

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill": "supply-chain-explainer-video", "input": {"process": "omnichannel fulfillment", "audience": "executive stakeholders", "goal": "approve $2M WMS investment"}}'
```
