import json

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def log_action(db: Session, action: str, entity_type: str, entity_id: int | None, details: dict | str | None = None):
    if isinstance(details, dict):
        details_value = json.dumps(details, ensure_ascii=False)
    else:
        details_value = details

    audit_log = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details_value,
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log
