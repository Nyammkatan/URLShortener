import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from utils import generate_code

from url_repository import URLRepository
from models import ShortenedURL
from datetime import datetime

def test_generate_code_format():
    code = generate_code()
    assert isinstance(code, str)
    assert len(code) == 5
    assert code.isalnum()


def test_save_and_get_url():
    test_db_path = "test.db"
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)    
    repo = URLRepository(db_path=test_db_path)
    url = ShortenedURL(code="abc123", original_url="https://test.com", created_at=datetime.now())
    repo.save(url)
    fetched = repo.get("abc123")

    assert fetched is not None
    assert fetched.original_url == url.original_url

    os.remove(test_db_path)