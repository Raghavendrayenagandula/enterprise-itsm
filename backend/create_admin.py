
from getpass import getpass

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Role, User
from app.security import hash_password


def main():
    name = input("Administrator name: ").strip()
    email = input("Administrator email: ").strip().lower()
    password = getpass("Password (minimum 12 characters): ")

    if len(name) < 2:
        raise SystemExit("Name must contain at least 2 characters.")

    if len(password) < 12 or len(password) > 128:
        raise SystemExit("Password must be 12 to 128 characters.")

    with SessionLocal() as db:
        existing = db.scalar(
            select(User).where(User.email == email)
        )
        if existing:
            raise SystemExit("A user with this email already exists.")

        admin_role = db.scalar(
            select(Role).where(Role.name == "admin")
        )
        if not admin_role:
            raise SystemExit(
                "Admin role not found. Run database/schema.sql first."
            )

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role_id=admin_role.id,
            is_active=True,
        )
        db.add(user)
        db.commit()

    print("Administrator created successfully.")


if __name__ == "__main__":
    main()
