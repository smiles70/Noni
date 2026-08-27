# PRICING-001: Deep research and force-ranked pricing recommendation

**Process:** v9.51  
**Intake:** `.ai/intake/2026-08-27-pricing-research-001.md`  
**Sources:** all external, published, and verifiable via DOI / official report / peer-reviewed journal / market leader public pricing pages.

---

## 1. Evidence summary

### 1.1 Older-adult willingness to pay

| Source | Finding | Relevance |
|--------|---------|-----------|
| **AARP, 2025 Tech Trends and Adults 50-Plus** | 60% of older adults are not willing to pay a fee for digital services they currently get free; 71% like the idea of a tech-support service but expect it to be bundled with the product purchase; 2 in 5 held off a tech purchase in 2024 due to finances. | Strong evidence for a generous free tier and against treating pricing as a core revenue gate. |
| **Yamauchi et al., Interactive Journal of Medical Research (i-JMR), 2017** (DOI: 10.2196/ijmr.7139) | Median WTP for an elderly telecare service in Japan was ~431 JPY / **US$3.70 per month** (contingent valuation method, n=305). | Anchor for a very low monthly ceiling if any recurring model is considered. |
| **Yuan et al., Risk Management and Healthcare Policy, 2024** (DOI: 10.2147/RMHP.S393767) | 30.5% "less unwilling" + 39.7% "not willing" to pay for digital health tech among urban elderly (n=639); WTP correlated with income, exercise, and health history. | Confirms the segment is not automatically willing to pay; pricing must match value and means. |
| **Mahoney et al. / Schulz et al. (cited in Caregivers' WTP study)** | Cost is a key limiting factor for technology adoption by older adults and their caregivers. | Justifies caregiver/gift payer as a separate, higher-WTP persona. |
| **Tang et al., Journal of Medical Internet Research, 2024** (DOI: 10.2196/50205) | Older US adults (55+) less willing to use telemedicine than younger adults; age 65+ OR 0.33. | Age itself reduces conversion; onboarding and pricing must be lower-pressure. |

### 1.2 Caregiver / proxy payer willingness

| Source | Finding | Relevance |
|--------|---------|-----------|
| **Wang et al., The Gerontologist, 2016** (DOI: 10.1093/geront/gnv033) | Caregivers of older adults were willing to pay a mean of **~$50/month for monitoring** and **~$70/month for monitoring + assistance** technologies. | Caregivers are a higher-WTP, emotionally motivated payer segment. |
| **AARP / Senior Planet** | In-person tech help costs **$20–$100 per hour** if not from family; free classes are the norm. | A paid product competes with "free help from a grandchild" and low-cost community classes. |

### 1.3 Comparable product pricing

| Product | Model | Entry monthly | Annual equivalent | Notes |
|---------|-------|---------------|-------------------|-------|
| **Duolingo Super** | Freemium subscription | $13.99/mo | $7.99/mo (annual $95.99) | Free habit first, pay to remove friction. |
| **Duolingo Max** | AI tier | $29.99/mo | ~$14/mo (annual $167.99) | Higher tier for AI features — relevant to Mynaani's Claude module. |
| **Lumosity** | Freemium subscription | $11.99/mo | $5.00/mo (annual $59.99) | Brain training with daily free games. |
| **Babbel** | Subscription | $14.95/mo | $6.95/mo (annual $83.40) | No free tier; lower annual. |
| **AARP Foundation Digital Skills Ready@50+** | Free (Google.org grant) | $0 | $0 | Sets a "free is expected" reference for basic digital skills. |
| **AARP membership** | Annual membership | $1.25/mo | $15/yr | An anchor for what older adults already pay for a trusted organization. |

### 1.4 Edtech / consumer SaaS pricing research

| Source | Finding | Relevance |
|--------|---------|-----------|
| **Toolradar, 2026 B2B SaaS Pricing Benchmarks** | 46.7% paid-only, 39.4% freemium, 14-day trial modal, $20–$50 starting tier. | B2C should lean toward freemium; Mynaani should avoid paid-only because of WTP data. |
| **Kyle Poyar (OpenView / Growth Unhinged)** | B2C free-to-paid conversion is ~20%; 50% of conversions happen in the first 7 days, 70% in 14 days, 90% in 30 days. Suggests reverse trials over pure free trials. | If a free trial is used, it must be short and high-touch, or a reverse trial is preferable. |
| **Patrick Campbell / ProfitWell (First Round Review, Reforge)** | WTP must be measured with Van Westendorp or price-sensitivity surveys; price must resonate with the persona; the value metric (how you charge) is as important as the price. | Pricing should be tied to a value metric learners understand, e.g., "one-time access to build Claude Skills." |
| **Reforge, Analyze Customer Willingness to Pay** | Consumers buy when WTP > price; different segments have different WTP. | Suggests two segments: learner (low WTP) and caregiver (higher WTP). |

### 1.5 Geragogy / trust constraints

| Source | Finding | Relevance |
|--------|---------|-----------|
| **Gates & Wilson-Menzfeld, 2022 (Journal of Applied Gerontology)** | Geragogy emphasizes autonomy, self-directed learning, and reducing objectified duty; negative perceptions of aging are a major barrier. | Pricing must feel like an empowered choice, not an obligation. |
| **Findsen & Formosa, 2012; Formosa, 2002/2011** | Geragogy supports independent and critical assessment of one's own life and experiences. | The paywall should come at a natural, value-demonstrated seam (Module 3 → 4). |
| **ACM CHI 2024 (Deceptive Patterns and Older Adults, DOI: 10.1145/3677113)** | **32% of older adults rated "Hidden Costs" and "Hard to Cancel" as the most concerning deceptive patterns.** | Auto-renew, hidden fees, and cancellation friction are deal-breakers. |
| **Trust-Led Subscription Design for Older Users (2024)** | Older users reward clarity, reliability, and respect; they will pay when the experience feels understandable, safe, and human-supported. | Pricing page must be plain-language, support-visible, and refund-guaranteed. |

---

## 2. Pricing approaches force-ranked

Scoring: 1 (poor) to 5 (excellent) across **Geragogy** (autonomy, no dark patterns), **Learner WTP** (older adult affordability), **Caregiver WTP**, **Flow Fit** (landing → auth → learning → paywall), **Trust/Safety**, **Revenue**, and **Simplicity**.

| Approach | Geragogy | Learner WTP | Caregiver WTP | Flow Fit | Trust | Revenue | Simplicity | Total |
|----------|----------|-------------|---------------|----------|-------|---------|------------|-------|
| **A. Fully free, grant/institution-funded** | 5 | 5 | 1 | 5 | 5 | 1 | 5 | 27 |
| **B. Freemium subscription ($7.99–$13.99/mo)** | 2 | 2 | 3 | 3 | 2 | 4 | 3 | 19 |
| **C. One-time lifetime purchase (current ADR 0021)** | 5 | 4 | 4 | 5 | 5 | 3 | 5 | 31 |
| **D. One-time + optional caregiver gift** | 5 | 4 | 5 | 4 | 5 | 4 | 4 | 31 |
| **E. Reverse trial (7–14 days premium free, then one-time)** | 4 | 3 | 4 | 5 | 4 | 4 | 4 | 28 |
| **F. Pay-per-module microtransactions** | 3 | 3 | 2 | 2 | 3 | 3 | 2 | 18 |
| **G. Institutional / B2B license (senior centers, Medicare Advantage)** | 4 | 1 (learner) | 4 (org) | 3 | 4 | 5 | 2 | 23 |

### Force-rank notes

1. **Fully free** maximizes adoption and trust but provides no revenue and is unsustainable without an external funder. It is the moral high ground but not a business model.
2. **Freemium subscription** scores low on geragogy and trust because of the documented older-adult aversion to auto-renew, cancellation friction, and hidden costs. The $7.99–$13.99/mo price is above the $3.70 WTP anchor from telecare research and competes with "free from family."
3. **One-time lifetime purchase** scores highest on trust and geragogy. It is a clear, bounded commitment: the learner knows exactly what they pay and what they get, with no surprise charges.
4. **Caregiver gift edition** is essentially the same model with a second payer. It opens a higher-WTP channel without changing the learner experience.
5. **Reverse trial** is a strong variant: let users experience Modules 4-5 for a limited time, then either keep them via one-time purchase or drop back to the free tier. It fits the flow well but adds implementation and support complexity.
6. **Pay-per-module** introduces repeated payment decisions, which erodes trust and cognitive safety.
7. **B2B / institutional license** is attractive for revenue and reach but is a separate go-to-market motion and not a substitute for the consumer flow.

---

## 3. Recommended model

**Primary recommendation: keep ADR 0021's one-time lifetime purchase, strengthen the caregiver-gift channel, and add a short, optional reverse trial for the paid modules.**

### Why this fits Mynaani

| Requirement | How the model satisfies it |
|-------------|---------------------------|
| **Landing / hero flow** | The "How it works" dialog can honestly say Modules 1-3 are free and complete. No credit card is needed to start. |
| **Auth / login** | Magic.link email signup is free. Payment only happens after the learner has completed 16 units and has built trust. |
| **Geragogy / autonomy** | The paywall appears at the natural Module 3 → 4 seam. The learner chooses to "build Skills and Agents" after already experiencing value. |
| **Trust / no dark patterns** | One-time price, no auto-renew, 30-day refund, exportable archive promise. This directly addresses the CHI 2024 finding that hidden costs and hard-to-cancel are the top concerns. |
| **Learner WTP** | $39 one-time is below the annual cost of Lumosity ($59.99) and Duolingo ($95.99), and converts to ~$3.25/month over a year — close to the $3.70 telecare WTP anchor. |
| **Caregiver WTP** | $59 gift edition targets the adult-child payer. It is a one-time, emotionally resonant purchase that does not create an ongoing financial relationship. |
| **Revenue sustainability** | Paid modules are 11 units of durable skill-building content with no per-user AI cost ceiling. A one-time price captures the value without creating unbounded usage cost risk. |

### Price positioning against evidence

- **$39 single-learner** is positioned as a one-time class fee, not a subscription. It is lower than the annual subscriptions of comparable edtech products, and it is framed as lifetime access to a productivity asset (Claude Skills and Agents).
- **$59 caregiver gift** is a $20 premium for the gift flow, receipt, and redemption. This is less than one hour of in-person tech help ($20–$100/hr) and creates a clear social-use case.
- **No monthly subscription in V1** because the AARP 2025 data shows that 60% of older adults are unwilling to pay for currently free digital services, and the telecare WTP median is only $3.70/month. A $39 one-time is psychologically closer to a small class or book than an ongoing bill.

### Reverse trial recommendation

A **7-day reverse trial** of Modules 4-5 is recommended as an *optional* experiment (with a new ADR and user-consent surface, per ADR 0021 §7):

- Learners who complete Module 3 are offered a free 7-day preview of Module 4.
- At the end of the 7 days, they can pay $39 to keep lifetime access, or their account drops back to the free tier.
- This addresses Kyle Poyar's finding that 50% of B2C conversions happen within 7 days, without the dark-pattern risk of a "trial that converts."
- It must be implemented with a clear, one-click "no, keep my free tier" option and no auto-charge.

---

## 4. Implementation implications for flow and auth

1. **Landing page:** no pricing on the hero. The CTA remains "How it works." Pricing appears only on a dedicated, accessible pricing page and at the Module 3 → 4 boundary.
2. **Auth:** free Magic.link signup; no payment during onboarding. Payment is a deliberate, post-learning action.
3. **Paywall:** the Module 3 → 4 prompt shows two calm options: "Continue with free tier" (Modules 1-3 remain open) and "Build Skills — one-time $39" (or "Buy as a gift — $59").
4. **Gift flow:** caregiver enters their email and the learner's email. The learner receives a redemption link via Magic.link; the caregiver receives a receipt. No ongoing account linkage.
5. **Refund:** one-click self-serve refund request within 30 days, logged to `billing_event` telemetry.
6. **Support:** a "Need help?" human callback or chat is visible on the pricing and paywall pages. Older adults convert when they can ask a human first.

---

## 5. Sources

1. AARP Research. *2025 Tech Trends and Adults 50-Plus*. https://www.aarp.org/research/topics/technology
2. Yamauchi et al. *Willngness to Pay for Elderly Telecare Service Using the Internet and Digital Terrestrial Broadcasting.* Interactive Journal of Medical Research, 2017. DOI: 10.2196/ijmr.7139
3. Yuan et al. *Determinants of and Willingness to Use and Pay for Digital Health Technologies Among the Urban Elderly.* Risk Management and Healthcare Policy, 2024. DOI: 10.2147/RMHP.S393767
4. Wang et al. *Caregivers' Willingness to Pay for Technologies to Support Caregiving.* The Gerontologist, 2016. DOI: 10.1093/geront/gnv033
5. Tang et al. *Findings From a National Survey of Older US Adults on Patient Willingness to Use Telehealth Services.* Journal of Medical Internet Research, 2024. DOI: 10.2196/50205
6. Gates & Wilson-Menzfeld. *What Role Does Geragogy Play in the Delivery of Digital Skills Programs for Middle and Older Age Adults?* Journal of Applied Gerontology, 2022. DOI: 10.1177/07334648221091236
7. Findsen & Formosa, 2012; Formosa, 2002/2011. Geragogy and critical geragogy.
8. CHI 2024. *"What a stupid way to do business": Towards an Understanding of Older Adults' Perceptions of Deceptive Patterns.* DOI: 10.1145/3677113
9. Kyle Poyar. *Your guide to PLG pricing 201* and *State of B2B Monetization* (Growth Unhinged / OpenView).
10. Patrick Campbell / ProfitWell. *How to price your startup product and service* (Airtree Ventures, First Round Review, Reforge).
11. Toolradar. *B2B SaaS Pricing Benchmarks 2026: Analysis of 9,024 Tools*.
12. Duolingo public pricing (super.duolingo.com/plus).
13. Lumosity public pricing (help.lumosity.com, App Store, lumosity.com/payment-policy).

---

## 6. Open questions for follow-up

1. Have we validated the $39/$59 price points with a small Van Westendorp survey of Mynaani's target learners and caregivers?
2. What is the marginal cost of serving a paid module user (Claude API usage, storage, support)?
3. Should we pilot the reverse trial with a small cohort before full release?
4. What payment processor and tax handling are required for one-time purchases and refunds?
