"""Organization maintenance tasks (OB-3).

license_renewal_reminders: daily scan of org_licenses — writes an
org_audit_log entry for licenses expiring within 30 days so staff have
a durable, queryable renewal queue. Notification delivery is a follow-up;
the audit row is the system of record for now.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from backend.core.database import SessionLocal
from backend.models.governance import OrgAuditLog
from backend.models.organizations import OrgLicense
from backend.tasks.celery_app import app

log = logging.getLogger(__name__)


@app.task(name="backend.tasks.org_tasks.license_renewal_reminders")
def license_renewal_reminders() -> dict:
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        horizon = now + timedelta(days=30)
        expiring = (
            db.query(OrgLicense)
            .filter(
                OrgLicense.expires_at.isnot(None),
                OrgLicense.expires_at > now,
                OrgLicense.expires_at <= horizon,
            )
            .all()
        )
        flagged = 0
        for lic in expiring:
            # Idempotent per day: skip if a reminder row already exists today.
            today = now.date().isoformat()
            already = (
                db.query(OrgAuditLog)
                .filter(
                    OrgAuditLog.organization_id == lic.organization_id,
                    OrgAuditLog.action == "license.expiring_soon",
                    OrgAuditLog.detail.like(f"%{today}%"),
                )
                .first()
            )
            if already is None:
                db.add(
                    OrgAuditLog(
                        id=uuid.uuid4(),
                        organization_id=lic.organization_id,
                        actor_account_id=None,
                        action="license.expiring_soon",
                        detail=(
                            f"license={lic.id} expires={lic.expires_at.date().isoformat()} "
                            f"reminder_date={today}"
                        ),
                    )
                )
                flagged += 1
        db.commit()
        return {"expiring": len(expiring), "flagged": flagged}
    finally:
        db.close()
