/**
 * CurriculumMenu — read-only lesson syllabus (S25.1).
 *
 * Renders the full course table of contents (Modules 1-5, with M4-M5
 * shown as gated entries) so a learner can preview what they will
 * encounter without committing to a sign-in or to a particular lesson.
 * Paid units are non-interactive and carry a muted-amber lock indicator
 * per CONTRACT I.A.
 *
 * Per ADR 0019 and CONTRACT Section IV:
 *   - Resolves its envelope from `/api/ui-envelope/curriculum.menu`.
 *   - Renders inside a RenderGuard boundary (fail-closed).
 *   - Uses ONLY tokens from `design/tokens.ts`.
 *
 * Primary-action accounting (envelope max=3):
 *   NavBar(≤2) + Continue(1) = ≤3 ✓
 *
 * Unit rows are rendered as plain text inside a List, NOT as Buttons:
 * the menu is a syllabus, not a deep-link launcher. Picking a specific
 * lesson is a future affordance; today, Continue resumes the learner
 * at their last position. This keeps the proposal honest and the
 * contract ceiling unbroken.
 */
import { CSSProperties, useEffect, useState } from "react";
import { loadEnvelope } from "../api/envelope";
import { loadCurriculumMenu, type CurriculumMenu } from "../api/curriculum";
import { COLORS, SPACING, TYPOGRAPHY, RADIUS } from "../design/tokens";
import type { UIStateEnvelope } from "../design/envelope";
import { RenderGuard, type RenderProposal } from "../design/RenderGuard";
import NavBar from "./NavBar";

interface Props {
  /** Resume the linear lesson sequence from saved progress. */
  onContinue: () => void;
  onSignIn?: () => void;
  onContinuePaid?: () => void;
  onAccount?: () => void;
  /** Jump to a specific unit (Module 0–3 free track). */
  onSelectUnit?: (module: number, unitId: string) => void;
  onHelp?: () => void;
}

const PAGE: CSSProperties = {
  background: COLORS.background,
  color: COLORS.textPrimary,
  fontFamily: TYPOGRAPHY.fontFamily,
  fontSize: TYPOGRAPHY.bodySizePx,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  padding: SPACING.lg,
  minHeight: "100vh",
};

const HEADING: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level1,
  fontWeight: 600,
  margin: 0,
  marginBottom: SPACING.md,
};

const INTRO: CSSProperties = {
  margin: 0,
  marginBottom: SPACING.xl,
  maxWidth: 640,
};

const SECTION: CSSProperties = {
  background: COLORS.surface,
  borderRadius: RADIUS.lg,
  padding: SPACING.lg,
  marginBottom: SPACING.md,
  maxWidth: 640,
};

const MODULE_TITLE: CSSProperties = {
  fontSize: TYPOGRAPHY.headingScale.level2,
  fontWeight: 600,
  margin: 0,
  marginBottom: SPACING.sm,
};

const UNIT_LIST: CSSProperties = {
  margin: 0,
  paddingLeft: SPACING.md,
};

const UNIT_ITEM: CSSProperties = {
  marginBottom: SPACING.xs,
};

const UNIT_BUTTON: CSSProperties = {
  fontSize: TYPOGRAPHY.bodySizePx,
  fontFamily: TYPOGRAPHY.fontFamily,
  lineHeight: TYPOGRAPHY.bodyLineHeight,
  padding: `${SPACING.sm}px ${SPACING.md}px`,
  backgroundColor: COLORS.surface,
  color: COLORS.accentMutedBlue,
  border: `2px solid ${COLORS.accentMutedBlue}`,
  borderRadius: RADIUS.sm,
  cursor: "pointer",
  textAlign: "left",
  width: "100%",
  marginBottom: SPACING.xs,
};

const UNIT_DESCRIPTION: CSSProperties = {
  color: COLORS.disabled,
  fontSize: TYPOGRAPHY.bodySizePx,
};

const LOCK_INDICATOR: CSSProperties = {
  color: COLORS.accentMutedAmber,
  fontSize: TYPOGRAPHY.bodySizePx,
  fontWeight: 600,
};

const CONTINUE_BUTTON: CSSProperties = {
  background: COLORS.accentMutedBlue,
  color: COLORS.surface,
  border: "none",
  borderRadius: RADIUS.sm,
  padding: `${SPACING.sm}px ${SPACING.lg}px`,
  fontSize: TYPOGRAPHY.bodySizePx,
  fontFamily: TYPOGRAPHY.fontFamily,
  cursor: "pointer",
  marginTop: SPACING.lg,
};

