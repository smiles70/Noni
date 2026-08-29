import "./styles.css";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { applyLargeTextOnBoot } from "./largeText";
import { AuthProvider } from "./auth/AuthProvider";
import { ErrorBoundary } from "./components/ErrorBoundary";

// One-time migration: move old noni-prefixed client state to mynaani.
// This preserves existing user sessions/progress after the brand rename.
function migrateNoniStorage() {
  try {
    const localRenames: [string, string][] = [
      ["noni_progress_v1", "mynaani_progress_v1"],
      ["noni_large_text", "mynaani_large_text"],
      ["noni.mock_token", "mynaani.mock_token"],
      ["noni.magic_token", "mynaani.magic_token"],
    ];
    for (const [oldKey, newKey] of localRenames) {
      const value = localStorage.getItem(oldKey);
      if (value !== null && localStorage.getItem(newKey) === null) {
        localStorage.setItem(newKey, value);
        localStorage.removeItem(oldKey);
      }
    }
    const sessionRenames: [string, string][] = [
      ["noni.auth_banner_retries", "mynaani.auth_banner_retries"],
    ];
    for (const [oldKey, newKey] of sessionRenames) {
      const value = sessionStorage.getItem(oldKey);
      if (value !== null && sessionStorage.getItem(newKey) === null) {
        sessionStorage.setItem(newKey, value);
        sessionStorage.removeItem(oldKey);
      }
    }
  } catch {
    // storage may be unavailable; ignore
  }
}

migrateNoniStorage();
applyLargeTextOnBoot();

// Dev/QA escape hatch: ?reset=1 wipes Mynaani-owned client state and
// reloads to the same path with the param stripped. Lets a developer
// or tester return to Lesson 1 without DevTools tricks.
const resetting = ((): boolean => {
  const params = new URLSearchParams(window.location.search);
  if (params.get("reset") !== "1") return false;
  try {
    localStorage.removeItem("mynaani_progress_v1");
    localStorage.removeItem("mynaani.mock_token");
    localStorage.removeItem("mynaani.magic_token");
  } catch (e) {
    if (
      e instanceof DOMException &&
      (e.name === "QuotaExceededError" || e.name === "SecurityError")
    ) {
      /* proceed to redirect anyway */
    }
  }
  const url = new URL(window.location.href);
  url.searchParams.delete("reset");
  window.location.replace(url.toString());
  return true;
})();

if (!resetting) {
  const root = ReactDOM.createRoot(
    document.getElementById("root") as HTMLElement,
  );

  root.render(
    <React.StrictMode>
      <ErrorBoundary>
        <BrowserRouter>
          <AuthProvider>
            <App />
          </AuthProvider>
        </BrowserRouter>
      </ErrorBoundary>
    </React.StrictMode>,
  );
}
