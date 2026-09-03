import os
import tempfile
import pytest
from app.db.database import init_db
from app.db.seed_data import seed_database

@pytest.fixture(scope="session", autouse=True)
def test_db_session():
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test_pahirowatch.db")
    os.environ["DATABASE_PATH"] = test_db_path
    
    init_db()
    seed_database()
    
    yield test_db_path
    
    # Cleanup
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass
