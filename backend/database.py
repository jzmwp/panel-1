from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import settings

connect_args = {}
if not settings.is_postgres:
    connect_args["check_same_thread"] = False
else:
    # Disable prepared statements for Supabase transaction pooler (pgbouncer)
    connect_args["options"] = "-c statement_timeout=30000"

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,
    pool_size=5 if settings.is_postgres else 0,
    max_overflow=10 if settings.is_postgres else 0,
)


# Enable WAL mode and foreign keys for SQLite only
if not settings.is_postgres:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
