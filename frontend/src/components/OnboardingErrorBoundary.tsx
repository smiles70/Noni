/**
 * OnboardingErrorBoundary - Error handling for onboarding flow (EPIC-002 Phase 4)
 *
 * Geragogy-compliant error boundary that provides calm, non-alarmist error
 * handling for the onboarding flow with clear recovery options.
 *
 * Key geragogy principles:
 * - Predictable interface with stable layout
 * - Calm, dignified error messages without urgency
 * - Clear recovery options
 * - Maximum 3 text levels visible
 * - Maximum 3 primary actionable elements
 * - Preserves visual context during errors
 * - Errors presented as system states, not user failures
 */
import * as React from "react";
import {
  BODY,
  CARD,
  DIVIDER,
  H1,
  PAGE,
  PRIMARY_BTN,
  SECONDARY_BTN,
  STACK,
} from "./AccountStyles";

interface Props {
  children: React.ReactNode;
  onRetry?: () => void;
  onSkip?: () => void;
  fallbackComponent?: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

export default class OnboardingErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    this.setState({
      error,
      errorInfo,
    });

    // Log error for debugging
    console.error("Onboarding error boundary caught:", error, errorInfo);
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
    this.props.onRetry?.();
  };

  handleSkip = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
    this.props.onSkip?.();
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallbackComponent) {
        return this.props.fallbackComponent;
      }

      return (
        <main style={PAGE}>
          <h1 style={H1}>Something went wrong</h1>

          <div style={CARD}>
            <p style={BODY}>
              The onboarding process encountered an issue. This is a system
              state, not something you did wrong. You can try again or skip
              this step and continue to the curriculum.
            </p>
          </div>

          <div style={STACK}>
            {this.props.onRetry && (
              <button
                type="button"
                style={PRIMARY_BTN}
                onClick={this.handleRetry}
              >
                Try again
              </button>
            )}
            {this.props.onSkip && (
              <button
                type="button"
                style={SECONDARY_BTN}
                onClick={this.handleSkip}
              >
                Skip this step
              </button>
            )}
          </div>

          <hr style={DIVIDER} />
          <p style={BODY}>
            If this issue continues, you can contact support for assistance.
            Your progress is saved automatically.
          </p>
        </main>
      );
    }

    return this.props.children;
  }
}