"""Seeds the database with demo data on first startup (idempotent)."""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.config import UNIT_PRICES
from app.core.security import hash_password
from app.models import (
    Client,
    ContractPlan,
    CostSnapshot,
    Instance,
    InstanceStatus,
    InstanceType,
    Member,
    Role,
)
from app.models.models import utcnow


def seed(db: Session) -> None:
    if db.query(Member).first() is not None:
        return  # already seeded

    now = utcnow()

    admin = Member(
        email="admin@techvalley.vn",
        password=hash_password("admin123!"),
        name="TechValley Admin",
        role=Role.ADMIN,
    )
    manager1 = Member(
        email="lam@techvalley.vn",
        password=hash_password("manager123!"),
        name="Thai Van Lam",
        role=Role.CLIENT_MANAGER,
    )
    manager2 = Member(
        email="minh@techvalley.vn",
        password=hash_password("manager123!"),
        name="Nguyen Minh",
        role=Role.CLIENT_MANAGER,
    )
    db.add_all([admin, manager1, manager2])
    db.flush()

    client_specs = [
        ("VinaSoft", ContractPlan.PREMIUM, manager1.id),
        ("Hanoi Logistics", ContractPlan.STANDARD, manager1.id),
        ("Saigon Retail", ContractPlan.BASIC, manager1.id),
        ("Mekong Foods", ContractPlan.STANDARD, manager1.id),
        ("DaNang Media", ContractPlan.BASIC, manager1.id),
        ("VN FinTech", ContractPlan.PREMIUM, manager2.id),
        ("EduViet", ContractPlan.STANDARD, manager2.id),
        ("GreenEnergy VN", ContractPlan.BASIC, manager2.id),
        ("HealthPlus", ContractPlan.PREMIUM, manager2.id),
        ("TravelGo", ContractPlan.STANDARD, manager2.id),
    ]
    clients = [Client(clientName=n, contractPlan=p, managerId=m) for n, p, m in client_specs]
    db.add_all(clients)
    db.flush()

    def inst(name, region, itype, status, cpu, client, launched_days, updated_hours):
        return Instance(
            instanceName=name,
            region=region,
            instanceType=itype,
            status=status,
            cpuUsage=cpu,
            monthlyCost=UNIT_PRICES[itype.value],
            clientId=client.id,
            launchedAt=now - timedelta(days=launched_days),
            updatedAt=now - timedelta(hours=updated_hours),
        )

    instances = [
        # VinaSoft (PREMIUM)
        inst("vinasoft-web-01", "ap-southeast-1", InstanceType.LARGE, InstanceStatus.RUNNING, 91.5, clients[0], 90, 1),
        inst("vinasoft-db-01", "ap-southeast-1", InstanceType.LARGE, InstanceStatus.RUNNING, 64.0, clients[0], 90, 2),
        inst("vinasoft-batch-01", "ap-northeast-2", InstanceType.MEDIUM, InstanceStatus.STOPPED, 0.0, clients[0], 60, 72),
        # Hanoi Logistics (STANDARD)
        inst("hnlog-api-01", "ap-southeast-1", InstanceType.MEDIUM, InstanceStatus.RUNNING, 85.2, clients[1], 45, 3),
        inst("hnlog-worker-01", "ap-southeast-1", InstanceType.SMALL, InstanceStatus.ERROR, 0.0, clients[1], 45, 6),
        # Saigon Retail (BASIC)
        inst("sgretail-pos-01", "ap-southeast-1", InstanceType.SMALL, InstanceStatus.RUNNING, 42.7, clients[2], 30, 1),
        inst("sgretail-report-01", "ap-southeast-1", InstanceType.SMALL, InstanceStatus.STOPPED, 0.0, clients[2], 30, 120),
        # Mekong Foods
        inst("mekong-erp-01", "ap-southeast-1", InstanceType.MEDIUM, InstanceStatus.RUNNING, 55.1, clients[3], 20, 2),
        # DaNang Media
        inst("dnmedia-stream-01", "ap-northeast-2", InstanceType.LARGE, InstanceStatus.ERROR, 0.0, clients[4], 15, 12),
        # VN FinTech (PREMIUM)
        inst("fintech-core-01", "ap-southeast-1", InstanceType.LARGE, InstanceStatus.RUNNING, 78.9, clients[5], 120, 1),
        inst("fintech-core-02", "ap-southeast-1", InstanceType.LARGE, InstanceStatus.RUNNING, 88.4, clients[5], 120, 1),
        # EduViet
        inst("eduviet-lms-01", "ap-southeast-1", InstanceType.MEDIUM, InstanceStatus.RUNNING, 33.0, clients[6], 25, 4),
        # GreenEnergy VN
        inst("green-iot-01", "ap-northeast-2", InstanceType.SMALL, InstanceStatus.STOPPED, 0.0, clients[7], 50, 96),
        # HealthPlus (PREMIUM)
        inst("health-api-01", "ap-southeast-1", InstanceType.MEDIUM, InstanceStatus.RUNNING, 96.3, clients[8], 70, 1),
        # TravelGo
        inst("travelgo-web-01", "ap-southeast-1", InstanceType.SMALL, InstanceStatus.RUNNING, 12.5, clients[9], 10, 1),
    ]
    db.add_all(instances)
    db.flush()

    # Previous-month cost snapshots for each client
    prev_month = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    for c in clients:
        c_instances = [i for i in instances if i.clientId == c.id]
        db.add(
            CostSnapshot(
                clientId=c.id,
                snapshotMonth=prev_month,
                totalCost=round(sum(i.monthlyCost for i in c_instances), 2),
                instanceCount=len(c_instances),
            )
        )

    db.commit()
