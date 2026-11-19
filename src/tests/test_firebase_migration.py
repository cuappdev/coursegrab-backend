import importlib.util
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
import sqlalchemy as sa


def test_migration_preserves_users_and_legacy_devices():
    engine = sa.create_engine("sqlite://")
    with engine.connect() as connection:
        connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR NOT NULL)")
        connection.execute("""CREATE TABLE sessions (
            id INTEGER PRIMARY KEY, user_id INTEGER, device_type VARCHAR,
            device_token VARCHAR, last_used DATETIME NOT NULL)""")
        connection.execute("INSERT INTO users VALUES (1, 'a@cornell.edu'), (2, 'b@cornell.edu')")
        connection.execute("""INSERT INTO sessions VALUES
            (1, 1, 'IOS', 'unique', '2026-01-01'),
            (2, 1, 'IOS', 'unique', '2026-02-01'),
            (3, 1, 'ANDROID', 'ambiguous', '2026-01-01'),
            (4, 2, 'ANDROID', 'ambiguous', '2026-02-01'),
            (5, 1, 'WEB', NULL, '2026-01-01')""")
        path = Path(__file__).parents[1] / "app/migrations/versions/f1a2b3c4d5e6_firebase_identity_and_devices.py"
        spec = importlib.util.spec_from_file_location("firebase_migration", path)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        with Operations.context(MigrationContext.configure(connection)):
            migration.upgrade()
            assert connection.execute("SELECT COUNT(*) FROM users").scalar() == 2
            assert connection.execute("SELECT COUNT(*) FROM sessions").scalar() == 5
            rows = connection.execute("SELECT user_id, device_type, device_token FROM device_registrations").fetchall()
            assert rows == []
            connection.execute("UPDATE users SET firebase_uid = 'uid' WHERE id = 1")
            with pytest.raises(sa.exc.IntegrityError):
                connection.execute("UPDATE users SET firebase_uid = 'uid' WHERE id = 2")
            migration.downgrade()
            assert connection.execute("SELECT COUNT(*) FROM users").scalar() == 2
            assert connection.execute("SELECT COUNT(*) FROM sessions").scalar() == 5
