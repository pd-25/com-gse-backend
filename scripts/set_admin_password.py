import argparse
import getpass
import sys
from pathlib import Path

from pwdlib import PasswordHash


sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database.session import SESSIONLOCAL  # noqa: E402
from app.models.admin import Admin  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Set the password for an existing Global Source Expo administrator."
    )
    parser.add_argument("email", help="Existing administrator email address")
    args = parser.parse_args()
    password = getpass.getpass("New admin password: ")
    confirmation = getpass.getpass("Confirm new admin password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match")
    if len(password) < 8:
        raise SystemExit("Password must contain at least 8 characters")

    with SESSIONLOCAL() as db:
        admin = db.query(Admin).filter(Admin.email == args.email.strip().lower()).first()
        if admin is None:
            raise SystemExit("Administrator not found")
        admin.password = PasswordHash.recommended().hash(password)
        admin.deleted_at = None
        db.commit()
    print("Administrator password updated successfully")


if __name__ == "__main__":
    main()
