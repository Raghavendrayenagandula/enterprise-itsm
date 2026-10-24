
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ticket, User, Role, AuditLog
from app.schemas import TicketCreate, TicketUpdate
from app.security import get_current_user, require_roles

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

MANAGERS = ("manager", "admin")
ENGINEERS = ("engineer", "manager", "admin")


def role_name(db: Session, user: User) -> str:
    role = db.get(Role, user.role_id)
    return role.name if role else ""


def ticket_access(db: Session, ticket: Ticket, user: User):
    role = role_name(db, user)

    if role in ("manager", "admin"):
        return

    if role == "engineer" and ticket.assignee_id == user.id:
        return

    if ticket.requester_id == user.id:
        return

    raise HTTPException(status_code=403, detail="Access denied")


def log_action(
    db: Session, user_id: int, action: str, ticket_id: int
):
    db.add(
        AuditLog(
            actor_id=user_id,
            action=action,
            entity_type="ticket",
            entity_id=ticket_id,
            metadata_json={},
        )
    )


@router.post("")
def create_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ticket = Ticket(
        title=data.title,
        description=data.description,
        type=data.type,
        category=data.category,
        priority=data.priority,
        status="NEW",
        requester_id=user.id,
    )
    db.add(ticket)
    db.flush()

    ticket.ticket_number = f"INC-{ticket.id:06d}"
    log_action(db, user.id, "ticket.created", ticket.id)
    db.commit()
    db.refresh(ticket)

    return ticket


@router.get("")
def list_tickets(
    status: str | None = None,
    priority: str | None = None,
    q: str | None = Query(default=None, max_length=100),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    role = role_name(db, user)
    stmt = select(Ticket)

    if role == "employee":
        stmt = stmt.where(Ticket.requester_id == user.id)
    elif role == "engineer":
        stmt = stmt.where(Ticket.assignee_id == user.id)

    if status:
        stmt = stmt.where(Ticket.status == status)
    if priority:
        stmt = stmt.where(Ticket.priority == priority)
    if q:
        stmt = stmt.where(
            or_(
                Ticket.title.like(f"%{q}%"),
                Ticket.ticket_number.like(f"%{q}%"),
            )
        )

    stmt = stmt.order_by(Ticket.created_at.desc())
    return list(db.scalars(stmt.offset(skip).limit(limit)).all())


@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ticket = db.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket_access(db, ticket, user)
    return ticket


@router.patch("/{ticket_id}")
def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ticket = db.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket_access(db, ticket, user)
    role = role_name(db, user)

    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No changes supplied")

    if role == "employee":
        raise HTTPException(
            status_code=403,
            detail="Employees cannot modify ticket workflow fields",
        )

    if role == "engineer":
        if ticket.assignee_id != user.id:
            raise HTTPException(status_code=403, detail="Not assigned")
        if set(changes) - {"status"}:
            raise HTTPException(
                status_code=403,
                detail="Engineers can only update status here",
            )

    if "status" in changes and changes["status"] is not None:
        new_status = changes["status"]
        old_status = ticket.status

        allowed = {
            "NEW": {"TRIAGED", "ASSIGNED"},
            "TRIAGED": {"ASSIGNED", "IN PROGRESS"},
            "ASSIGNED": {"IN PROGRESS"},
            "IN PROGRESS": {"PENDING", "RESOLVED"},
            "PENDING": {"IN PROGRESS", "RESOLVED"},
            "RESOLVED": {"CLOSED", "IN PROGRESS"},
            "CLOSED": set(),
        }

        if new_status not in allowed.get(old_status, set()):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid transition: {old_status} -> {new_status}",
            )

        if new_status == "ASSIGNED" and not ticket.assignee_id:
            raise HTTPException(
                status_code=400,
                detail="Assign an engineer before setting ASSIGNED",
            )

        if new_status == "RESOLVED":
            ticket.resolved_at = datetime.now(timezone.utc).replace(
                tzinfo=None
            )

    for field, value in changes.items():
        if value is not None:
            setattr(ticket, field, value)

    log_action(db, user.id, "ticket.updated", ticket.id)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.post("/{ticket_id}/assign")
def assign_ticket(
    ticket_id: int,
    engineer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*MANAGERS)),
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    engineer = db.get(User, engineer_id)
    if not engineer or not engineer.is_active:
        raise HTTPException(status_code=404, detail="User not found")

    if role_name(db, engineer) != "engineer":
        raise HTTPException(
            status_code=400,
            detail="Assignee must have the engineer role",
        )

    if ticket.status in ("RESOLVED", "CLOSED"):
        raise HTTPException(
            status_code=400, detail="Cannot assign a closed ticket"
        )

    ticket.assignee_id = engineer.id
    if ticket.status in ("NEW", "TRIAGED"):
        ticket.status = "ASSIGNED"

    log_action(db, user.id, "ticket.assigned", ticket.id)
    db.commit()
    db.refresh(ticket)
    return ticket
