import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database.seeder.admin_seeder import AdminSeeder  # noqa: E402
from app.database.session import SESSIONLOCAL  # noqa: E402


def main() -> None:
    with SESSIONLOCAL() as db:
        AdminSeeder().run(db)


if __name__ == "__main__":
    main()
