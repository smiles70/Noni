/**
 * CurriculumMenu — read-only lesson syllabus (S25.1).
 *
 * Renders the full free-track table of contents (Modules 1-3 + bridge
 * side lessons) so a learner can preview what they will encounter
 * without committing to a sign-in or to a particular lesson. Modules
 * 4+ are paid and intentionally never appear here; do not infer their
 * existence from this menu.
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

const UNIT_DESCRIPTION: CSSProperties = {
  color: COLORS.disabled,
  fontSize: TYPOGRAPHY.bodySizePx,
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
  const { onContinue, onSignIn, onContinuePaid, onAccount } = props;
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
  const proposal: RenderProposal = {
    components: ["Heading", "Body", "Button", "Card", "List"],
    primaryActionCount: 2 /* NavBar worst-case */ + 1 /* Continue */,
    irreversibleActionCount: 0,
    highlightedRecommendationCount: 1,
    visibleTextLevels: 2 /* h1 module + body */,
    colorsUsed: [
      COLORS.background,
      COLORS.surface,
      COLORS.textPrimary,
      COLORS.accentMutedBlue,
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
        />
        <h1 style={HEADING} data-component="Heading">
          Lessons
        </h1>
        <p style={INTRO} data-component="Body">
          Here is the full free course at a glance. There are three modules,
          plus a couple of optional side lessons. You can browse them now, or
          jump straight in.
        </p>

        {menu.modules.map((mod) => (
          <section key={mod.id} style={SECTION} data-component="Card">
            <h2 style={MODULE_TITLE} data-component="Heading">
              {mod.title}
            </h2>
            <ul style={UNIT_LIST} data-component="List">
              {mod.units.map((u) => (
                <li key={u.id} style={UNIT_ITEM}>
                  <strong>{u.title}</strong>
                  <span style={UNIT_DESCRIPTION}> — {u.description}</span>
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
