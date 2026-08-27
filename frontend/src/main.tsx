import './styles.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { applyLargeTextOnBoot } from './largeText';
import { AuthProvider } from './auth/AuthProvider';
import { ErrorBoundary } from './components/ErrorBoundary';

applyLargeTextOnBoot();

// Dev/QA escape hatch: ?reset=1 wipes Mynaani-owned client state and
// reloads to the same path with the param stripped. Lets a developer
// or tester return to Lesson 1 without DevTools tricks.
const resetting = ((): boolean => {
  const params = new URLSearchParams(window.location.search);
  if (params.get('reset') !== '1') return false;
  try {
    localStorage.removeItem('noni_progress_v1');
    localStorage.removeItem('noni.mock_token');
  } catch (e) {
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

if (!resetting) {
  const root = ReactDOM.createRoot(
    document.getElementById('root') as HTMLElement,
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
