import './styles.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { applyLargeTextOnBoot } from './largeText';
import { ClerkProvider } from '@clerk/clerk-react';

applyLargeTextOnBoot();

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
      <ClerkProvider publishableKey={clerkKey} afterSignOutUrl="/">
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
