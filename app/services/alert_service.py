from datetime import date, datetime, time

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models import Alert, AlertType, Instance
from app.models.models import utcnow


def list_alerts(
    db: Session,
    client_ids: list[int] | None,
    alertType: AlertType | None = None,
    isResolved: bool | None = None,
    dateFrom: date | None = None,
    dateTo: date | None = None,
) -> list[Alert]:
    query = db.query(Alert).join(Instance, Alert.instanceId == Instance.id)
    if client_ids is not None:
        query = query.filter(Instance.clientId.in_(client_ids or [-1]))
    if alertType is not None:
        query = query.filter(Alert.alertType == alertType)
    if isResolved is not None:
        query = query.filter(Alert.isResolved.is_(isResolved))
    if dateFrom is not None:
        query = query.filter(Alert.detectedAt >= datetime.combine(dateFrom, time.min))
    if dateTo is not None:
        query = query.filter(Alert.detectedAt <= datetime.combine(dateTo, time.max))
    return query.order_by(Alert.detectedAt.desc()).all()


def resolve_alert(db: Session, alert_id: int) -> Alert:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise NotFoundException("Alert", alert_id)
    if not alert.isResolved:
        alert.isResolved = True
        alert.resolvedAt = utcnow()
        db.commit()
        db.refresh(alert)
    return alert
