/**
 * PaidLessonRenderer — paid-track wrapper (modules 4–5).
 *
 * Delegates to the shared `LessonRenderer` core (Sprint P4 extraction)
 * with the paid-track sequence and `loadPaidLesson` loader. The loader
 * unwraps the discriminated 200/402 result into `LessonResponse` on
 * success, or throws `PaywallError` on 402 so the core can route to
 * `onPaywall` instead of showing a generic error banner.
 *
 * On the final unit's last page, Continue shows "Finish →" rather than
 * the free-track's "Continue to paid modules →".
 */
import { loadPaidLesson, PaywallError } from "../api/curriculum";
import type { PaywallSignal } from "../api/curriculum";
import LessonRenderer from "./curriculum/LessonRenderer";

interface Props {
  onSignIn?: () => void;
  onOpenMenu?: () => void;
  onAccount?: () => void;
  /** Called when the learner finishes the last paid unit. */
  onSequenceComplete: () => void;
  /** Called when any paid lesson load returns 402. The parent should
   *  switch to the paywall view. */
  onPaywall: (signal: PaywallSignal) => void;
  onHelp?: () => void;
}

const PAID_SEQUENCE = [
  { module: 4, unitId: "module4-unit-1" },
  { module: 4, unitId: "module4-unit-2" },
  { module: 4, unitId: "module4-unit-3" },
  { module: 4, unitId: "module4-unit-4" },
  { module: 4, unitId: "module4-unit-5" },
  { module: 4, unitId: "module4-unit-6" },
  { module: 5, unitId: "module5-unit-1" },
  { module: 5, unitId: "module5-unit-2" },
  { module: 5, unitId: "module5-unit-3" },
  { module: 5, unitId: "module5-unit-4" },
  { module: 5, unitId: "module5-unit-5" },
] as const;

export default function PaidLessonRenderer({
  onSignIn,
  onOpenMenu,
  onAccount,
  onSequenceComplete,
  onPaywall,
  onHelp,
}: Props) {
  return (
    <LessonRenderer
      sequence={PAID_SEQUENCE}
      loadLesson={async (module, unitId) => {
        const result = await loadPaidLesson(module as 4 | 5, unitId);
        if (result.kind === "ok") return result.lesson;
        if (result.kind === "paywall") {
          throw new PaywallError(result.signal);
        }
        throw new Error(result.message);
      }}
      onSequenceComplete={onSequenceComplete}
      onSignIn={onSignIn}
      onOpenMenu={onOpenMenu}
      onAccount={onAccount}
      onPaywall={onPaywall}
      onHelp={onHelp}
      getContinueLabel={(isLastUnit, isLastPage) =>
        isLastUnit && isLastPage ? "Finish →" : "Continue →"
      }
    />
  );
}
