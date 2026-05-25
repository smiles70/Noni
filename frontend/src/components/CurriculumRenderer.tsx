/**
 * CurriculumRenderer — free-track wrapper (modules 1–3).
 *
 * Delegates to the shared `LessonRenderer` core extracted in Sprint
 * "paid modules" P4. The core handles NavBar, Indicator,
 * Previous/Continue flow, retrieval choices, progress persistence,
 * envelope loading, proposal accounting, and RenderGuard enforcement.
 *
 * This file only defines the free-track sequence and loader, then
 * passes them through.
 */
import { loadFreeLesson } from "../api/curriculum";
import LessonRenderer from "./curriculum/LessonRenderer";

interface Props {
  onSignIn?: () => void;
  onOpenMenu?: () => void;
  onContinueGated: () => void;
  onAccount?: () => void;
}

const FREE_SEQUENCE = [
  { module: 1, unitId: "unit-1" },
  { module: 1, unitId: "unit-2" },
  { module: 1, unitId: "unit-3" },
  { module: 1, unitId: "unit-4" },
  { module: 1, unitId: "unit-5" },
  { module: 1, unitId: "unit-6" },
  { module: 1, unitId: "unit-7" },
  { module: 2, unitId: "module2-unit-1" },
  { module: 2, unitId: "module2-unit-2" },
  { module: 2, unitId: "module2-unit-3" },
  { module: 2, unitId: "module2-unit-4" },
  { module: 2, unitId: "module2-unit-5" },
  { module: 3, unitId: "module3-unit-1" },
  { module: 3, unitId: "module3-unit-2" },
  { module: 3, unitId: "module3-unit-3" },
  { module: 3, unitId: "module3-unit-4" },
] as const;

export default function CurriculumRenderer({
  onSignIn,
  onOpenMenu,
  onContinueGated,
  onAccount,
}: Props) {
  return (
    <LessonRenderer
      sequence={FREE_SEQUENCE}
      loadLesson={(module, unitId) =>
        loadFreeLesson(module as 1 | 2 | 3, unitId)
      }
      onSequenceComplete={onContinueGated}
      onContinuePaid={onContinueGated}
      onSignIn={onSignIn}
      onOpenMenu={onOpenMenu}
      onAccount={onAccount}
    />
  );
}
