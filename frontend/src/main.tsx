import './styles.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { applyLargeTextOnBoot } from './largeText';
import { AUTH_PROVIDER, CLERK_PUBLISHABLE_KEY } from './lib/env';
import { ClerkProvider } from '@clerk/clerk-react';
import { AuthProvider } from './auth/AuthProvider';
import { ErrorBoundary } from './components/ErrorBoundary';

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
  } catch (e) {
    // Sprint 28 quick-win: SecurityError (Safari private mode) plus
    // QuotaExceededError are both non-fatal for the reset flow.
    if (
      e instanceof DOMException &&
      (e.name === 'QuotaExceededError' || e.name === 'SecurityError')
    ) {
      /* proceed to redirect anyway */
    }
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
const provider = AUTH_PROVIDER;
const clerkKey = CLERK_PUBLISHABLE_KEY;

if (!resetting) {
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement,
);

if (provider === 'clerk') {
  if (!clerkKey) {
    // Sprint "Fix Red": graceful error instead of hard-throw (P11).
    // Geragogy-safe: calm, actionable message. No exclamation marks.
    root.render(
      <div style={{
        padding: '24px',
        fontFamily: 'Inter, system-ui, sans-serif',
        color: '#222222',
        backgroundColor: '#F4F4F2',
        maxWidth: '480px',
        margin: '48px auto',
        lineHeight: 1.6,
      }}>
        <h1 style={{ fontSize: '19px', marginBottom: '16px' }}>
          Configuration needed
        </h1>
        <p style={{ fontSize: '16px', marginBottom: '16px' }}>
          This build is configured for Clerk authentication, but the
          publishable key is missing. You can continue in mock mode
          or provide the key.
        </p>
        <p style={{ fontSize: '16px', color: '#4A6FA5' }}>
          To use mock mode: set VITE_AUTH_PROVIDER=mock
        </p>
      </div>,
    );
  } else {
    root.render(
      <React.StrictMode>
        <ErrorBoundary>
          {/* No `afterSignOutUrl` here: post-signout navigation is owned by
              App.tsx (handleSignedOut), which is the single source of truth
              for view transitions. Letting Clerk redirect us would race
              our state updates and unmount the SignOut button mid-await. */}
          <ClerkProvider publishableKey={clerkKey}>
            <AuthProvider>
              <App />
            </AuthProvider>
          </ClerkProvider>
        </ErrorBoundary>
      </React.StrictMode>,
    );
  }
} else {
  root.render(
    <React.StrictMode>
      <ErrorBoundary>
        <AuthProvider>
          <App />
        </AuthProvider>
      </ErrorBoundary>
    </React.StrictMode>,
  );
}
} // end if (!resetting)
