from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import AlertType, ContractPlan, InstanceStatus, InstanceType, Role

T = TypeVar("T")


# ---------- Auth ----------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    role: Role
    name: str


# ---------- Members ----------
class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    role: Role
    createdAt: datetime


# ---------- Clients ----------
class ClientCreate(BaseModel):
    clientName: str = Field(min_length=1, max_length=100)
    contractPlan: ContractPlan
    managerId: int


class ClientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clientName: str
    contractPlan: ContractPlan
    managerId: int
    createdAt: datetime


# ---------- Instances ----------
class InstanceCreate(BaseModel):
    instanceName: str = Field(min_length=1, max_length=100)
    region: str = Field(min_length=1, max_length=50)
    instanceType: InstanceType
    status: InstanceStatus = InstanceStatus.RUNNING
    cpuUsage: float = Field(default=0.0, ge=0.0, le=100.0)
    clientId: int


class InstanceStatusUpdate(BaseModel):
    status: InstanceStatus
    cpuUsage: float | None = Field(default=None, ge=0.0, le=100.0)


class InstanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    instanceName: str
    region: str
    instanceType: InstanceType
    status: InstanceStatus
    cpuUsage: float
    monthlyCost: float
    clientId: int
    launchedAt: datetime
    updatedAt: datetime


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    totalPages: int


# ---------- Alerts ----------
class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    instanceId: int
    alertType: AlertType
    message: str
    isResolved: bool
    detectedAt: datetime
    resolvedAt: datetime | None


# ---------- Monitoring ----------
class MonitorReport(BaseModel):
    generatedAt: datetime
    instanceCountByStatus: dict[str, int]
    warningCount: int
    totalMonthlyCost: float
    unresolvedAlertCount: int
    unresolvedAlerts: list[AlertOut]


# ---------- Cost / SLA ----------
class ClientCostResponse(BaseModel):
    clientId: int
    clientName: str
    month: str
    instanceCount: int
    totalMonthlyCost: float
    costByInstance: list[dict]


class CostForecastResponse(BaseModel):
    clientId: int
    clientName: str
    forecastMonth: str
    runningInstanceCount: int
    forecastCost: float
    breakdown: dict[str, dict]


class SlaResponse(BaseModel):
    clientId: int
    clientName: str
    contractPlan: ContractPlan
    slaThreshold: float
    month: str
    uptimePercent: float
    isViolation: bool
    instanceDetails: list[dict]


# ---------- LLM ----------
class DiagnosisResponse(BaseModel):
    instanceId: int
    instanceName: str
    status: InstanceStatus
    diagnosis: str
    source: str  # "llm" or "rule-based"
