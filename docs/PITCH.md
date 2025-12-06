# Cosilico Pitch

## One-Liner

**The infrastructure layer for policy-aware AI.** Calculate taxes and benefits. Predict household attributes. Simulate policy impacts. One API.

---

## The Problem

Every AI assistant will need to answer questions about money and government:

- "Can I afford this house?"
- "What benefits am I eligible for?"
- "How would this tax change affect me?"

**Today, AI hallucinates these answers.** LLMs guess at tax brackets, make up eligibility rules, and can't cite sources. This is fine for casual queries. It's unacceptable for financial decisions.

The companies building AI assistants, fintech apps, and benefits platforms need reliable infrastructure. They need calculations they can trust, predictions they can explain, and citations they can show users.

**That infrastructure doesn't exist.** Tax software is consumer-facing (TurboTax). Microsimulation tools are academic. There's no API designed for AI systems that need accurate, auditable policy calculations.

---

## The Solution

Cosilico is the **Stripe for policy calculations** - infrastructure that developers integrate, not software that end-users see.

### Three Capabilities, One API

```python
from cosilico import predict

result = predict(
    person={"age": 35, "income": 45000, "state": "CA", "has_children": True},
    variables=["eitc", "childcare_expense", "snap_eligible"]
)

# {
#   "eitc": {"value": 3200, "type": "calculated", "citation": "26 USC § 32"},
#   "childcare_expense": {"value": 8500, "type": "predicted", "confidence": 0.82},
#   "snap_eligible": {"value": true, "type": "calculated", "citation": "7 USC § 2014"}
# }
```

| Capability | What it does | How it works |
|------------|--------------|--------------|
| **Calculate** | Deterministic tax/benefit calculations | Rules engine compiled from statute |
| **Predict** | Statistical estimates for unobserved attributes | ML models trained on enhanced microdata |
| **Simulate** | Population-scale policy modeling | Microsimulation across 100M+ households |

**The key insight:** Users don't care whether a value is calculated or predicted. They just want the answer. We handle the complexity internally and return structured results with appropriate metadata (citations for calculations, confidence for predictions).

---

## Market Opportunity

### Total Addressable Market (with sources)

