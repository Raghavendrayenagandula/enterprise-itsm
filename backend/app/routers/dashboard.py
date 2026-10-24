
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ticket, User, Role
from app.security import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("")
def dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    role = db.get(Role, user.role_id)
    query = select(Ticket)

    if role and role.name == "employee":
        query = query.where(Ticket.requester_id == user.id)
    elif role and role.name == "engineer":
        query = query.where(Ticket.assignee_id == user.id)

    scoped_tickets = query.subquery()

    total = db.scalar(
        select(func.count()).select_from(scoped_tickets)
    ) or 0

    open_count = db.scalar(
        select(func.count()).select_from(scoped_tickets).where(
            scoped_tickets.c.status.notin_(["RESOLVED", "CLOSED"])
        )
    ) or 0

    critical_count = db.scalar(
        select(func.count()).select_from(scoped_tickets).where(
            scoped_tickets.c.priority == "critical",
            scoped_tickets.c.status.notin_(["RESOLVED", "CLOSED"]),
        )
    ) or 0

    status_rows = db.execute(
        select(scoped_tickets.c.status, func.count())
        .group_by(scoped_tickets.c.status)
    ).all()

    return {
        "total_tickets": total,
        "open_tickets": open_count,
        "critical_tickets": critical_count,
        "tickets_by_status": {
            status: count for status, count in status_rows
        },
    }
