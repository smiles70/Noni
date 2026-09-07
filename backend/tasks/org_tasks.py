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
from backend.models.organizations import Organization, OrgLicense
from backend.services import email
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
                # Deliver the notice (deferred-safe: email never blocks the
                # audit row; failure only means no email today).
                org = (
                    db.query(Organization)
                    .filter(Organization.id == lic.organization_id)
                    .one_or_none()
                )
                if org is not None and org.admin_email:
                    days = (lic.expires_at - now).days
                    text = (
                        f"A note from mynaani: the site license for {org.name} "
                        f"renews in about {days} days.\n\n"
                        "When you are ready, reply to this email or write to "
                        "help@mynaani.com and we will take care of it together.\n\n"
                        "— mynaani"
                    )
                    email.send(
                        org.admin_email,
                        "Your community license renewal is coming up",
                        text,
                    )
        db.commit()
        return {"expiring": len(expiring), "flagged": flagged}
    finally:
        db.close()


@app.task(name="backend.tasks.org_tasks.sharing_pattern_scan")
def sharing_pattern_scan() -> dict:
    """Weekly passive scan: flags accounts whose Progress signature looks
    like several hands on one login. Output is an audit row + a support
    flag ONLY — it never restricts or notifies the learner. Outreach is
    a warm human conversation offering a community license."""
    import uuid as _uuid

    from backend.models.governance import AccountFlag
    from backend.models.learning import Progress
    from backend.services.sharing_signals import detect_sharing

    db = SessionLocal()
    try:
        account_ids = [r[0] for r in db.query(Progress.account_id).distinct().all()]
        flagged = 0
        today = datetime.now(timezone.utc).date().isoformat()
        for aid in account_ids:
            rows = db.query(Progress).filter(Progress.account_id == aid).all()
            res = detect_sharing(rows)
            if not res["flag"]:
                continue
            # idempotent per day
            already = (
                db.query(AccountFlag)
                .filter(
                    AccountFlag.account_id == aid,
                    AccountFlag.flag == "sharing_signal",
                    AccountFlag.detail.like(f"%{today}%"),
                )
                .first()
            )
            if already is None:
                db.add(
                    AccountFlag(
                        id=_uuid.uuid4(),
                        account_id=aid,
                        flag="sharing_signal",
                        detail=f"date={today} reasons={','.join(res['reasons'])}",
                    )
                )
                flagged += 1
        db.commit()
        if flagged:
            email.send(
                "help@mynaani.com",
                f"{flagged} account(s) show a sharing pattern — gentle outreach list",
                "These accounts show usage patterns consistent with several "
                "people sharing one login. Please reach out warmly — offer the "
                "community license; do not mention monitoring or restrict access.",
            )
        return {"scanned": len(account_ids), "flagged": flagged}
    finally:
        db.close()
