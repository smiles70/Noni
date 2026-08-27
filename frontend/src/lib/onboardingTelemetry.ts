/**
 * Onboarding telemetry tracking (EPIC-002 Phase 4)
 *
 * Tracks onboarding flow events for monitoring and analytics.
 * Integrates with BetterStack monitoring for production observability.
 */

interface OnboardingEvent {
  event: string;
  timestamp: number;
  userId?: string;
  metadata?: Record<string, unknown>;
}

class OnboardingTelemetry {
  private static instance: OnboardingTelemetry;
  private events: OnboardingEvent[] = [];
  private maxEvents = 100;

  private constructor() {}

  static getInstance(): OnboardingTelemetry {
    if (!OnboardingTelemetry.instance) {
      OnboardingTelemetry.instance = new OnboardingTelemetry();
    }
    return OnboardingTelemetry.instance;
  }

  /**
   * Track an onboarding event
   */
  track(event: string, metadata?: Record<string, unknown>): void {
    const telemetryEvent: OnboardingEvent = {
      event,
      timestamp: Date.now(),
      metadata,
    };

    this.events.push(telemetryEvent);

    // Keep only the most recent events
    if (this.events.length > this.maxEvents) {
      this.events = this.events.slice(-this.maxEvents);
    }

    // Send to backend if BetterStack is configured
    this.sendToBackend(telemetryEvent);
  }

  /**
   * Track welcome page view
   */
  trackWelcomeView(): void {
    this.track("onboarding.welcome_view");
  }

  /**
   * Track account setup start
   */
  trackAccountSetupStart(): void {
    this.track("onboarding.account_setup_start");
  }

  /**
   * Track account setup completion
   */
  trackAccountSetupComplete(): void {
    this.track("onboarding.account_setup_complete");
  }

  /**
   * Track getting started view
   */
  trackGettingStartedView(): void {
    this.track("onboarding.getting_started_view");
  }

  /**
   * Track getting started completion
   */
  trackGettingStartedComplete(): void {
    this.track("onboarding.getting_started_complete");
  }

  /**
   * Track first action completion
   */
  trackFirstActionComplete(): void {
    this.track("onboarding.first_action_complete");
  }

  /**
   * Track onboarding abandonment
   */
  trackAbandonment(step: string): void {
    this.track("onboarding.abandonment", { step });
  }

  /**
   * Track error during onboarding
   */
  trackError(error: string, step: string): void {
    this.track("onboarding.error", { error, step });
  }

  /**
   * Get recent events for debugging
   */
  getRecentEvents(count: number = 10): OnboardingEvent[] {
    return this.events.slice(-count);
  }

  /**
   * Clear all events
   */
  clearEvents(): void {
    this.events = [];
  }

  /**
   * Send event to backend for BetterStack integration
   */
  private async sendToBackend(event: OnboardingEvent): Promise<void> {
    try {
      const response = await fetch("/api/v1/telemetry/onboarding", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(event),
      });

      if (!response.ok) {
        console.error(
          "Failed to send onboarding telemetry:",
          response.statusText,
        );
      }
    } catch (error) {
      // Silently fail to avoid disrupting user experience
      console.error("Error sending onboarding telemetry:", error);
    }
  }
}

export const onboardingTelemetry = OnboardingTelemetry.getInstance();
