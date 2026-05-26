import { Component, type ErrorInfo, type ReactNode } from 'react';
import { logger } from '../lib/logger';
import { COLORS } from '../design/tokens';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

/**
 * Sprint 23 M6: React ErrorBoundary — catches unhandled errors in the
 * component tree and renders a safe fallback UI instead of a blank screen.
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to telemetry with request_id if available
    const requestId =
      (window as unknown as { __noni_request_id?: string }).__noni_request_id ??
      'unknown';
    logger.error('ErrorBoundary caught error', {
      requestId,
      error: error.message,
      componentStack: errorInfo.componentStack,
    });
    // TODO: forward to backend telemetry endpoint
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            padding: '2rem',
            textAlign: 'center',
            fontFamily: 'system-ui, sans-serif',
            color: COLORS.textPrimary,
            background: COLORS.background,
          }}
        >
          <h1 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
            Something went wrong.
          </h1>
          <p style={{ fontSize: '1rem', marginBottom: '1.5rem' }}>
            Please refresh the page or contact support if the problem persists.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '0.75rem 1.5rem',
              fontSize: '1rem',
              cursor: 'pointer',
              border: 'none',
              borderRadius: '4px',
              background: COLORS.accentMutedBlue,
              color: COLORS.surface,
            }}
          >
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
