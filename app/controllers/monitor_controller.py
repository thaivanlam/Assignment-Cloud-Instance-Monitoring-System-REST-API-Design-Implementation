from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import accessible_client_ids, get_current_member
from app.database import get_db
from app.models import Member
from app.schemas.schemas import InstanceOut, MonitorReport
from app.services import monitor_service

router = APIRouter(prefix="/api/monitor", tags=["Monitoring"])


@router.get(
    "/warnings",
    response_model=list[InstanceOut],
    summary="CPU >= 80% list + auto-record Alert (skips if unresolved alert exists)",
)
def warnings(db: Session = Depends(get_db), member: Member = Depends(get_current_member)):
    return monitor_service.check_warnings(db, accessible_client_ids(member, db))


@router.get(
    "/errors",
    response_model=list[InstanceOut],
    summary="ERROR status list + auto-record critical Alert",
)
def errors(db: Session = Depends(get_db), member: Member = Depends(get_current_member)):
    return monitor_service.check_errors(db, accessible_client_ids(member, db))


@router.get(
    "/long-stopped",
    response_model=list[InstanceOut],
    summary="Instances STOPPED for 48+ hours",
)
def long_stopped(db: Session = Depends(get_db), member: Member = Depends(get_current_member)):
    return monitor_service.check_long_stopped(db, accessible_client_ids(member, db))


@router.get(
    "/report",
    response_model=MonitorReport,
    summary="Full status report (count by status / warnings / total cost / unresolved alerts)",
)
def report(db: Session = Depends(get_db), member: Member = Depends(get_current_member)):
    return monitor_service.build_report(db, accessible_client_ids(member, db))
