import getpass
import re
import sys
from pathlib import Path

from pwdlib import PasswordHash


sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database.session import SESSIONLOCAL  # noqa: E402
from app.models.admin import Admin  # noqa: E402


def main() -> None:
    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass.getpass("Admin password: ")
    confirmation = getpass.getpass("Confirm admin password: ")
    if len(name) < 2:
        raise SystemExit("Admin name must contain at least 2 characters")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise SystemExit("Enter a valid email address")
    if password != confirmation:
        raise SystemExit("Passwords do not match")
    if len(password) < 8:
        raise SystemExit("Password must contain at least 8 characters")

    with SESSIONLOCAL() as db:
        if db.query(Admin.id).filter(Admin.email == email).first():
            raise SystemExit("An administrator with this email already exists")
        db.add(
            Admin(
                name=name,
                email=email,
                password=PasswordHash.recommended().hash(password),
                is_subadmin=False,
            )
        )
        db.commit()
    print("Super administrator created successfully")


if __name__ == "__main__":
    main()