| Segment | 2024 | 2030-34 | CAGR | Source |
|---------|------|---------|------|--------|
| **Tax Tech (Global)** | $18.5B | $36.7B | 12.1% | [MarketsandMarkets](https://www.marketsandmarkets.com/Market-Reports/tax-tech-market-28373824.html) |
| **Corporate Tax Software** | $12.9B | $24.1B | 8.9% | [Verified Market Research](https://www.verifiedmarketresearch.com/product/corporate-tax-software-market/) |
| Benefits Administration | $2.5B | $4B | 10.6% | [Verified Market Research](https://www.verifiedmarketresearch.com/product/employee-benefits-administration-software-market/) |
| Data Enrichment | $2.4B | $4.6B | 10.1% | [Grand View Research](https://www.grandviewresearch.com/industry-analysis/data-enrichment-solutions-market-report) |
| AI Infrastructure | $46B | $356B | 29.1% | [Fortune Business Insights](https://www.fortunebusinessinsights.com/ai-infrastructure-market-110456) |

**TAM: $100B+** across verticals that need policy-aware calculations.

### Corporate Tax Opportunity

Corporate tax software is a $12.9B market growing to $24.1B by 2030. Large enterprises represent 52.87% of revenue. Key trends:
- Cloud solutions: 61% market share, 14.82% CAGR
- API-based integration with ERP systems accelerating
- North America: 35-40% of global market

### International Expansion Opportunity

Global tax compliance is exploding due to cross-border commerce:
- B2B cross-border payments: $31.6T (2024) → $50T (2032)
- 45% of jurisdictions expect tax complexity to increase (TMF Group 2024)
- EU digital tax policies driving demand for multi-jurisdictional platforms

**Cosilico's international advantage:**
- PolicyEngine already covers US, UK, Canada (half-built)
- AI-assisted rule encoding enables rapid expansion to new countries
- Open source contributors worldwide can accelerate coverage

### Comparable Company Valuations

| Company | What They Built | Valuation / Exit | Relevance |
|---------|-----------------|------------------|-----------|
| **Avalara** | Sales tax API | $8.4B acquisition (2022) | Proves tax calculation APIs can be massive |
| **Plaid** | Financial data API | $6.1B ($390M ARR, 16x multiple) | API infrastructure for fintech |
| **Gusto** | Payroll + benefits | $9.3B (2025) | Benefits eligibility is core to their platform |
| **Rippling** | HR platform | $11.5B (2024) | Multi-country tax calculations needed |
| **Intuit** | TurboTax, QuickBooks | $16.3B revenue (2024) | No public tax calculation API |

### Why AI Can't Solve This Alone

Stanford research on GPT-4 tax accuracy ([source](https://arxiv.org/)):
- **67% accuracy** on tax true/false questions
- Only **76 of 98 scenarios** within 10% of correct tax liability
- LLMs will always need to call deterministic calculation tools

TurboTax doesn't offer a public API. There's no infrastructure layer for AI-native tax/benefits apps.

### Why Now

1. **AI Tool Use is Standard** — Function calling shipped in GPT-4 (2023), Claude 3 (2024). MCP protocol now adopted by Microsoft.
2. **Fintech Consolidation** — Avalara ($8.4B), Clearbit (HubSpot), Credit Karma ($8.1B by Intuit). Acquirers paying premium for tax/financial data.
3. **Regulation Coming** — SEC, CFPB examining AI in financial services. Audit trails will be required.
4. **Open Source AI Maturing** — a16z, OSS Capital, Index all increasing open source investments. Open infrastructure is the new standard.

---

## Business Model

### Open Source Core, Paid Services

```
FREE (Open Source)
├── Rules engine, DSL, compiler
├── Imputation algorithms (microimpute, microcalibrate)
├── Enhanced public microdata (ECPS)
└── Self-host everything if you want

PAID
├── Hosted API (we run it for you)
├── Support + SLA
├── Custom model training
├── Enterprise data enrichment
```

**We don't lock in customers with proprietary algorithms.** Revenue comes from convenience, freshness, and scale - not gatekeeping.

### Revenue Streams

#### 1. API Usage (SMB + Startups)
- Per-prediction pricing: $0.001 - $0.01 per call
- Monthly plans with included volume
- Self-serve signup, usage-based billing

#### 2. Enterprise Data Enrichment (Large B2B)
- Customer data enrichment: predict 200+ attributes per record
- Per-record pricing: $0.10 - $1.00 depending on attributes
- Or annual license for self-hosted deployment
- Support + model update subscription

**Example deal:** Grocery chain with 10M customers
- $0.50/record enrichment = $5M
- $500K/year for updates + support
- Total: $5.5M year 1, $500K+ recurring

#### 3. Enterprise Platform (Large Companies)
- Unlimited API access
- SLA guarantees (99.9% uptime, <100ms latency)
- Custom jurisdiction modules
- Dedicated support
- $100K - $1M+ annually

#### 4. Microsimulation Compute (Government + Research)
- Population-scale policy modeling
- Cloud compute for 100M+ household simulations
- Per-simulation pricing or subscription
- $50K - $500K per engagement

---

## Revenue Projections

### Conservative Path

| Year | ARR | Customers | Key Milestones |
|------|-----|-----------|----------------|
| 1 | $500K | 5-10 design partners | Product-market fit, first enterprise deal |
| 2 | $3M | 50+ paying customers | Self-serve launch, 2-3 enterprise deals |
| 3 | $10M | 200+ customers | Enterprise sales team, international expansion |
| 4 | $30M | 500+ customers | Platform status, AI lab partnerships |
| 5 | $75M | 1000+ customers | Category leader |

### Aggressive Path (Unicorn)

| Year | ARR | Valuation | Key Milestones |
|------|-----|-----------|----------------|
| 1 | $1M | $10M (seed) | 10 design partners, prove accuracy |
| 2 | $5M | $50M (Series A) | 100 customers, first $1M+ deal |
| 3 | $20M | $200M (Series B) | Enterprise traction, 10+ countries |
| 4 | $60M | $500M | AI lab integrations, category definition |
| 5 | $150M | $1B+ | Standard infrastructure for policy-aware AI |

**Path to unicorn:** $150M+ ARR at 7-10x multiple = $1B+ valuation

---

## Customer Segments

### Tier 1: Design Partners (Year 1)

| Type | Example Companies | What They Need |
|------|-------------------|----------------|
| AI-native fintech | Ramp, Brex, Mercury | Tax calculations for expense categorization |
| Benefits platforms | Beam, Justworks, Rippling | Eligibility determination |
| Financial planning AI | Monarch, Copilot | Tax projections, scenario modeling |
| Benefits navigators | Propel, SingleStop | Multi-program eligibility |

**Goal:** 5-10 design partners who co-develop with us, become case studies.

### Tier 2: Growth Customers (Year 2-3)

| Type | Example Companies | Deal Size |
|------|-------------------|-----------|
| Neobanks | Chime, Current, Dave | $100K - $500K |
| Payroll | Gusto, Deel, Remote | $200K - $1M |
| Insurance | Lemonade, Oscar | $100K - $500K |
| Tax prep | Column Tax, April | $200K - $1M |

### Tier 3: Enterprise (Year 3+)

| Type | Example Companies | Deal Size |
|------|-------------------|-----------|
| Large retailers | Walmart, Target, Kroger | $1M - $10M |
| Major banks | Chase, BofA, Wells Fargo | $1M - $5M |
| HR platforms | Workday, ADP, Paychex | $500K - $5M |
| Government | IRS, SSA, State agencies | $500K - $10M |

### Tier 4: Strategic (Year 4+)

| Type | Example Companies | Structure |
|------|-------------------|-----------|
| AI Labs | Anthropic, OpenAI, Google | Partnership / integration deal |
| Cloud providers | AWS, GCP, Azure | Marketplace listing |

---

## Competitive Landscape

### Why Not Existing Solutions?

| Alternative | What They Do | Limitation |
|-------------|--------------|------------|
| **Column Tax** | Embedded tax *filing* API for fintechs | Filing only, not calculation-as-a-service. No benefits. |
| **Symmetry Software** | Payroll tax engine (gross-to-net) | Payroll taxes only, not income tax or benefits |
| **Benefit Kitchen** | Benefits eligibility screening (18 programs, 8 states) | No tax calculations, limited state coverage |
| **TurboTax/H&R Block** | Consumer tax filing | No API, not designed for AI integration |
| **Avalara/TaxJar** | Sales tax APIs | Sales tax only, not income tax or benefits |
| **Academic microsims (TAXSIM)** | Research tax models | Not API-first, limited support, slow |

### Detailed Competitive Analysis

| Capability | Column Tax | Symmetry | Benefit Kitchen | Cosilico |
|------------|------------|----------|-----------------|----------|
| Income tax calculation | ✅ (for filing) | ❌ | ❌ | ✅ |
| Income tax filing | ✅ | ❌ | ❌ | ❌ |
| Payroll tax (FICA, etc.) | ❌ | ✅ | ❌ | ✅ |
| Benefits eligibility | ❌ | ❌ | ✅ (limited) | ✅ |
| 50-state coverage | ✅ | ✅ | ❌ (8 states) | ✅ |
| Attribute prediction | ❌ | ❌ | ❌ | ✅ |
| Microsimulation | ❌ | ❌ | ❌ | ✅ |
| Open source | ❌ | ❌ | ❌ | ✅ |

**Key insight from Column Tax's blog:** "Today's LLMs cannot 'do taxes' on their own because tax calculations require 100% correctness. Today's models hallucinate." — This validates our core thesis.

**Note on payroll providers:** Rippling, Gusto, ADP all build payroll tax calculations in-house. They're potential customers for benefits eligibility + income tax projections, not competitors.

### Our Moats

1. **Microdata** - Enhanced CPS, synthetic populations, calibrated survey data. Hard to recreate.

2. **Coverage** - Federal + 50 states + benefits programs. Expensive to build, ongoing maintenance.

3. **Validation** - Test suites against IRS examples, edge cases, real-world scenarios. Trust is earned.

4. **Freshness** - Parameters updated when law changes. Ongoing investment competitors won't make.

5. **AI-Native Design** - Built for function calling, structured outputs, citations. Not retrofitted.

6. **AI Encoding Infrastructure** - PolicyEngine + TAXSIM serve as verification oracles for AI agents that learn to encode rules from statute. This is TDD at scale: generate unlimited test cases from oracles, let AI iterate until passing. The training data factory is the moat, not the encoded rules. See [AI_ENCODING.md](./AI_ENCODING.md).

---

## Team

### Max Ghenis - Founder & CEO

- Founded PolicyEngine (2021), used by governments and researchers worldwide
- Built microsimulation models for US, UK, Canada
- Background: Google, Uber (data science)
- MIT economics

### [Additional team TBD]

Hiring for:
- Founding engineer (systems / infrastructure)
- Founding engineer (ML / data)
- First sales hire (enterprise)

---

## Traction

### PolicyEngine Foundation

- **1M+ simulations** run on PolicyEngine platform
- **Used by:** UK government, US Congress (JCT), state legislatures
- **Coverage:** US federal + 50 states, UK, Canada
- **Community:** 50+ open source contributors

### Technical Validation

- Validated against IRS examples, academic benchmarks
- Sub-100ms latency for household calculations
- Census-scale microsimulation (100M+ households)

### Relationships

- Funders: [foundations supporting PolicyEngine]
- Government users: [agencies using PE for analysis]
- Research partners: [universities, think tanks]

---

## The Ask

### Seed Round: $3-5M

**Use of funds:**

| Category | Allocation | Purpose |
|----------|------------|---------|
| Engineering | 50% | Core platform, API, infrastructure |
| Data/ML | 25% | Prediction models, microdata enhancement |
| Go-to-market | 15% | First sales hire, design partner acquisition |
| Operations | 10% | Legal, finance, ops |

**Milestones to Series A:**
- 10+ paying customers
- $1M+ ARR
- 1-2 enterprise deals ($500K+)
- Proven accuracy at scale

### What We're Looking For

- Lead investor who understands infrastructure / API businesses
- Intros to fintech, AI companies as design partners
- Expertise in enterprise sales motion

---

## Why This Wins

1. **Timing:** AI adoption creates massive demand for reliable policy tools
2. **Team:** Built the leading open source microsimulation platform
3. **Moat:** Data + coverage + validation compound over time
4. **Model:** Open source builds trust, paid services capture value
5. **Vision:** Every AI agent needs Cosilico - we become the standard

---

## Appendix

### Technical Architecture

See [DESIGN.md](./DESIGN.md) for detailed technical architecture:
- Rules engine with legal citations
- Multi-target compilation (Python, JS, SQL)
- Bi-temporal parameters (effective date + vintage)
- Filesystem-first for AI agent workflows

### Data Philosophy

**Default: Open**
- All algorithms open source (Apache 2.0)
- All public data published freely
- Synthesis where raw data can't be shared

**Exception: External constraints only**
- Vendor agreements prohibiting redistribution
- PII/privacy requirements
- We push toward openness, invest in synthesis
- Paid tier bridges gaps where openness isn't legally possible

### Comparable Exits (Updated 2025)

| Company | What They Built | Valuation | ARR Multiple |
|---------|-----------------|-----------|--------------|
| Avalara | Sales tax API | $8.4B (acquired 2022) | ~10x |
| Plaid | Financial data API | $6.1B (2025) | ~16x |
| Gusto | Payroll + benefits | $9.3B (2025) | ~15x |
| Rippling | HR platform | $11.5B (2024) | ~20x |
| Stripe | Payments infrastructure | $50B+ | ~15x |

API infrastructure companies command premium valuations (15-20x ARR) due to high retention, usage-based growth, and switching costs.

### Target Investors

**Tier 1: Thesis Alignment**

| Firm | Focus | Portfolio | Why Cosilico |
|------|-------|-----------|--------------|
| **OSS Capital** | Commercial open source | GitLab, Elastic ($300B+ value) | Our open-source-first model is exactly their thesis |
| **Ribbit Capital** | Fintech | Robinhood, Coinbase, Affirm ($12B AUM) | Infrastructure for their portfolio companies |
| **QED Investors** | Fintech infrastructure | Credit Karma, Nubank, Klarna | "Picks and shovels" thesis |

**Tier 2: AI + Infrastructure**

| Firm | Focus | Portfolio | Why Cosilico |
|------|-------|-----------|--------------|
| **a16z Infrastructure** | AI infrastructure | Fivetran, dbt, ElevenLabs ($1.25B fund) | AI tools for policy calculations |
| **General Catalyst** | Applied AI + fintech | $30B AUM, raised $8B in 2024 | Government + fintech angle |
| **Index Ventures** | Fintech + open source | Revolut, Robinhood, Figma | Spans both verticals |

**Tier 3: Seed Specialists**

| Firm | Focus | Portfolio | Why Cosilico |
|------|-------|-----------|--------------|
| **First Round Capital** | Seed + enterprise | 545 companies, $3.8M avg seed | Enterprise + fintech + AI clusters |
| **Obvious Ventures** | World positive | Beyond Meat, Diamond Foundry | Policy simulation enables better governance |

### Anticipated Objections

| Objection | Response |
|-----------|----------|
| "AI will get better at tax" | Stanford: GPT-4 only 67% accurate on tax T/F. Deterministic calculations need tools, not guesses. |
| "TurboTax will crush you" | They don't have a public API. Consumer-facing, not infrastructure. |
| "Is open source viable?" | MongoDB $1.7B ARR, GitLab $600M ARR, all built on open core. |
| "Can you execute?" | PolicyEngine: 1M+ simulations, UK government, US Congress users. Already built. |
| "Single founder risk" | Actively hiring co-founders. 50+ OSS contributors as extended team. |

Cosilico is infrastructure for the next layer: policy calculations, predictions, and simulation.

---

## Appendix B: Flagship Apps

Cosilico invests in (but doesn't operate) open source applications that demonstrate platform value. These are separate entities with independent teams, using Cosilico APIs like any other customer.

### FinSim — Personal Financial Planning

**Thesis:** Consumer financial planning apps are stuck in the 1990s. Maxifi (ESPlanner successor) charges $109-199/year for lifetime consumption smoothing, but runs on legacy architecture and offers no API. Mint died. The market is ripe for a modern, open source alternative.

**What it does:**
- Lifetime tax projections with consumption smoothing
- Social Security optimization (when to claim)
- Tax-efficient withdrawal strategies (Roth conversion ladders, etc.)
- Scenario comparison (move states, change jobs, have kids)

**Why it matters for Cosilico:**
- Proves the Rules API works for real financial planning at consumer scale
- Demonstrates accuracy vs. established competitors (Maxifi)
- Generates revenue as a Cosilico customer (API fees)
- Creates case study: "FinSim built a $X business on our API"

**Competitive landscape:**

| App | Pricing | Tech | API |
|-----|---------|------|-----|
| Maxifi (ESPlanner) | $109-199/yr | Legacy desktop-era | None |
| NewRetirement | $120-250/yr | Web, closed source | None |
| Boldin | $120/yr | Web, closed source | None |
| **FinSim** | Freemium | Modern web, open source | Cosilico |

**Relationship to Cosilico:** Portfolio investment. Max advises, separate team operates. Uses Cosilico APIs at standard pricing.

### HiveSight — LLM Perspective Simulation

**Thesis:** Pollsters, researchers, and product teams need to understand how different demographics think. Traditional surveys are slow and expensive. LLMs can simulate perspectives, but only if grounded in accurate demographic data.

**What it does:**
- "How would a median-income family in Ohio view this policy?"
- Synthetic focus groups with demographically-realistic participants
- Survey simulation at 1000x the speed and 1/100th the cost
- Grounded in actual population distributions, not LLM stereotypes

**Why it matters for Cosilico:**
- Proves the Data API (enhanced microdata) has value beyond tax calculations
- Opens entirely new market (research, polling, product testing)
- Demonstrates Cosilico's mission: "simulate society"

**Relationship to Cosilico:** Portfolio investment. Uses Cosilico's enhanced microdata API.
