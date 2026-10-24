
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    role: Literal["employee", "engineer", "manager", "admin"] = (
        "employee"
    )


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    role: str

    model_config = ConfigDict(from_attributes=True)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TicketCreate(BaseModel):
    title: str = Field(min_length=4, max_length=200)
    description: str = Field(min_length=5, max_length=10000)
    type: Literal["incident", "service_request"] = "incident"
    category: str = Field(default="General", max_length=80)
    priority: Literal["low", "medium", "high", "critical"] = "medium"


class TicketUpdate(BaseModel):
    status: Literal[
        "NEW", "TRIAGED", "ASSIGNED", "IN PROGRESS",
        "PENDING", "RESOLVED", "CLOSED"
    ] | None = None
    priority: Literal["low", "medium", "high", "critical"] | None = None


class TicketOut(BaseModel):
    id: int
    ticket_number: str | None
    title: str
    description: str
    type: str
    category: str
    priority: str
    status: str
    requester_id: int
    assignee_id: int | None
    created_at: datetime