export default function CurriculumMenu(props: Props) {
  const { onContinue, onSignIn, onContinuePaid, onAccount, onSelectUnit, onHelp } = props;
  const [envelope, setEnvelope] = useState<UIStateEnvelope | null>(null);
  const [menu, setMenu] = useState<CurriculumMenu | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    loadEnvelope("curriculum.menu")
      .then((env) => {
        if (!cancelled) setEnvelope(env);
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load envelope");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    loadCurriculumMenu()
      .then((m) => {
        if (!cancelled) setMenu(m);
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load menu");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <main aria-live="polite" data-component="BlockedNotice" style={PAGE}>
        <p>The lesson menu could not be loaded: {error}</p>
      </main>
    );
  }
  if (!envelope || !menu) {
    return (
      <main aria-live="polite" data-component="PendingBanner" style={PAGE}>
        <p>One moment — loading.</p>
      </main>
    );
  }

  // NavBar contribution: up to 2 (Upgrade + Account) when signed in.
  // Continue is the single highlighted recommendation.
  // Paid modules add Indicator (lock status) but no new primary actions.
  const proposal: RenderProposal = {
    components: ["Heading", "Body", "Button", "Card", "List", "Indicator"],
    primaryActionCount: 2 /* NavBar worst-case */ + 1 /* Continue */,
    irreversibleActionCount: 0,
    highlightedRecommendationCount: 1,
    visibleTextLevels: 2 /* h1 module + body */,
    colorsUsed: [
      COLORS.background,
      COLORS.surface,
      COLORS.textPrimary,
      COLORS.accentMutedBlue,
      COLORS.accentMutedAmber,
      COLORS.disabled,
    ],
    spacingPxUsed: [SPACING.xs, SPACING.sm, SPACING.md, SPACING.lg, SPACING.xl],
    radiusPxUsed: [RADIUS.sm, RADIUS.lg],
    motionDurationsMs: [],
    positionShiftPxUsed: [],
    hasUnconfirmedIrreversibleAction: false,
    usesOptimisticProgression: false,
  };

  return (
    <RenderGuard envelope={envelope} proposal={proposal}>
      <main style={PAGE} data-component="Card">
        <NavBar
          onSignIn={onSignIn}
          onContinuePaid={onContinuePaid}
          onAccount={onAccount}
          onHelp={onHelp}
        />
        <h1 style={HEADING} data-component="Heading">
          Lessons
        </h1>
        <p style={INTRO} data-component="Body">
          Here is the full course at a glance. Modules 0–3 are free.
          Modules 4–5 are available after a one-time purchase.
          Tap any free lesson to jump straight to it.
        </p>

        {menu.modules.map((mod) => (
          <section key={mod.id} style={SECTION} data-component="Card">
            <h2 style={MODULE_TITLE} data-component="Heading">
              {mod.title}
            </h2>
            <ul style={UNIT_LIST} data-component="List">
              {mod.units.map((u) => (
                <li key={u.id} style={UNIT_ITEM}>
                  {onSelectUnit ? (
                    <button
                      type="button"
                      style={UNIT_BUTTON}
                      onClick={() => onSelectUnit(mod.id, u.id)}
                    >
                      <strong>{u.title}</strong>
                      <span style={UNIT_DESCRIPTION}> — {u.description}</span>
                    </button>
                  ) : (
                    <>
                      <strong>{u.title}</strong>
                      <span style={UNIT_DESCRIPTION}> — {u.description}</span>
                    </>
                  )}
                </li>
              ))}
            </ul>
          </section>
        ))}

        {menu.bridge_units.length > 0 ? (
          <section style={SECTION} data-component="Card">
            <h2 style={MODULE_TITLE} data-component="Heading">
              Side lessons (optional)
            </h2>
            <ul style={UNIT_LIST} data-component="List">
              {menu.bridge_units.map((u) => (
                <li key={u.id} style={UNIT_ITEM}>
                  <strong>{u.title}</strong>
                  <span style={UNIT_DESCRIPTION}> — {u.description}</span>
                </li>
              ))}
            </ul>
          </section>
        ) : null}

        {/* Paid modules — surfaced as gated, non-interactive entries. */}
        <section style={SECTION} data-component="Card">
          <h2 style={MODULE_TITLE} data-component="Heading">
            Module 4 — Building Claude Skills
          </h2>
          <ul style={UNIT_LIST} data-component="List">
            <li style={UNIT_ITEM}>
              <span style={LOCK_INDICATOR} data-component="Indicator">
                Locked —{" "}
              </span>
              <strong>What a Claude Skill Is</strong>
              <span style={UNIT_DESCRIPTION}>
                {" "}
                — Understanding Skills as named, reusable instructions.
              </span>
            </li>
            <li style={UNIT_ITEM}>
              <span style={LOCK_INDICATOR} data-component="Indicator">
                Locked —{" "}
              </span>
              <strong>When a Skill Is Useful</strong>
              <span style={UNIT_DESCRIPTION}>
                {" "}
                — Learning when a Skill helps more than repeating instructions.
              </span>
            </li>
            <li style={UNIT_ITEM}>
              <span style={LOCK_INDICATOR} data-component="Indicator">
                Locked —{" "}
              </span>
              <strong>Creating Your First Skill</strong>
              <span style={UNIT_DESCRIPTION}>
                {" "}
                — Building a simple Skill with Claude&apos;s help.
              </span>
            </li>
            <li style={UNIT_ITEM}>
              <span style={LOCK_INDICATOR} data-component="Indicator">
                Locked —{" "}
              </span>
              <strong>Naming and Describing a Skill</strong>
              <span style={UNIT_DESCRIPTION}>
                {" "}
                — Making Skills clear, readable, and trustworthy.
              </span>
            </li>
            <li style={UNIT_ITEM}>
              <span style={LOCK_INDICATOR} data-component="Indicator">
                Locked —{" "}
              </span>
              <strong>Testing and Refining a Skill</strong>
              <span style={UNIT_DESCRIPTION}>
                {" "}
                — Checking that a Skill behaves the way you expect.
              </span>
            </li>
            <li style={UNIT_ITEM}>
              <span style={LOCK_INDICATOR} data-component="Indicator">
                Locked —{" "}
              </span>
              <strong>Trusting a Skill Over Time</strong>
              <span style={UNIT_DESCRIPTION}>
                {" "}
                — Using Skills confidently while staying in control.
              </span>
            </li>
          </ul>
        </section>

        <section style={SECTION} data-component="Card">
          <h2 style={MODULE_TITLE} data-component="Heading">
            Module 5 — Composing Agents
          </h2>
          <ul style={UNIT_LIST} data-component="List">
            <li style={UNIT_ITEM}>
              <span style={LOCK_INDICATOR} data-component="Indicator">
                Locked —{" "}
              </span>
              <strong>What an Agent Is (Built from Skills)</strong>
              <span style={UNIT_DESCRIPTION}>
                {" "}
                — Understanding agents as structured roles made from Skills.
              </span>
            </li>
            <li style={UNIT_ITEM}>
              <span style={LOCK_INDICATOR} data-component="Indicator">
                Locked —{" "}
              </span>
              <strong>Designing an Agent&apos;s Job</strong>
              <span style={UNIT_DESCRIPTION}>
                {" "}
                — Defining what an agent should do — and what it should not do.
              </span>
            </li>
            <li style={UNIT_ITEM}>
              <span style={LOCK_INDICATOR} data-component="Indicator">
                Locked —{" "}
              </span>
              <strong>Building an Agent Step by Step</strong>
              <span style={UNIT_DESCRIPTION}>
                {" "}
                — Creating an agent by combining Skills carefully.
              </span>
            </li>
            <li style={UNIT_ITEM}>
              <span style={LOCK_INDICATOR} data-component="Indicator">
                Locked —{" "}
              </span>
              <strong>Using an Agent Safely</strong>
              <span style={UNIT_DESCRIPTION}>
                {" "}
                — Working with agents while staying in control.
              </span>
            </li>
            <li style={UNIT_ITEM}>
              <span style={LOCK_INDICATOR} data-component="Indicator">
                Locked —{" "}
              </span>
              <strong>Staying the Authority</strong>
              <span style={UNIT_DESCRIPTION}>
                {" "}
                — Reinforcing dignity, judgment, and control when using agents.
              </span>
            </li>
          </ul>
        </section>

        <button
          type="button"
          style={CONTINUE_BUTTON}
          data-component="Button"
          onClick={onContinue}
        >
          Continue your lesson →
        </button>
      </main>
    </RenderGuard>
  );
}
