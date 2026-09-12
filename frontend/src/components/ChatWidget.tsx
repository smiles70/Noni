/**
 * Retell website widget — caregiver & senior-facility journeys ONLY.
 *
 * data-contract-exemption="chat-widget": ADR 0032. The floating action
 * button and chat panel are rendered by Retell's script, outside the
 * closed-world component inventory — exempted as a designated external
 * surface on these journeys only:
 *   /gift, /for-communities, /c/:slug, /org, and gift-mode
 *   /purchase/success. NEVER mount on the B2C learner journey.
 *
 * Geragogy: calm fab text, no popup, no auto-open, no urgency styling.
 * No-ops cleanly when the public key env vars are unset (e.g. dev).
 */
import { useEffect } from "react";
import { COLORS } from "../design/tokens";
import { RETELL_CHAT_AGENT_ID, RETELL_PUBLIC_KEY } from "../lib/env";

const WIDGET_SRC = "https://dashboard.retellai.com/retell-widget-v2.js";

export default function ChatWidget() {
  useEffect(() => {
    if (!RETELL_PUBLIC_KEY || !RETELL_CHAT_AGENT_ID) return;
    if (document.getElementById("retell-widget")) return;

    const s = document.createElement("script");
    s.id = "retell-widget";
    s.src = WIDGET_SRC;
    s.type = "module";
    s.dataset.publicKey = RETELL_PUBLIC_KEY;
    s.dataset.agentId = RETELL_CHAT_AGENT_ID;
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
  }, []);

  return <span data-contract-exemption="chat-widget" hidden />;
}
