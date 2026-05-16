import './styles.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { applyLargeTextOnBoot } from './largeText';
import { ClerkProvider } from '@clerk/clerk-react';
import { ClerkTokenBridge } from './components/ClerkTokenBridge';

applyLargeTextOnBoot();

// Dev/QA escape hatch: ?reset=1 wipes Noni-owned client state and
// reloads to the same path with the param stripped. Lets a developer
// or tester return to Lesson 1 without DevTools tricks.
//
// Surgical scope: clears ONLY the two keys this app writes itself
// (noni_progress_v1, noni.mock_token). Clerk-owned localStorage is
// left untouched so a Clerk-signed-in user stays signed in across
// the reset; only their curriculum position is rewound.
//
// `resetting` short-circuits the React mount below so we don't render
// a stale frame between location.replace() and the new page loading.
const resetting = ((): boolean => {
  const params = new URLSearchParams(window.location.search);
  if (params.get('reset') !== '1') return false;
  try {
    localStorage.removeItem('noni_progress_v1');
    localStorage.removeItem('noni.mock_token');
  } catch {
    /* private mode / quota — proceed to redirect anyway */
  }
  const url = new URL(window.location.href);
  url.searchParams.delete('reset');
  window.location.replace(url.toString());
  return true;
})();

// VITE_AUTH_PROVIDER selects the auth path at build time:
//   - "mock"  -> dev/tests; SignInPage renders an email form, credential
//                is "mock:<email>". No ClerkProvider mounted.
//   - "clerk" -> production (post-ADR-0024); ClerkProvider wraps the
//                tree, SignInPage renders Clerk's <SignIn /> widget.
// Default is "mock" so a freshly-cloned repo runs without any external
// signup. Switching to Clerk requires both env vars below.
const env = (import.meta as unknown as {
  env?: { VITE_AUTH_PROVIDER?: string; VITE_CLERK_PUBLISHABLE_KEY?: string };
}).env ?? {};
const provider = env.VITE_AUTH_PROVIDER ?? 'mock';
const clerkKey = env.VITE_CLERK_PUBLISHABLE_KEY ?? '';

if (!resetting) {
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement,
);

if (provider === 'clerk') {
  if (!clerkKey) {
    // Fail loud at boot rather than crashing inside Clerk later.
    throw new Error(
      'VITE_AUTH_PROVIDER=clerk requires VITE_CLERK_PUBLISHABLE_KEY to be set at build time.',
    );
  }
  root.render(
    <React.StrictMode>
      {/* No `afterSignOutUrl` here: post-signout navigation is owned by
          App.tsx (handleSignedOut), which is the single source of truth
          for view transitions. Letting Clerk redirect us would race
          our state updates and unmount the SignOut button mid-await. */}
      <ClerkProvider publishableKey={clerkKey}>
        <ClerkTokenBridge />
        <App />
      </ClerkProvider>
    </React.StrictMode>,
  );
} else {
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
}
} // end if (!resetting)
