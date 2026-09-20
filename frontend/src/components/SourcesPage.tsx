/**
 * SourcesPage — /sources — shared evidence surface (PS-BID17-004).
 *
 * Owner directive: references live here, not inline on the marketing
 * pages. Persona-partitioned groups (caregiver set / community set) —
 * the lists stay separated, no cross-referencing claims. Persona-neutral
 * shared surface: light paper document layout, default footer.
 */
import { CSSProperties } from "react";
import { Link } from "react-router-dom";
import { COLORS, SPACING, TYPOGRAPHY } from "../design/tokens";
import Footer from "./Footer";

const PAGE: CSSProperties = {
  fontFamily: TYPOGRAPHY.fontFamily,
  color: COLORS.textPrimary,
  backgroundColor: COLORS.background,
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  minHeight: "100vh",
};

const WRAP: CSSProperties = {
  maxWidth: 720,
  margin: "0 auto",
  padding: `${SPACING.xl}px ${SPACING.lg}px ${SPACING.xxl}px`,
};

const GROUP_LABEL: CSSProperties = {
  fontSize: 13,
  fontWeight: 700,
  letterSpacing: 1.5,
  textTransform: "uppercase",
  color: COLORS.textPrimary,
  margin: `${SPACING.xl}px 0 ${SPACING.sm}px`,
};

const SOURCE_ITEM: CSSProperties = {
  marginBottom: SPACING.lg,
  fontSize: 15,
  lineHeight: 1.65,
};

const LINK: CSSProperties = {
  color: COLORS.accentMutedBlue,
  fontWeight: 600,
};

const CAREGIVER_SOURCES = [
  {
    name: 'Tang X. et al. — "I Never Imagined Grandma Could Do So Well with Technology" (CSCW 2022)',
    url: "https://xinrutang.github.io/file/FamilyCSCW22/FamilyCSCW22.pdf",
    why: "Younger family members support older adults' technology learning over time as influencers, supporters, protectors, and monitors.",
  },
  {
    name: "Caregiver Action Network — CIC Caregiver Tech Insights Survey (2026)",
    url: "https://www.caregiveraction.org/wp-content/uploads/2026/05/CIC-Survey-2026.pdf",
    why: "90% of family caregivers already use digital tools; nearly four in ten spend 11 or more hours per week on care coordination.",
  },
  {
    name: "AARP / Age in Place Tech — 2025 Technology Trends: Older Adults and Caregiving",
    url: "https://www.ageinplacetech.com/files/aip/2025-technology-trends-older-adults-caregiving.doi_.10.26419-2fres.00891.007.pdf",
    why: "Adults 50+ who are caregivers adopt convenience and safety technology more often than non-caregivers.",
  },
  {
    name: "JMIR Aging — Application-based interventions for family caregivers of older adults: scoping review (2026)",
    url: "https://aging.jmir.org/2026/1/e76115",
    why: "Apps can improve caregiver well-being and burden, but the biggest gap is usable, well-evaluated design.",
  },
  {
    name: "SSPH+ / Frontiers in Public Health Reviews — Digital Informal Care: The Use of Technology in Family Care (2025)",
    url: "https://www.ssph-journal.org/journals/public-health-reviews/articles/10.3389/phrs.2025.1608872/full",
    why: "Digital tools can reduce caregiver burden and improve competence, but only when they are usable and accessible.",
  },
  {
    name: "Heliyon — The impact of family members on aging persons' technology use intentions (2025)",
    url: "https://doi.org/10.1016/j.heliyon.2025.e42252",
    why: "When family caregivers and older adults share the same belief about capability, technology use intention is highest.",
  },
  {
    name: "Laganà L. et al. — Enhancing computer self-efficacy in older adults: a randomised controlled study",
    url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC4265211/",
    why: "Age-appropriate, self-paced training significantly improves attitudes and self-efficacy in older learners.",
  },
];

const COMMUNITY_SOURCES = [
  {
    name: "Pew Research Center — How Americans' opinions and use of AI differ by age (2026)",
    url: "https://www.pewresearch.org/internet/2026/06/17/how-opinions-and-use-of-ai-differ-by-age/",
    why: "AI chatbot adoption: 57% under-50 vs. 28% ages 50+; 65+ the most uncertain group.",
  },
  {
    name: "Nielsen Norman Group — Usability for Senior Citizens",
    url: "https://www.nngroup.com/articles/usability-seniors-improvements/",
    why: "Adults 65+ succeed at website tasks 55% vs. 75% for ages 21–55, ~43% slower.",
  },
  {
    name: "W3C Web Accessibility Initiative — Web Accessibility for Older Users: A Literature Review",
    url: "https://www.w3.org/WAI/older-users/literature/",
    why: "Ageing vision: ~80% contrast-sensitivity loss by age 80; presbyopia; colour-shift.",
  },
  {
    name: "Owsley C. — Vision and Aging, Annual Review of Vision Science (UAB School of Medicine)",
    url: "https://www.annualreviews.org/content/journals/10.1146/annurev-vision-111815-114550",
    why: "Contrast sensitivity and visual-processing-speed decline in later life.",
  },
  {
    name: "Hasher L. & Zacks R.T. — Working memory, comprehension, and aging (University of Toronto)",
    url: "https://hasherlab.psych.utoronto.ca/abstracts/hasher_zacks_88.htm",
    why: "Aging reduces inhibition of irrelevant information — visual distraction harms learning.",
  },
  {
    name: "JMIR (2025) — Cognitive load and learning performance in digital health education for older patients",
    url: "https://www.jmir.org/2025/1/e79430",
    why: "Cognitive load is the key mediator of digital-learning outcomes (large effect).",
  },
  {
    name: "Laganà L. et al. — Enhancing computer self-efficacy in older adults: a randomised controlled study",
    url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC4265211/",
    why: "Age-appropriate training significantly improves attitudes and self-efficacy.",
  },
];

function SourceGroup({
  label,
  items,
}: {
  label: string;
  items: { name: string; url: string; why: string }[];
}) {
  return (
    <section aria-label={label}>
      <h2 style={GROUP_LABEL}>{label}</h2>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {items.map((s) => (
          <li key={s.url} style={SOURCE_ITEM}>
            <a
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              style={LINK}
            >
              {s.name}
            </a>
            <br />
            <span style={{ color: COLORS.textPrimary }}>{s.why}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default function SourcesPage() {
  return (
    <div style={PAGE} data-contract-exemption="marketing.sources">
      <main style={WRAP}>
        <h1
          style={{
            fontSize: TYPOGRAPHY.headingScale.level1,
            fontWeight: 700,
            lineHeight: 1.4,
            margin: 0,
          }}
        >
          Sources
        </h1>
        <p style={{ color: COLORS.textPrimary, marginTop: SPACING.sm }}>
          Every claim on our marketing pages is backed by a published, reachable
          source. The research behind what we say — free to read and judge for
          yourself.
        </p>
        <SourceGroup label="For caregivers" items={CAREGIVER_SOURCES} />
        <SourceGroup
          label="For communities &amp; facilities"
          items={COMMUNITY_SOURCES}
        />
        <p
          style={{
            fontSize: 15,
            color: COLORS.textPrimary,
            marginTop: SPACING.xl,
          }}
        >
          Questions about the research?{" "}
          <Link to="/contact" style={LINK}>
            Send us a note
          </Link>
          .
        </p>
      </main>
      <Footer currentPath="/sources" />
    </div>
  );
}
