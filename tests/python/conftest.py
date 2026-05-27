import os
import tempfile

# Force test DB path BEFORE any sysclean module is imported
# This prevents the disk I/O errors and protects the production database.
_test_db = os.path.join(tempfile.gettempdir(), "sysclean_pytest.db")
os.environ["SYSCLEAN_DB_PATH"] = _test_db
