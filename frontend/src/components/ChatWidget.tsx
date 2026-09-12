/**
 * Retell website widget — persona-scoped (ADR 0032).
 *
 * Two DISTINCT journeys with two DISTINCT agents and knowledge bases:
 *   journey="gift"     — /gift and gift-mode /purchase/success
 *                        (KB has no community/org pricing)
 *   journey="facility" — /for-communities, /c/:slug, /org
 *                        (KB has no gift/individual pricing)
 * NEVER mount on the B2C learner journey.
 *
 * data-contract-exemption="chat-widget": the FAB + panel are rendered
 * by Retell's script, outside the closed-world component inventory.
 *
 * Geragogy: calm fab text, no popup, no auto-open, no urgency styling.
 * No-ops cleanly when the public key env vars are unset (e.g. dev).
 */
import { useEffect } from "react";
import { COLORS } from "../design/tokens";
import {
  RETELL_CHAT_AGENT_ID_FACILITY,
  RETELL_CHAT_AGENT_ID_GIFT,
  RETELL_PUBLIC_KEY,
} from "../lib/env";

const WIDGET_SRC = "https://dashboard.retellai.com/retell-widget-v2.js";

const AGENTS = {
  gift: RETELL_CHAT_AGENT_ID_GIFT,
  facility: RETELL_CHAT_AGENT_ID_FACILITY,
} as const;

export default function ChatWidget({
  journey,
}: {
  journey: keyof typeof AGENTS;
}) {
  useEffect(() => {
    const agentId = AGENTS[journey];
    if (!RETELL_PUBLIC_KEY || !agentId) return;
    if (document.getElementById("retell-widget")) return;

    const s = document.createElement("script");
    s.id = "retell-widget";
    s.src = WIDGET_SRC;
    s.type = "module";
    s.dataset.publicKey = RETELL_PUBLIC_KEY;
    s.dataset.agentId = agentId;
    s.dataset.agentVersion = "0";
    s.dataset.title = "Chat with MyNaani";
    s.dataset.fabText = "Ask a question";
    s.dataset.botName = "MyNaani assistant";
    s.dataset.showAiPopup = "false";
    s.dataset.autoOpen = "false";
    s.dataset.color = COLORS.accentMutedBlue;
    document.head.appendChild(s);

    return () => {
      // SPA navigation off a widget page must not leave the FAB on a
      // learner journey. The script dedupes by id; the widget injects
      // its own hosts — best-effort sweep, verify on staging.
      document.getElementById("retell-widget")?.remove();
      document
        .querySelectorAll('[id*="retell"], [class*="retell-widget"]')
        .forEach((el) => el.remove());
    };
  }, [journey]);

  return <span data-contract-exemption="chat-widget" hidden />;
}
