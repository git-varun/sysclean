import pathlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Path configured to ~/... sysclean.db
DB_PATH = pathlib.Path.home() / ".local/share/sysclean/sysclean.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# High concurrency SQLite: WAL mode and normal synchronous
# Note: In SQLAlchemy 2.0+ we can pass sqlite_pragma to execution_options or use events.
# We'll use connection events to execute PRAGMAs
from sqlalchemy import event

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False, "timeout": 15}
)

from queue_engine.models import Base
Base.metadata.create_all(bind=engine)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
